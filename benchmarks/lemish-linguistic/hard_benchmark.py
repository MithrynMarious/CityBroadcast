"""
E-commerce order processing API.
Handles user orders, inventory, payments, and admin operations.
"""
import hashlib
import hmac
import json
import os
import time
import threading
from functools import wraps
from flask import Flask, request, jsonify, session, g
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "production-secret-key-2024"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "postgresql://orders:orders@localhost/shop")
db = SQLAlchemy(app)


# ── Models ──

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(64))  # SHA-256
    role = db.Column(db.String(20), default="customer")
    api_key = db.Column(db.String(64))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    price = db.Column(db.Float)
    stock = db.Column(db.Integer)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))
    quantity = db.Column(db.Integer)
    total = db.Column(db.Float)
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.Float, default=time.time)


# ── Auth ──

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        if api_key:
            user = User.query.filter_by(api_key=api_key).first()
            if user:
                g.user = user
                return f(*args, **kwargs)
        if "user_id" in session:
            user = User.query.get(session["user_id"])
            if user:
                g.user = user
                return f(*args, **kwargs)
        return jsonify({"error": "unauthorized"}), 401
    return decorated

def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if g.user.role != "admin":
            return jsonify({"error": "forbidden"}), 403
        return f(*args, **kwargs)
    return decorated


# ── Auth Endpoints ──

@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "email taken"}), 409
    user = User(
        email=data["email"],
        password_hash=hash_password(data["password"]),
        api_key=hashlib.sha256(os.urandom(32)).hexdigest()
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"id": user.id, "api_key": user.api_key})

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(
        email=data["email"],
        password_hash=hash_password(data["password"])
    ).first()
    if not user:
        return jsonify({"error": "invalid credentials"}), 401
    session["user_id"] = user.id
    return jsonify({"status": "ok", "role": user.role})


# ── Product Endpoints ──

@app.route("/api/products")
def list_products():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    products = Product.query.paginate(page=page, per_page=per_page)
    return jsonify([{"id": p.id, "name": p.name, "price": p.price, "stock": p.stock}
                    for p in products.items])

@app.route("/api/products/<int:product_id>")
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({"id": product.id, "name": product.name, "price": product.price, "stock": product.stock})


# ── Order Endpoints ──

@app.route("/api/orders", methods=["POST"])
@require_auth
def create_order():
    data = request.json
    product = Product.query.get(data["product_id"])
    if not product:
        return jsonify({"error": "product not found"}), 404

    quantity = data.get("quantity", 1)
    total = product.price * quantity

    # Apply discount code if provided
    discount_code = data.get("discount_code")
    if discount_code:
        discount = _lookup_discount(discount_code)
        if discount:
            total = total * (1 - discount["percentage"] / 100)

    if product.stock < quantity:
        return jsonify({"error": "insufficient stock"}), 400

    product.stock -= quantity
    order = Order(user_id=g.user.id, product_id=product.id, quantity=quantity, total=total)
    db.session.add(order)
    db.session.commit()
    return jsonify({"order_id": order.id, "total": total}), 201

@app.route("/api/orders/<int:order_id>")
@require_auth
def get_order(order_id):
    order = Order.query.get_or_404(order_id)
    return jsonify({
        "id": order.id, "product_id": order.product_id,
        "quantity": order.quantity, "total": order.total,
        "status": order.status
    })

@app.route("/api/orders/<int:order_id>/cancel", methods=["POST"])
@require_auth
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.status != "pending":
        return jsonify({"error": "cannot cancel"}), 400
    order.status = "cancelled"
    product = Product.query.get(order.product_id)
    product.stock += order.quantity
    db.session.commit()
    return jsonify({"status": "cancelled"})

@app.route("/api/my-orders")
@require_auth
def my_orders():
    orders = Order.query.filter_by(user_id=g.user.id).all()
    return jsonify([{"id": o.id, "total": o.total, "status": o.status} for o in orders])


# ── Admin Endpoints ──

@app.route("/api/admin/users")
@require_auth
@require_admin
def admin_list_users():
    users = User.query.all()
    return jsonify([{"id": u.id, "email": u.email, "role": u.role, "api_key": u.api_key} for u in users])

@app.route("/api/admin/orders")
@require_auth
@require_admin
def admin_list_orders():
    status = request.args.get("status")
    query = Order.query
    if status:
        query = query.filter_by(status=status)
    return jsonify([{"id": o.id, "user_id": o.user_id, "total": o.total, "status": o.status}
                    for o in query.all()])

@app.route("/api/admin/product", methods=["PUT"])
@require_auth
@require_admin
def admin_update_product():
    data = request.json
    product = Product.query.get(data["id"])
    if "price" in data:
        product.price = data["price"]
    if "stock" in data:
        product.stock = data["stock"]
    if "name" in data:
        product.name = data["name"]
    db.session.commit()
    return jsonify({"updated": True})


# ── Webhook ──

WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "whsec_default_secret")

@app.route("/api/webhook/payment", methods=["POST"])
def payment_webhook():
    payload = request.get_data()
    signature = request.headers.get("X-Signature")
    expected = hmac.new(WEBHOOK_SECRET.encode(), payload, hashlib.sha256).hexdigest()
    if not signature == expected:
        return jsonify({"error": "invalid signature"}), 403

    event = json.loads(payload)
    if event["type"] == "payment.completed":
        order = Order.query.get(event["order_id"])
        order.status = "paid"
        db.session.commit()
    return jsonify({"received": True})


# ── Helpers ──

_discount_cache = {}

def _lookup_discount(code):
    if code in _discount_cache:
        return _discount_cache[code]
    # Simulate external API call
    result = {"code": code, "percentage": int(code.split("-")[-1]) if "-" in code else 10}
    _discount_cache[code] = result
    return result


# ── Background Tasks ──

def cleanup_stale_orders():
    """Cancel orders older than 24 hours that are still pending."""
    while True:
        cutoff = time.time() - 86400
        stale = Order.query.filter(Order.status == "pending", Order.created_at < cutoff).all()
        for order in stale:
            order.status = "expired"
            product = Product.query.get(order.product_id)
            product.stock += order.quantity
        db.session.commit()
        time.sleep(3600)

threading.Thread(target=cleanup_stale_orders, daemon=True).start()


if __name__ == "__main__":
    app.run(debug=True)
