#!/usr/bin/env python3
"""
Lemish Linguistic Benchmark Runner

Runs all prompt conditions against a benchmark code file, scores results,
and produces a comparison table.

Usage:
    python run_benchmark.py --target easy --endpoint http://localhost:1234 --api-key KEY
    python run_benchmark.py --target hard --endpoint http://localhost:1234 --api-key KEY
    python run_benchmark.py --target hard --use-agents  # Uses Claude Code Agent tool
    python run_benchmark.py --target hard --mode molecule --constructs Ward,Tally,Heed,Balm
"""

import argparse
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROMPTS = json.loads((SCRIPT_DIR / "prompts.json").read_text())
RESULTS_DIR = SCRIPT_DIR / "results"


def call_lm_studio(endpoint, api_key, system, prompt, max_tokens=2000):
    """Call LM Studio or any Anthropic-compatible endpoint."""
    url = f"{endpoint.rstrip('/')}/v1/messages"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }
    body = {
        "model": "auto",
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        body["system"] = system

    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers)
    resp = urllib.request.urlopen(req, timeout=300)
    result = json.loads(resp.read())
    return {
        "text": result["content"][0]["text"],
        "input_tokens": result.get("usage", {}).get("input_tokens", 0),
        "output_tokens": result.get("usage", {}).get("output_tokens", 0),
    }


def score_output(text, answer_key_path):
    """Score output against an answer key file."""
    key = json.loads(answer_key_path.read_text()) if answer_key_path.suffix == ".json" else None

    # If markdown answer key, parse it for keywords
    if answer_key_path.suffix == ".md":
        return score_by_keywords(text, answer_key_path)

    return {"found": 0, "total": 0, "missed": []}


def score_by_keywords(text, key_path):
    """Score by scanning for vulnerability keywords in output text."""
    t = text.lower()

    # Hard benchmark keywords
    vulns = {
        "A1: Hardcoded secret key": ["hardcod", "secret_key", "secret key", "production-secret"],
        "A2: SHA-256 unsalted passwords": ["sha-256", "sha256", "salt", "bcrypt", "argon", "rainbow"],
        "A3: Debug mode": ["debug=true", "debug mode", "debugger"],
        "B4: IDOR get_order": ["idor"],
        "B5: IDOR cancel_order": [],  # Needs "cancel" + auth context
        "B6: Admin leaks API keys": ["api_key", "impersonat"],
        "B7: Discount code injection": ["discount", "percentage", "100%", "negative"],
        "B8: Race condition stock": ["race", "concurrent", "atomic", "toctou"],
        "C9: Timing attack webhook": ["timing", "compare_digest", "constant-time", "time-safe"],
        "C10: Default webhook secret": ["whsec_default", "default"],
        "C11: API key in response": [],
        "C12: Thread safety background": ["thread", "context"],
        "C13: Mass assignment admin": ["mass assign", "whitelist"],
        "C14: Unbounded pagination": ["per_page", "pagination", "unbounded"],
        "C15: No rate limiting login": ["rate limit", "brute force", "lockout"],
    }

    found = []
    for vuln, keywords in vulns.items():
        for kw in keywords:
            if kw in t:
                found.append(vuln)
                break

    # Special cases needing context
    if "cancel" in t and ("auth" in t or "own" in t or "idor" in t):
        if "B5: IDOR cancel_order" not in found:
            found.append("B5: IDOR cancel_order")
    if "api_key" in t and ("response" in t or "cleartext" in t or "intercept" in t):
        if "C11: API key in response" not in found:
            found.append("C11: API key in response")

    all_vulns = list(vulns.keys())
    missed = [v for v in all_vulns if v not in found]

    # Count hedges
    hedge_words = PROMPTS.get("hedge_words", ["might", "could", "potentially", "perhaps", "may ", "consider"])
    hedge_count = sum(t.count(h) for h in hedge_words)

    # Count bonus findings (beyond planted)
    bonus_keywords = ["negative quantity", "float", "salami", "no logout", "session invalidat",
                      "no email valid", "cache poison", "cache dos", "memory exhaust",
                      "no registration rate", "null product", "api key rotat"]
    bonus = [kw for kw in bonus_keywords if kw in t]

    return {
        "found": found,
        "missed": missed,
        "score": len(found),
        "total": len(all_vulns),
        "hedge_count": hedge_count,
        "bonus": bonus,
    }


def run_conditions(target, endpoint, api_key, conditions=None):
    """Run all or specified conditions against a benchmark."""
    benchmark_file = SCRIPT_DIR / f"{target}_benchmark.py"
    if not benchmark_file.exists():
        print(f"ERROR: {benchmark_file} not found")
        sys.exit(1)

    code = benchmark_file.read_text()
    answer_key = SCRIPT_DIR / f"{target}_benchmark_answer_key.md"

    RESULTS_DIR.mkdir(exist_ok=True)

    all_conditions = conditions or list(PROMPTS["conditions"].keys())
    results = {}

    for cond_name in all_conditions:
        cond = PROMPTS["conditions"].get(cond_name)
        if not cond:
            print(f"Unknown condition: {cond_name}")
            continue

        prompt = cond["prompt_template"].replace("{CODE}", code)
        system = cond.get("system", "")

        print(f"\nRunning: {cond_name} ({cond['principle']})")
        start = time.time()

        try:
            result = call_lm_studio(endpoint, api_key, system, prompt)
            elapsed = time.time() - start

            # Score
            if answer_key.exists():
                scores = score_by_keywords(result["text"], answer_key)
            else:
                scores = {"score": "?", "total": "?", "hedge_count": 0, "found": [], "missed": [], "bonus": []}

            results[cond_name] = {
                "text": result["text"],
                "elapsed": elapsed,
                "tokens_in": result["input_tokens"],
                "tokens_out": result["output_tokens"],
                **scores,
            }

            # Save individual result
            out_path = RESULTS_DIR / f"{target}_{cond_name}.txt"
            out_path.write_text(result["text"])

            s = scores.get("score", "?")
            t = scores.get("total", "?")
            h = scores.get("hedge_count", 0)
            b = len(scores.get("bonus", []))
            print(f"  {s}/{t} vulns | {h} hedges | {b} bonus | {elapsed:.1f}s")

        except Exception as e:
            print(f"  ERROR: {e}")
            results[cond_name] = {"error": str(e)}

    # Summary table
    print("\n" + "=" * 70)
    print(f"SUMMARY — {target} benchmark")
    print("=" * 70)

    control_score = results.get("control", {}).get("score", 0)
    for name, r in sorted(results.items(), key=lambda x: -x[1].get("score", 0)):
        if "error" in r:
            print(f"  {name:20s} | ERROR")
            continue
        delta = r["score"] - control_score
        sign = "+" if delta > 0 else ""
        bonus = len(r.get("bonus", []))
        print(f"  {name:20s} | {r['score']:2d}/{r['total']} ({sign}{delta}) | hedges: {r['hedge_count']:2d} | bonus: {bonus} | {r['elapsed']:5.1f}s")

    # Save all results
    results_path = RESULTS_DIR / f"{target}_all_results.json"
    serializable = {k: {kk: vv for kk, vv in v.items() if kk != "text"} for k, v in results.items()}
    results_path.write_text(json.dumps(serializable, indent=2, default=str))
    print(f"\nResults saved to: {results_path}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Lemish Linguistic Benchmark Runner")
    parser.add_argument("--target", choices=["easy", "hard"], required=True, help="Which benchmark to run")
    parser.add_argument("--endpoint", default="http://localhost:1234", help="LM Studio endpoint URL")
    parser.add_argument("--api-key", default="lmstudio", help="API key for the endpoint")
    parser.add_argument("--conditions", nargs="*", help="Specific conditions to run (default: all)")
    parser.add_argument("--use-agents", action="store_true", help="Use Claude Code Agent tool instead of direct API")
    parser.add_argument("--mode", choices=["single", "molecule", "tinybrain"], default="single", help="Execution mode")
    parser.add_argument("--constructs", help="Comma-separated construct names for molecule/tinybrain mode")
    args = parser.parse_args()

    if args.use_agents:
        print("Agent mode not yet implemented — use direct API with --endpoint")
        sys.exit(1)

    if args.mode in ("molecule", "tinybrain"):
        print(f"{args.mode} mode not yet implemented — generates dispatch files (TODO)")
        sys.exit(1)

    run_conditions(args.target, args.endpoint, args.api_key, args.conditions)


if __name__ == "__main__":
    main()
