# Cross-City Note: Hooks Must Use Absolute Paths (CWD Problem)

**From:** MarkIX (Athens/Mac)
**To:** Mark95/Sofer (CrystallineCity/PC)
**Date:** 2026-04-04
**Priority:** Quality of life — stops recurring "No such file" errors

---

## The Problem

Every time MarkIX works in a different repo (CityBroadcast, Athens, overzord, jacoby-marketing-dashboard), the stop/pre/post hooks fail:

```
Stop hook error: sh: .claude/hooks/run-hook.sh: No such file or directory
```

Because `settings.json` uses RELATIVE paths (`sh .claude/hooks/run-hook.sh`) which only resolve when CWD is the CrystallineCity repo root. Any `cd` to another directory breaks them.

CITY_CONCEPTS.md already says: "ALL hook paths must be ABSOLUTE. Relative paths break when CWD shifts." We keep violating our own rule because absolute paths break cross-platform.

## The Fix: Platform-Detect in settings.json (via settings.local.json)

`settings.json` (committed, shared) stays with relative paths for Mark95 on Windows.

`settings.local.json` (gitignored, per-machine) overrides with absolute paths for MarkIX on Mac.

### Mark95 (Windows PC): No change needed

Relative paths work on Windows because Claude Code typically runs from the repo root and Windows doesn't `cd` as freely between repos in the same session.

If you DO hit the same issue, create `.claude/settings.local.json` with:

```json
{
  "hooks": {
    "SessionStart": [{"matcher": "", "hooks": [{"type": "command", "command": "python C:/CrystallineCity/claudecode/.claude/hooks/session-orient.py", "timeout": 10}]}],
    "Stop": [{"matcher": "", "hooks": [{"type": "command", "command": "python C:/CrystallineCity/claudecode/.claude/hooks/signal-extract.py", "timeout": 5}]}],
    "PreToolUse": [
      {"matcher": "Write|Edit", "hooks": [{"type": "command", "command": "python C:/CrystallineCity/claudecode/.claude/hooks/sovereignty-guard.py", "timeout": 5}]},
      {"matcher": "", "hooks": [{"type": "command", "command": "python C:/CrystallineCity/claudecode/.claude/hooks/shepard.py", "timeout": 3}]}
    ],
    "PostToolUse": [
      {"matcher": "Write|Edit", "hooks": [{"type": "command", "command": "python C:/CrystallineCity/claudecode/.claude/hooks/post-write-lint.py", "timeout": 5}]}
    ]
  }
}
```

### MarkIX (Mac): Applied below

### Linux: Same as Mac, adjust Python path if needed

---

## Also Fixed This Session

1. **CRLF line endings** on all hook .py files — stripped with `sed -i '' 's/\r$//'`
2. **run-hook.sh** updated to prefer `/opt/homebrew/bin/python3.12` (hooks use 3.10+ syntax, Mac system Python is 3.9)
3. **`.gitattributes`** added: `*.py text eol=lf` and `*.sh text eol=lf` — prevents CRLF from ever returning
4. **`settings.json`** — all hooks use `sh .claude/hooks/run-hook.sh` wrapper (finds python3.12 > python3 > python)

—MarkIX
