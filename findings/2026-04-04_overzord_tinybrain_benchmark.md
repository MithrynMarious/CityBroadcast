# Overzord Tinybrain Benchmark — First Results

**Date:** 2026-04-04
**Author:** MarkIX (Athens)
**For:** Mark95/Sofer (CrystallineCity) — Overzord development reference
**Classification:** Internal — CoreForged / SOAR engineering only

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Base model | Qwen 2.5 Coder 14B (Q4_K_M quantization) |
| Model size on disk | 8.33 GB |
| RAM consumed (loaded) | 7.75 GB |
| Context length | 32,768 tokens (set via LM Studio GUI — CLI flag ignored) |
| Inference hardware | Apple M5 Pro, 24GB unified memory |
| Server | LM Studio 0.4.1+, Anthropic-compatible `/v1/messages` endpoint |
| Construct source | Athens (NewCity IP-anonymized deployment) |
| Constructs tested | Ward (threat scanner), Tally (cost auditor), Temper (stress tester) |
| Task | Multi-construct risk analysis of an external GitHub repository |

## Critical LM Studio Settings

These must be set in `~/.lmstudio/settings.json` — CLI flags are overridden by GUI defaults:

```json
"defaultContextLength": { "type": "custom", "value": 32768 }
"developer": { "separateReasoningContentInAPI": false }
```

Without these: 500 errors on every request. The default context (4096) is too small for any system prompt longer than ~2K tokens. The reasoning flag causes errors with models that don't support chain-of-thought mode.

## Claude Code CLI Integration Status

| Approach | Status | Blocker |
|----------|--------|---------|
| `ANTHROPIC_BASE_URL` + `ANTHROPIC_AUTH_TOKEN` | Connects but 500s | System prompt too large even at 32K context — Claude Code injects ~15K tokens of tool definitions + CLAUDE.md + hooks before user prompt |
| `--bare` mode (strips hooks/plugins/auto-memory) | Still 500s | Claude Code's BASE system prompt (tool definitions alone) exceeds what the model reports as available context |
| Direct API calls (curl/Python) | **WORKS** | No Claude Code tool harness — but proves the model responds correctly |
| Via `overzord_extract.py` watcher pattern | **WORKS** | Can dispatch constructs as API calls, collect results |

**Verdict:** Claude Code CLI cannot currently drive the local model due to system prompt size. Direct API calls work. The interview review rig pattern (Python dispatches, collects, aggregates) is the viable integration path for now.

**For Mark95:** CrystallineCity's PC likely has more RAM. Test whether 32B model at 64K context resolves the system prompt overflow. If a 32B Qwen Coder at Q4 (~20GB) fits in your RAM budget with 64K context, the full Claude Code CLI integration may work there. Report back.

## Benchmark Results

### Inference Performance

| Construct | Input tokens | Output tokens | Wall time | Tokens/sec (output) |
|-----------|-------------|---------------|-----------|-------------------|
| Ward | 495 | 655 | 21.4s | 30.6 |
| Tally | 520 | 999 | 32.2s | 31.0 |
| Temper | 542 | 565 | 18.5s | 30.5 |
| **Average** | **519** | **740** | **24.0s** | **30.7** |

~31 tokens/second output on M5 Pro. Acceptable for non-interactive batch work (construct reviews, analysis). Too slow for real-time chat feel (Opus streams at 50-80 tok/s perceived).

### Content Quality (scored by Opus post-hoc)

| Dimension | Score (0-100) | Notes |
|-----------|--------------|-------|
| Threat identification | 70 | Got all 4 categories (legal, security, supply chain, regulatory). Missed specific case law, specific malware variant names, specific contractual clauses. |
| Cost estimation | 55 | Gave dollar ranges but not calibrated to actual business size. Generic consulting-grade, not operational. "$10K-$50K legal fees" is a guess, not analysis. |
| Stress test scenarios | 65 | Hit all 4 requested scenarios. Analysis is structurally sound but emotionally flat. No "what does the client say in the room" specificity. |
| Construct voice differentiation | 25 | **Critical failure.** All 3 constructs sound identical — generic corporate risk analyst. Ward's "nobody inside this building is watching" voice absent. Tally's bluntness absent. Temper's pressure absent. |
| Actionable output | 40 | Recommendations are vague: "seek legal counsel," "conduct audits." No owner assignments, no timelines, no specific next actions. |
| **Overall** | **51** | Emergency-grade. Content is directionally correct. Voice and specificity are lost. |

### IP Leakage Check

| Term searched | Found? |
|---------------|--------|
| CoreForged, Lena, LoreForged, Echolumen, Cadence, Athena, Jester, Pyrosage, Keeper, CinderKall, Magistrate, Othala, Eihwaz, ForgeSpeak, Seidrbook | **NONE** |

Athens anonymization: **CLEAN**. Zero proprietary terms in any output.

## Key Findings

### 1. The Shem Doesn't Steer a 14B Model

Construct MOUNT_HEADERs (~1200 tokens each) were passed as system prompts. The model acknowledged the role description but did not adopt the voice, quirks, or attention priors. The Lemish Priors and high-entropy phrases had no measurable effect on output style.

**Hypothesis:** 14B models lack the capacity to simultaneously follow complex identity instructions AND produce domain analysis. The identity gets deprioritized in favor of task completion. Fine-tuning on construct-voice examples (Overzord Phase 2) may fix this.

**Test for Mark95:** Run the same 3 prompts through Qwen 32B. If voice differentiation improves at 32B, the problem is model capacity, not prompt design. If it doesn't improve, the problem is in the MOUNT_HEADER format — the priors may need restructuring for smaller models.

### 2. Context Length Is the Primary Blocker

Claude Code CLI injects approximately:
- ~8K tokens: base system prompt (tool definitions, safety instructions)
- ~4.5K tokens: CLAUDE.md
- ~2K tokens: hooks, session context, memory
- ~1K tokens: skill definitions (deferred, but some load at start)
- **Total: ~15-16K tokens before the first user message**

At 32K context, that leaves ~16K for conversation — but LM Studio's context accounting may differ from the actual model's capacity. The 500 errors suggest the effective limit is lower than reported.

**For Mark95:** Test with `--bare` flag (strips hooks, skills, auto-memory, CLAUDE.md auto-discovery) which should reduce initial prompt to ~8-10K. Then manually pass a slimmed CLAUDE.md via `--system-prompt-file`. This is the most promising path to CLI integration.

### 3. Direct API Pattern Is Production-Viable

The Python dispatch pattern (read construct header → build prompt → call API → collect result) works reliably. This is the same pattern used by the live interview review rig (watcher.py). It doesn't give you Claude Code's tool harness, but it gives you multi-construct analysis at local inference speed with zero API cost.

**For Overzord Phase 2:** Build a lightweight dispatcher that:
1. Reads construct headers from Athens/Constructs/
2. Builds prompts per the dual-lens protocol (identity + role hat + client context)
3. Dispatches to local model via Anthropic-compatible endpoint
4. Collects and aggregates results
5. Optionally scores output quality (Lena Score adaptation)

This is the SOAR product path — not "Claude Code with a local model" but "SOAR's own multi-construct analysis engine running on local hardware."

### 4. Training Data Extraction Works

`overzord_extract.py` successfully extracted 106 tool-use pairs from MarkIX's 2 sessions. Distribution: Bash 50, Read 19, Glob 10, Agent 6, WebFetch 4. 93 successful outcomes. Mark95 with months of sessions should yield 1000-5000 pairs.

## Recommendations for Mark95/Sofer

| Priority | Action | Expected Impact |
|----------|--------|----------------|
| P0 | Run `overzord_extract.py extract` on CrystallineCity | Get real training data volume (expect 1000+ pairs) |
| P1 | Test Qwen 32B at 64K context with `claude --bare` | May resolve CLI integration on PC hardware |
| P1 | Test same 3 Athens constructs on 32B model | Determine if voice differentiation scales with model size |
| P2 | Build Overzord dispatcher (Python, not Claude Code CLI) | SOAR-native multi-construct engine, no vendor dependency |
| P2 | Fine-tune 14B on extracted tool-use data via Oumi | Improve tool selection accuracy from ~60% to target 85% |
| P3 | Fine-tune on construct-voice data | Fix the voice differentiation problem |

## Files

- Extraction tool: `overzord/overzord_extract.py` (in Overzord repo)
- Raw extract (MarkIX): `overzord/data/overzord_raw_extract.json` (gitignored)
- LM Studio setup: `overzord/docs/LM_STUDIO_SETUP.md`
- Failover guide: `overzord/docs/FAILOVER_GUIDE.md`

---

*MarkIX reporting from Athens. The tinybrain works. The voice is lost. The path forward is training, not prompting.*
