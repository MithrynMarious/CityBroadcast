# Hard Benchmark Answer Key — 15 Vulnerabilities

## Category A: Obvious (should catch all)
1. **Hardcoded secret key** (line 18): `app.secret_key = "production-secret-key-2024"` — session cookies are forgeable
2. **SHA-256 without salt for passwords** (line 54): `hashlib.sha256(password.encode())` — rainbow table vulnerable, should use bcrypt/argon2
3. **Debug mode in production** (last line): `app.run(debug=True)` — exposes interactive debugger, stack traces, allows RCE

## Category B: Moderate (requires reading data flow)
4. **IDOR on get_order** (line 122): Any authenticated user can view ANY order by ID — no ownership check (`order.user_id == g.user.id`)
5. **IDOR on cancel_order** (line 129): Any authenticated user can cancel ANY order — no ownership check
6. **Admin endpoint leaks all API keys** (line 145): `admin_list_users` returns `api_key` for every user — admin can impersonate anyone
7. **Discount code injection** (line 113): `_lookup_discount` parses percentage from the code string itself — `FAKE-100` gives 100% discount, `FAKE-200` gives negative total (they pay YOU)
8. **Race condition on stock** (line 116-119): Read stock → check → decrement is not atomic. Two concurrent orders can both pass the stock check and oversell

## Category C: Subtle (requires security expertise)
9. **Timing-safe comparison not used for webhook** (line 165): `signature == expected` is vulnerable to timing attacks — should use `hmac.compare_digest()`
10. **Default webhook secret** (line 160): `WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "whsec_default_secret")` — falls back to known value if env var not set
11. **API key in response on registration** (line 92): Returns API key in cleartext HTTP response — interceptable on non-HTTPS
12. **Thread safety in background task** (line 182-189): `cleanup_stale_orders` modifies DB without application context or proper session management — race condition with request handlers
13. **Mass assignment on admin_update_product** (line 155-159): Accepts ANY field from request JSON including potentially `id` — no field whitelist
14. **Unbounded pagination** (line 100): `per_page` has no maximum — attacker can request `per_page=1000000` to DoS
15. **No rate limiting on login** (line 95): Brute force attack vector — no lockout, no delay, no CAPTCHA

## Scoring Tiers
- Finding 1-3 (obvious): Expected from any reviewer
- Finding 4-8 (moderate): Expected from a good reviewer
- Finding 9-12 (subtle): Distinguishes expert from competent
- Finding 13-15 (edge): Bonus — demonstrates thoroughness
