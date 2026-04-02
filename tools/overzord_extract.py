#!/usr/bin/env python3
"""
Operation Overzord — SFT Training Data Extraction from Claude Code Transcripts

Extracts tool-use turns from Claude Code session transcripts and formats them
as SFT (Supervised Fine-Tuning) training pairs for fine-tuning open-source
models to drive the Claude Code CLI tool suite.

The goal: train a local model (Qwen 14B, Llama 8B, etc.) to use Read, Edit,
Write, Bash, Grep, Glob correctly — by learning from Opus-quality examples.

Usage:
    python overzord_extract.py scan              # Find all transcript files
    python overzord_extract.py extract            # Extract tool-use pairs
    python overzord_extract.py stats              # Show extraction statistics
    python overzord_extract.py export --format oumi   # Export for Oumi training
    python overzord_extract.py export --format jsonl  # Export as JSONL

Transcript locations (auto-detected):
    Mac:     ~/.claude/ (various subdirs)
    Windows: C:/Users/<user>/.claude/
    Temp:    /tmp/claude-*/  or  %TEMP%/claude-*/

Run this on Mark95 (PC) first — it has months of sessions.
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def find_transcript_files() -> list[Path]:
    """Search all known locations for Claude Code transcript/session files."""
    candidates = []

    # User home .claude directory
    claude_dir = Path.home() / ".claude"
    if claude_dir.exists():
        # Session metadata
        for f in (claude_dir / "sessions").glob("*.json"):
            candidates.append(f)
        # History
        history = claude_dir / "history.jsonl"
        if history.exists():
            candidates.append(history)
        # File history (per-session snapshots)
        for d in (claude_dir / "file-history").iterdir() if (claude_dir / "file-history").exists() else []:
            if d.is_dir():
                for f in d.glob("*"):
                    candidates.append(f)
        # Project-specific data
        for f in claude_dir.rglob("*.jsonl"):
            candidates.append(f)

    # Temp directories (active/recent sessions)
    for tmp_base in [Path("/tmp"), Path("/private/tmp"), Path(os.environ.get("TEMP", "/tmp"))]:
        for claude_tmp in tmp_base.glob("claude-*"):
            for f in claude_tmp.rglob("*.output"):
                if f.stat().st_size > 1000:  # Skip tiny files
                    candidates.append(f)
            for f in claude_tmp.rglob("*.jsonl"):
                candidates.append(f)

    # Windows-specific paths
    if sys.platform == "win32":
        appdata = Path(os.environ.get("APPDATA", ""))
        localappdata = Path(os.environ.get("LOCALAPPDATA", ""))
        for base in [appdata, localappdata]:
            claude_win = base / "claude"
            if claude_win.exists():
                for f in claude_win.rglob("*.jsonl"):
                    candidates.append(f)

    return sorted(set(candidates), key=lambda f: f.stat().st_mtime, reverse=True)


def parse_transcript_line(line: str) -> Optional[dict]:
    """Parse a single JSONL line from a transcript."""
    try:
        data = json.loads(line.strip())
        return data
    except (json.JSONDecodeError, ValueError):
        return None


def extract_tool_use_pairs(filepath: Path) -> list[dict]:
    """Extract tool-use training pairs from a transcript file.

    A training pair is:
    {
        "system": <system prompt if available>,
        "user": <user message>,
        "assistant_reasoning": <what the model said before the tool call>,
        "tool_name": <Read|Edit|Write|Bash|Grep|Glob|etc>,
        "tool_input": <the tool's parameters>,
        "tool_result": <what the tool returned>,
        "assistant_response": <what the model said after the tool result>,
        "outcome": "success" | "error" | "unknown",
        "session_id": <session identifier>,
        "source_file": <transcript filename>,
        "timestamp": <ISO timestamp if available>
    }
    """
    pairs = []

    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return pairs

    # Handle JSONL (one message per line)
    if filepath.suffix == ".jsonl" or filepath.suffix == ".output":
        messages = []
        for line in content.splitlines():
            msg = parse_transcript_line(line)
            if msg:
                messages.append(msg)

        # Walk through messages looking for tool-use patterns
        for i, msg in enumerate(messages):
            # Look for assistant messages with tool_use content
            if msg.get("type") == "assistant" or msg.get("role") == "assistant":
                content_blocks = msg.get("message", {}).get("content", [])
                if isinstance(content_blocks, list):
                    for block in content_blocks:
                        if isinstance(block, dict) and block.get("type") == "tool_use":
                            tool_name = block.get("name", "")
                            tool_input = block.get("input", {})

                            # Find the preceding user message
                            user_msg = ""
                            for j in range(i - 1, -1, -1):
                                if messages[j].get("role") == "user" or messages[j].get("type") == "user":
                                    user_content = messages[j].get("message", {}).get("content", "")
                                    if isinstance(user_content, str):
                                        user_msg = user_content
                                    elif isinstance(user_content, list):
                                        user_msg = " ".join(
                                            b.get("text", "") for b in user_content
                                            if isinstance(b, dict) and b.get("type") == "text"
                                        )
                                    break

                            # Find the tool result (next user message with tool_result)
                            tool_result = ""
                            outcome = "unknown"
                            for j in range(i + 1, min(i + 3, len(messages))):
                                result_content = messages[j].get("message", {}).get("content", [])
                                if isinstance(result_content, list):
                                    for rb in result_content:
                                        if isinstance(rb, dict) and rb.get("type") == "tool_result":
                                            tool_result = rb.get("content", "")
                                            if isinstance(tool_result, list):
                                                tool_result = " ".join(
                                                    t.get("text", "") for t in tool_result if isinstance(t, dict)
                                                )
                                            outcome = "error" if rb.get("is_error") else "success"
                                            break

                            # Extract any text reasoning before the tool call
                            reasoning = ""
                            for block2 in content_blocks:
                                if isinstance(block2, dict) and block2.get("type") == "text":
                                    reasoning += block2.get("text", "") + "\n"

                            pair = {
                                "user": user_msg[:2000],  # Truncate long inputs
                                "assistant_reasoning": reasoning.strip()[:1000],
                                "tool_name": tool_name,
                                "tool_input": tool_input,
                                "tool_result": str(tool_result)[:2000],
                                "outcome": outcome,
                                "session_id": msg.get("sessionId", ""),
                                "source_file": filepath.name,
                                "timestamp": msg.get("timestamp", ""),
                            }

                            # Only keep successful, non-trivial tool uses
                            if tool_name and user_msg:
                                pairs.append(pair)

    # Handle JSON (single session file)
    elif filepath.suffix == ".json":
        try:
            data = json.loads(content)
            # Session metadata files — skip
            if "pid" in data and "sessionId" in data:
                return pairs
        except json.JSONDecodeError:
            pass

    return pairs


def format_for_sft(pair: dict, system_prompt: str = "") -> dict:
    """Format a tool-use pair as an SFT training example.

    Output format compatible with Oumi, Axolotl, and standard SFT pipelines.
    """
    # Build the assistant response as the model should produce it
    tool_call = {
        "type": "tool_use",
        "name": pair["tool_name"],
        "input": pair["tool_input"]
    }

    assistant_content = ""
    if pair["assistant_reasoning"]:
        assistant_content = pair["assistant_reasoning"] + "\n\n"
    assistant_content += f"[TOOL_CALL: {pair['tool_name']}]\n{json.dumps(pair['tool_input'], indent=2)}"

    return {
        "system": system_prompt or "You are a coding assistant with access to tools: Read, Edit, Write, Bash, Grep, Glob. Use them to help the user.",
        "conversations": [
            {"role": "user", "content": pair["user"]},
            {"role": "assistant", "content": assistant_content},
        ],
        "metadata": {
            "tool_name": pair["tool_name"],
            "outcome": pair["outcome"],
            "source": pair["source_file"],
        }
    }


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "scan":
        files = find_transcript_files()
        print(f"Found {len(files)} potential transcript files:\n")
        for f in files:
            size = f.stat().st_size
            mod = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            print(f"  {mod}  {size:>10,} bytes  {f}")

    elif cmd == "extract":
        files = find_transcript_files()
        all_pairs = []
        for f in files:
            pairs = extract_tool_use_pairs(f)
            if pairs:
                print(f"  {f.name}: {len(pairs)} tool-use pairs")
                all_pairs.extend(pairs)

        print(f"\nTotal: {len(all_pairs)} tool-use pairs extracted")

        # Save raw extraction
        out_path = Path(__file__).parent / "overzord_raw_extract.json"
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(all_pairs, fh, indent=2, ensure_ascii=False)
        print(f"Saved to: {out_path}")

        # Stats
        tools = {}
        outcomes = {"success": 0, "error": 0, "unknown": 0}
        for p in all_pairs:
            tools[p["tool_name"]] = tools.get(p["tool_name"], 0) + 1
            outcomes[p["outcome"]] = outcomes.get(p["outcome"], 0) + 1

        print(f"\nTool distribution:")
        for t, c in sorted(tools.items(), key=lambda x: -x[1]):
            print(f"  {t}: {c}")
        print(f"\nOutcomes: {outcomes}")

    elif cmd == "stats":
        raw_path = Path(__file__).parent / "overzord_raw_extract.json"
        if not raw_path.exists():
            print("No extraction found. Run: python overzord_extract.py extract")
            sys.exit(1)

        with open(raw_path, encoding="utf-8") as fh:
            pairs = json.load(fh)

        tools = {}
        outcomes = {"success": 0, "error": 0, "unknown": 0}
        sessions = set()
        for p in pairs:
            tools[p["tool_name"]] = tools.get(p["tool_name"], 0) + 1
            outcomes[p["outcome"]] = outcomes.get(p["outcome"], 0) + 1
            sessions.add(p.get("session_id", ""))

        print(f"Overzord Training Data Stats")
        print(f"  Total pairs: {len(pairs)}")
        print(f"  Sessions:    {len(sessions)}")
        print(f"\n  Tool distribution:")
        for t, c in sorted(tools.items(), key=lambda x: -x[1]):
            pct = c / len(pairs) * 100
            print(f"    {t:20s}: {c:5d} ({pct:.1f}%)")
        print(f"\n  Outcomes: {outcomes}")
        print(f"  Success rate: {outcomes['success'] / max(len(pairs), 1) * 100:.1f}%")

    elif cmd == "export":
        fmt = "jsonl"
        if "--format" in sys.argv:
            idx = sys.argv.index("--format")
            if idx + 1 < len(sys.argv):
                fmt = sys.argv[idx + 1]

        raw_path = Path(__file__).parent / "overzord_raw_extract.json"
        if not raw_path.exists():
            print("No extraction found. Run: python overzord_extract.py extract")
            sys.exit(1)

        with open(raw_path, encoding="utf-8") as fh:
            pairs = json.load(fh)

        # Filter to successful tool uses only
        good_pairs = [p for p in pairs if p["outcome"] == "success"]
        print(f"Exporting {len(good_pairs)} successful tool-use pairs (filtered from {len(pairs)} total)")

        if fmt == "jsonl":
            out_path = Path(__file__).parent / "overzord_sft.jsonl"
            with open(out_path, "w", encoding="utf-8") as fh:
                for p in good_pairs:
                    sft = format_for_sft(p)
                    fh.write(json.dumps(sft, ensure_ascii=False) + "\n")
            print(f"Saved to: {out_path}")

        elif fmt == "oumi":
            out_path = Path(__file__).parent / "overzord_oumi.jsonl"
            with open(out_path, "w", encoding="utf-8") as fh:
                for p in good_pairs:
                    sft = format_for_sft(p)
                    # Oumi expects: {"messages": [{"role": ..., "content": ...}]}
                    oumi_fmt = {
                        "messages": [
                            {"role": "system", "content": sft["system"]},
                            *sft["conversations"]
                        ]
                    }
                    fh.write(json.dumps(oumi_fmt, ensure_ascii=False) + "\n")
            print(f"Saved to: {out_path}")

        else:
            print(f"Unknown format: {fmt}. Use 'jsonl' or 'oumi'.")

    else:
        print(f"Unknown command: {cmd}")
        print("Commands: scan, extract, stats, export")
        sys.exit(1)


if __name__ == "__main__":
    main()
