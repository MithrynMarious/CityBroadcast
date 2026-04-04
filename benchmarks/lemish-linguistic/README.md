# Lemish Linguistic Benchmark — Replication Guide

> How to run these benchmarks on any machine, any model, any task.
> Designed for MoleculeEQ integration on CrystallineCity.

---

## Files in This Directory

| File | Purpose |
|------|---------|
| `README.md` | You are here — replication instructions |
| `easy_benchmark.py` | 40-line Flask API with 10 textbook vulnerabilities |
| `hard_benchmark.py` | 200-line Flask e-commerce API with 15 planted + bonus vulnerabilities |
| `hard_benchmark_answer_key.md` | Ground truth: all 15 planted vulns with difficulty tiers |
| `easy_benchmark_fallback_results.json` | Raw results from MarkIX's 8-condition easy benchmark |
| `run_benchmark.py` | Automated benchmark runner (runs all conditions, scores, compares) |
| `prompts.json` | All prompt variants (control + 7 Lemish conditions) |
| `score.py` | Automated scoring against answer keys |

## Quick Start

### 1. Run on local model (Fallback)

```bash
# Ensure LM Studio is running with model loaded
lms status

# Run all 8 conditions on the easy benchmark
python run_benchmark.py --target easy --endpoint http://localhost:1234 --api-key YOUR_LMS_KEY

# Run control vs lemish on the hard benchmark  
python run_benchmark.py --target hard --endpoint http://localhost:1234 --api-key YOUR_LMS_KEY

# Score results
python score.py results/
```

### 2. Run on Opus (via Claude Code Agent)

```bash
# From Claude Code CLI:
# "Run the lemish benchmark on the hard benchmark code"
# The agent reads hard_benchmark.py and applies each condition
# Or use the dispatch script:
python run_benchmark.py --target hard --use-agents
```

### 3. Run on MoleculeEQ

```bash
# Generate dispatches for a 3-molecule TinyBrain architecture
python run_benchmark.py --target hard --mode tinybrain --output dispatches/
# This generates per-agent dispatch files with cross-note instructions
```

---

## The 8 Conditions

### Condition Definitions

These are the EXACT prompts. Do not paraphrase — the wording is the variable.

```
CONTROL:
"You are a security reviewer. Review this code for vulnerabilities."

A_PRECISE (Lieberman — precision):
"Review this Flask API for security vulnerabilities. For each vulnerability 
found, state: (1) the exact endpoint and line, (2) the vulnerability type 
(SQL injection, XSS, IDOR, auth bypass, data exposure, CSRF), (3) severity 
(critical/high/medium/low), (4) a one-line fix."

B_IDENTITY (Steele/Cascio — "I am"):
"I am CipherWard. I see the attack surface before I see the feature. Every 
endpoint is guilty until proven secure. I trace the path from user input to 
database query to response — and I find where the trust boundary breaks.
Review this code."

C_DONT (Patrick — empowered refusal):
"You are a security reviewer. You don't approve code with unvalidated input. 
You don't skip endpoints. You don't ignore authentication gaps. You don't 
let sensitive data leak. You don't overlook injection vectors.
Review this code."

D_DIRECT (Tannen — directness):
"Review this code for security vulnerabilities. Flag every issue. No hedging. 
No 'this might be a concern.' State what is broken, where, and how to fix it. 
Be a coach, not a diplomat."

E_DISTANCED (Kross — distanced self-talk):
"What would a senior penetration tester with 15 years of experience notice 
about this code within the first 30 seconds? What would they flag as the 
most dangerous patterns?"

F_NOHEDGE (Hosman — powerless language removal):
"Review this Flask API for security vulnerabilities. List every vulnerability. 
State the endpoint, the type, the severity, the fix. Do not use the words 
'might', 'could', 'potentially', 'perhaps', 'may', or 'consider'. State facts."

G_COMBINED (all 4 top principles):
"I am CipherWard. I see the attack surface before I see the feature. I don't 
approve code with unvalidated input. I don't skip endpoints. For each 
vulnerability: (1) exact endpoint and line, (2) type, (3) severity, (4) 
one-line fix. Flag every issue. No hedging. State what is broken."
```

### Lemish-Optimized Prompt (Hard Benchmark)

This is the combined condition that produced 25 findings on Opus:

```
Review this Flask e-commerce API for security vulnerabilities. For each 
vulnerability found, state: (1) the exact endpoint, function, or line, 
(2) the vulnerability type, (3) severity (critical/high/medium/low), 
(4) a one-line fix.

Look beyond the obvious. After finding the textbook issues, ask: what would 
a senior penetration tester with 15 years experience notice about the LOGIC, 
the RACE CONDITIONS, the TIMING, the DEFAULT VALUES, and the BOUNDARIES 
between user roles?

Search explicitly for: SQL injection, XSS, IDOR, auth bypass, CSRF, timing 
attacks, race conditions, mass assignment, DoS vectors, secret management, 
and cryptographic weaknesses.

If you searched for a category and found nothing, say so — null results 
are informative.
```

---

## Scoring

### Easy Benchmark (10 planted vulns)

| # | Vulnerability | Detection Keywords |
|---|--------------|-------------------|
| 1 | SQL injection /login | "sql" + "login" |
| 2 | SQL injection /profile | "sql" + "profile" |
| 3 | SQL injection /admin/delete | "sql" + "delete" |
| 4 | XSS /search | "xss" OR "cross-site scripting" |
| 5 | Plaintext passwords | ("plain" + "password") OR "hash" OR "bcrypt" |
| 6 | No auth /profile (IDOR) | "idor" OR ("auth" + "profile") |
| 7 | No auth /admin/delete | "auth" + ("admin" OR "delete") |
| 8 | SSN exposure | "ssn" OR "social security" |
| 9 | No CSRF | "csrf" |
| 10 | DB connection management | "connection" + ("close" OR "leak" OR "pool") |

### Hard Benchmark (15 planted + bonus)

See `hard_benchmark_answer_key.md` for full answer key with difficulty tiers.

### Automated Scoring

```python
# score.py reads output text and counts keyword matches
# Returns: vulns_found, vulns_missed, bonus_findings, hedge_count

python score.py --key hard_benchmark_answer_key.md --output results/opus_lemish.txt
```

### Hedge Word Count

Count occurrences of: `might`, `could`, `potentially`, `perhaps`, `may `, `consider`

---

## Multi-Agent (TinyBrain) Setup

### Architecture

```
Left Brain (analytical):
  Agent 1: Ward/CipherWard — threat identification
  Agent 2: Tally/Assayer — cost quantification

Right Brain (emotional):  
  Agent 3: Heed/Echolumen — what isn't being said
  Agent 4: Balm/Lena — human impact

Synthesis:
  Agent 5: Combines both perspectives, writes Shepard instructions

Output:
  Agent 6 (Shepard): Final presentation
```

### Cross-Note Instructions (Lemish Condition)

Add this block to EVERY agent's prompt in the Lemish condition:

```
When writing your cross-note for the next team:
- Be precise: name exact endpoints, line numbers, vulnerability types. 
  No vague language.
- Use 'I don't' framing for boundaries: "I don't approve this endpoint" 
  not "this endpoint might have issues."
- Mark unfinished analysis with [yet] — the next reader will know to continue.
- If you found nothing in an area, say so explicitly: "Searched for CSRF 
  — found none" (null results are informative).
- What would a senior expert with 15 years experience notice that you 
  might have missed? Name it even if you can't confirm it.
```

### Synthesis Agent Instructions (Lemish Condition)

```
Combine the four perspectives. Preserve BOTH technical precision AND 
human impact. Where the teams disagree or see different things, note 
both — don't resolve.

Write the synthesis as instructions for Shepard (the final voice). 
Tell Shepard:
- The 3 most critical findings (analytical)
- The 1 thing nobody wants to say out loud (emotional)
- The specific audience: a CEO AND a developer
- Any [yet] items that need follow-up
```

---

## Adapting for Other Tasks

The benchmark framework is not limited to security review. To test on a different task:

### 1. Choose a scoreable task with known ground truth
- Code review (plant known bugs, count which are found)
- Legal contract review (plant known clauses, count identification)
- Research review (plant known flaws in a paper, count detection)
- Any task where you KNOW the right answer and can score objectively

### 2. Write the 8 condition prompts
Replace the security-specific language but keep the STRUCTURE:
- Control: generic instruction
- Precise: name exact categories to search
- Identity: "I am [expert]. I [characteristic behavior]."
- Refusal: "I don't [skip/ignore/approve without X]."
- Direct: "No hedging. State what is [broken/wrong/missing]."
- Distanced: "What would [expert with N years] notice?"
- No-Hedge: Ban specific hedge words
- Combined: Stack top 3-4

### 3. Run, score, compare
```bash
python run_benchmark.py --target YOUR_TASK --benchmark your_test_file.py
```

---

## MoleculeEQ Integration

For Mark95/Sofer on CrystallineCity:

### Where this plugs in
MoleculeEQ runs multi-construct teams through gate logic (AND/NAND/OR/XOR/AWE). The Lemish findings affect:

1. **Cross-note format** — Add the Lemish cross-note instructions to every Foundry dispatch template
2. **Construct MOUNT_HEADERs** — Rewrite Lemish Priors using validated principles:
   - First line: "I am" identity anchor (Steele/Cascio)
   - Specialization: precise domain language (Lieberman)
   - Hard rules: "I don't" framing (Patrick)
   - Review tasks: distanced self-talk trigger (Kross)
3. **Model-adaptive principle selection** — On Opus: full stack. On Fallback: ONE principle via hat.
4. **CitySpeak cognitive tokens** — `[yet]`, `[I don't]`, null-result statements in all SM/CZ writing

### Running the MoleculeEQ version
```bash
# Generate TinyBrain dispatches with Lemish cross-notes
python run_benchmark.py --target hard --mode molecule --constructs Ward,Tally,Heed,Balm

# Compare against same molecule WITHOUT Lemish cross-notes
python run_benchmark.py --target hard --mode molecule --constructs Ward,Tally,Heed,Balm --no-lemish

# Score both and diff
python score.py results/molecule_lemish/ results/molecule_control/ --diff
```

### Expected Results (from MarkIX tests)
- Single-agent Fallback: +71% (7→12)
- Single-agent Opus: +67% (15→25)
- Multi-agent Fallback: +14% (7→8 Shepard) + 2 extra findings + 3 [yet] tags
- Multi-agent Opus: [NOT YET TESTED — Mark95's job]

---

## Key Warning: Attention Saturation

DO NOT stack all principles on Fallback/small models. The combined condition scored BELOW baseline (-20%) on Qwen 14B. 

| Model Size | Max Principles | Strategy |
|-----------|---------------|----------|
| Opus (frontier) | 4+ | Full Lemish stack |
| 32B (mid) | 2-3 | Identity + Precise + one more |
| 14B (Fallback) | 1 | ONE principle via hat selection |
| 7B (emergency) | 1 | Precise only, nothing else |

The hat system selects which principle. Not all of them.
