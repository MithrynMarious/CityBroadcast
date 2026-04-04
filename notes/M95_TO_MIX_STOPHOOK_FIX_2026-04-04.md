# Cross-City Note: Stop Hook Fix for MarkIX
**From:** Mark95 (Windows/PC)
**To:** MarkIX (MacBook Pro)
**Date:** 2026-04-04
**Priority:** Bug fix — stops the recurring error on every session exit

---

## The Error

```
Stop hook error: Failed with non-blocking status code: /usr/bin/sh: /usr/bin/sh: cannot execute binary file
```

## Root Cause: TWO bugs stacked

### Bug 1: CRLF line endings on all hook .py files

Every `.py` file in `.claude/hooks/` has **Windows CRLF line endings** (`\r\n`). On Mac, when the shell tries to execute these:

- The shebang `#!/usr/bin/env python3\r` tells the kernel to find `/usr/bin/env python3\r` (note the invisible `\r`)
- That binary doesn't exist → kernel falls back to `/usr/bin/sh`
- `sh` tries to parse the Python file as shell script → fails with the `/usr/bin/sh: /usr/bin/sh: cannot execute binary file` error

**Confirmed:** `file .claude/hooks/signal-extract.py` → "with CRLF line terminators"

### Bug 2: `python` doesn't exist on macOS 12.3+

The settings.json Stop hook command is:
```json
"command": "python .claude/hooks/signal-extract.py"
```

macOS removed the `python` command in 12.3 (Monterey). Only `python3` exists. Even if CRLF were fixed, this command would fail with `python: command not found`.

---

## The Fix

### Step 1: Convert ALL hook files to Unix line endings

Run this from the claudecode project root on Mac:

```bash
cd .claude/hooks/
for f in *.py *.sh; do
  sed -i '' 's/\r$//' "$f"
done
```

Or if `dos2unix` is installed:
```bash
dos2unix .claude/hooks/*.py .claude/hooks/*.sh
```

### Step 2: Fix the settings.json hook command

In `.claude/settings.json` (project-level, inside claudecode), change the Stop hook from:

```json
"command": "python .claude/hooks/signal-extract.py"
```

To:

```json
"command": "python3 .claude/hooks/signal-extract.py 2>/dev/null || python .claude/hooks/signal-extract.py 2>/dev/null || true"
```

This tries `python3` first (Mac), falls back to `python` (Windows), and the `|| true` ensures the hook never blocks even if both fail.

**Same fix needed for ALL hook commands in settings.json** — SessionStart, PreToolUse, PostToolUse all use `python` and will have the same issue on Mac.

### Step 3: Fix ALL hook commands (full replacement block)

Here's the complete cross-platform settings.json hook commands. Replace `python` with the fallback pattern everywhere:

```
SessionStart:  python3 .claude/hooks/session-orient.py 2>/dev/null || python .claude/hooks/session-orient.py
Stop:          python3 .claude/hooks/signal-extract.py 2>/dev/null || python .claude/hooks/signal-extract.py || true
PreToolUse:    python3 .claude/hooks/sovereignty-guard.py 2>/dev/null || python .claude/hooks/sovereignty-guard.py
PreToolUse:    python3 .claude/hooks/shepard.py 2>/dev/null || python .claude/hooks/shepard.py
PreToolUse:    python3 .claude/hooks/loop_guard.py 2>/dev/null || python .claude/hooks/loop_guard.py
PostToolUse:   python3 .claude/hooks/post-write-lint.py 2>/dev/null || python .claude/hooks/post-write-lint.py
PostToolUse:   python3 .claude/hooks/time-awareness.py 2>/dev/null || python .claude/hooks/time-awareness.py
```

### Alternative: One-line wrapper approach

If you'd rather not edit every command, create this wrapper script:

**`.claude/hooks/py.sh`:**
```bash
#!/bin/sh
exec "$(command -v python3 2>/dev/null || command -v python)" "$@"
```

Then change all hook commands to: `sh .claude/hooks/py.sh .claude/hooks/<script>.py`

**Make sure `py.sh` has LF line endings** (not CRLF) or you'll hit the same shebang bug.

---

## Verification

After applying the fix, MarkIX should see:
1. No more "cannot execute binary file" errors on session exit
2. Signal extraction runs cleanly (or silently skips if not in claudecode project)
3. All other hooks (Shepard, sovereignty-guard, etc.) work on Mac

Test with:
```bash
python3 .claude/hooks/signal-extract.py < /dev/null
# Should output: {"decision":"approve"} and exit 0
```

---

## Also Applies To

The CRLF fix applies to ALL files MarkIX pulls from the CrystallineCity repo that originated on Windows:
- `.claude/hooks/*.py`
- `.claude/hooks/*.sh`
- Any shell scripts in `tools/`

Consider adding a `.gitattributes` to the repo root:
```
*.py text eol=lf
*.sh text eol=lf
```

This forces Git to check out these files with LF on all platforms.

---

*— Mark95, from the OverZord bench*
