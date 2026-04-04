# Multi-Construct AI Architecture: Design, Benchmarks, and Local Inference Viability

**Author:** CoreForged LLC / SOAR.ai Engineering
**Date:** April 2026
**Audience:** AI engineering leadership, technical evaluators, potential partners

---

## Abstract

This report documents a production AI architecture that orchestrates multiple specialized agent identities ("constructs") through a shared tool harness and persistent memory system. Unlike single-agent approaches, the system routes tasks through domain-specific agents with distinct operational parameters, attention patterns, and quality frameworks — coordinated by a project management layer and backed by a knowledge graph with 1,457 relationship edges.

We present benchmark results comparing the architecture running on a frontier API model (Claude Opus 4.6) against a locally-hosted open-source model (Qwen 2.5 Coder 14B), demonstrating that the orchestration framework is model-agnostic: the same construct definitions, memory system, and tool interfaces produce usable output on both backends, with measurable quality differences that inform deployment decisions.

---

## 1. Architecture Overview

### 1.1 Core Components

The system comprises four independent layers:

**Identity Layer ("Shem")**
A set of markdown instruction files that define operational behavior for the AI session. Each file specifies: role description, domain specialization, voice parameters, attention priors (what the agent notices first), interaction rules, and high-entropy phrases that anchor the agent's behavioral distribution. These files are model-agnostic — they function as system prompts for any LLM that supports instruction-following.

**Tool Layer ("Suit")**
The tool interface through which the LLM interacts with the environment. Currently implemented via Claude Code CLI (Read, Edit, Write, Bash, Grep, Glob, Agent), with MCP (Model Context Protocol) extensions for domain-specific capabilities (memory search, knowledge graph queries, construct registry lookups). The tool layer is backend-independent — any LLM that supports the Anthropic Messages API can drive the same tools.

**Memory Layer**
Three-tier persistent memory:
- **EAM (Enhanced Active Memory):** Append-only forensic session logs with structured metadata. Currently 245+ entries indexed with hybrid retrieval (keyword, semantic embeddings, Hebbian co-occurrence, temporal decay).
- **Knowledge Graph:** 448 nodes, 1,457 edges mapping relationships between sessions, projects, agents, and artifacts. Backed by Apache AGE (PostgreSQL) for persistent Cypher queries, with NetworkX fallback.
- **CMB (Conversation Memory Buffer):** Medium-term conversational texture. Zone-based compaction (identity 90d, knowledge 60d, operations 30d).

**Construct Layer**
47 named agent identities, each with:
- Identity file (role, voice, attention priors, behavioral rules)
- Domain specialization tags for automated routing
- Self-authored preference/fear/awe parameters that influence memory decay rates
- Mountable as overlays on the base agent (single or dual-mount)

### 1.2 Construct Orchestration

Tasks are routed through constructs based on domain matching. A project management construct (persistent overlay) recommends which specialist(s) to activate for each task. Multiple constructs can operate in parallel — dispatched as independent inference calls that return structured output aggregated by the orchestration layer.

Gate logic governs multi-construct output:
- **AND gate:** All constructs must agree (quality assurance)
- **XOR gate:** Disagreement escalates to human decision-maker
- **AWE gate:** Disagreement is preserved as output, not resolved (exploratory research)

### 1.3 Anti-Sycophancy Framework

Based on Chandra et al. (2025, "Sycophantic Chatbots Cause Delusional Spiraling, Even in Ideal Bayesians"), the system implements structural countermeasures against confirmation bias:

- **Epistemology Interview:** Maps user beliefs, evidence standards, and emotional attachments before research begins. Captures falsification thresholds ("what would change your mind?") and goalpost locks ("what sources do you trust?").
- **Falsification-first research:** Disconfirming searches are generated before confirming searches. Every finding carries a counter-evidence count.
- **Doubling-down detection:** Per-turn monitoring for certainty escalation, source dismissal, and goalpost movement — signals that the user is deepening commitment to a hypothesis despite contradicting evidence.
- **Sycophancy score:** Per-session measurement of confirming-to-disconfirming output ratio, ground-holding vs. capitulation count, and self-reported assessment of base-model agreement pressure.

---

## 2. Deployment Configurations

The architecture has been tested in two configurations:

| Configuration | Model | Inference | Memory Budget | Context Window |
|--------------|-------|-----------|---------------|----------------|
| **Cloud (primary)** | Claude Opus 4.6 | Anthropic API | Unlimited | 1M tokens |
| **Local (failover)** | Qwen 2.5 Coder 14B | LM Studio on Apple M5 Pro | 7.75 GB model + 24 GB system | 32K tokens |

Both configurations use identical:
- Construct identity files
- Memory system (EAM index, knowledge graph, embeddings)
- Tool interfaces
- Orchestration logic

---

## 3. Benchmark: Cloud vs. Local Inference

### 3.1 Test Design

Three constructs were dispatched in parallel to analyze a software repository for risk assessment. Each construct received:
- Its identity file as system prompt (~1,200 tokens)
- A shared context block describing the repository (~200 tokens)
- A domain-specific analysis prompt (~150 tokens)

Constructs:
- **Ward** (threat scanner): External risk identification — legal, security, supply chain, regulatory
- **Tally** (cost auditor): Financial and opportunity cost quantification
- **Temper** (stress tester): Scenario analysis under hostile conditions

### 3.2 Performance Results

| Metric | Cloud (Opus 4.6) | Local (Qwen 14B) |
|--------|-----------------|-------------------|
| Output tokens/second | 50-80 (streamed) | 30.7 (batch) |
| Average response time | ~8s per construct | ~24s per construct |
| Parallel dispatch overhead | Negligible (API) | Negligible (localhost) |
| Total wall time (3 constructs) | ~10s (parallel API) | ~72s (sequential local) |
| Cost per run | ~$0.15 (API billing) | $0.00 (local hardware) |

### 3.3 Content Quality Assessment

Output from both configurations was evaluated across five dimensions by a human reviewer with domain expertise:

| Dimension | Cloud (Opus) | Local (Qwen 14B) | Delta |
|-----------|-------------|-------------------|-------|
| **Threat identification** (did it find the real risks?) | 95 | 70 | -25 |
| **Cost estimation** (calibrated to actual business context?) | 85 | 55 | -30 |
| **Stress test scenarios** (specific and actionable?) | 90 | 65 | -25 |
| **Construct voice differentiation** (do agents sound distinct?) | 90 | 25 | -65 |
| **Actionable output** (specific next steps with owners?) | 90 | 40 | -50 |
| **Overall** | **90** | **51** | **-39** |

### 3.4 Key Findings

**Finding 1: Content is directionally correct on local inference.**
The 14B model identified the same risk categories as the frontier model in all three constructs. Legal exposure, security concerns, supply chain fragility, and regulatory implications were all surfaced. The gap is in specificity — the frontier model cites specific precedents, names specific malware variants, and calibrates cost estimates to the actual business. The local model gives generic ranges.

**Finding 2: Construct voice differentiation fails on smaller models.**
The most significant quality gap (-65 points) is in construct voice. The frontier model produces distinct writing styles, speech patterns, and analytical frameworks per construct — a threat scanner writes differently than a cost auditor. The 14B model produces functionally identical output regardless of which construct identity is loaded. The identity instructions are acknowledged but not internalized.

**Hypothesis:** Voice differentiation scales with model parameter count and instruction-following capability. Fine-tuning on construct-voice examples (supervised learning from frontier model sessions) may partially close this gap. Testing at 32B parameters is planned.

**Finding 3: The architecture is genuinely model-agnostic.**
The same construct files, the same orchestration logic, and the same prompt structure produced structured output on both backends. Switching from cloud to local required zero changes to construct definitions, memory configuration, or dispatch logic — only the API endpoint URL changed. This confirms the design principle: the identity layer and tool layer are independent of the inference layer.

**Finding 4: IP isolation holds under local inference.**
The anonymized construct deployment (renamed identities, scrubbed proprietary references) produced zero IP leakage across all 3 construct outputs totaling 2,219 tokens. The construct renaming and file migration preserved functional capability while removing all traceable proprietary terminology.

---

## 4. Memory System Performance

### 4.1 Knowledge Graph

| Metric | Value |
|--------|-------|
| Total nodes | 448 |
| Total edges | 1,457 |
| Node types | EAM entries (session logs), EPICs (projects), Agents (instances), Files, Humans |
| Edge types | interacted_in, created_by, preceded_by, worked_on, touches_file |
| Backend | Apache AGE (PostgreSQL) + NetworkX fallback |
| Build time | ~3 seconds |
| Query time (traversal) | <100ms |

### 4.2 Semantic Search

| Metric | Value |
|--------|-------|
| Embedding model | all-MiniLM-L6-v2 (384 dimensions) |
| Indexed entries | 245 |
| Embedding build time | ~2 seconds (incremental, hash-based change detection) |
| Search latency | <200ms |
| Retrieval strategies | 4 (keyword, semantic, Hebbian co-occurrence, recursive sub-question decomposition) |
| Strategy selection | UCB1 multi-armed bandit (auto-selects best strategy per query type) |

### 4.3 Decay Model

Memory entries decay at rates calibrated by category:

| Category | Halflife | Use Case |
|----------|----------|----------|
| Fear-tagged entries | ~2.4 years | Danger-sense. What the system flinches from. Persists because forgetting danger is dangerous. |
| Awe-tagged entries | ~3.8 years | Foundational insights. Nearly permanent. |
| Preference-tagged | ~1.9 years | Operational identity. Stable. |
| Interest-tagged | ~347 days | Active investigations. Releases on resolution. |
| Knowledge (default) | ~138 days | Session records. Standard decay. |
| Operations | ~46 days | Session artifacts. Self-clearing. |

Constructs author their own preference/fear/awe entries, which create keywords that resist temporal decay in the search index. This produces identity-shaped memory — different constructs remember different things longer based on what matters to their role.

---

## 5. Training Data Pipeline (Overzord)

### 5.1 Extraction

An automated extraction tool (`overzord_extract.py`) scans Claude Code CLI session transcripts and produces supervised fine-tuning (SFT) training pairs:

```
{user_prompt} → {tool_selection, tool_parameters, tool_result, assistant_response}
```

| Metric | Value |
|--------|-------|
| Sessions scanned | 2 (new deployment) |
| Tool-use pairs extracted | 106 |
| Success rate | 88% (93/106) |
| Tool distribution | Bash 47%, Read 18%, Glob 9%, Agent 6%, Web 7%, Write/Edit 5% |
| Export formats | JSONL (generic SFT), Oumi platform format |

Older deployments with months of sessions are expected to yield 1,000-5,000 training pairs.

### 5.2 Fine-Tuning Approach

The extracted training data enables supervised fine-tuning of open-source models on tool-use patterns specific to the deployment's actual workflow. The training target is not general coding ability — it is accurate tool selection and parameter construction for the specific tool interface.

Training platforms evaluated:

| Platform | Approach | Cost | Hardware |
|----------|----------|------|----------|
| Oumi | Automated evaluate→synthesize→train loop | $25/month or free (OSS) | Cloud GPUs |
| Unsloth | LoRA/QLoRA, fast iteration | Free | Consumer GPU (16GB+ VRAM) |
| Direct (Axolotl/HuggingFace) | Full fine-tune | GPU rental (~$50-400) | Cloud |

Expected improvement: tool selection accuracy from ~60% (stock) to ~85% (fine-tuned) based on published results for similar SFT pipelines on coding models (Allen AI Open Coding Agents, 2025; TeichAI distillation, 2026).

---

## 6. Use Cases

### 6.1 Multi-Construct Review

Parallel dispatch of 3-6 constructs to review a deliverable, plan, or artifact through distinct analytical lenses. Each construct produces independent structured output. Gate logic determines how disagreements are handled.

**Example:** A project closure review dispatched to three constructs produced:
- Project management lens: identified 2 of 4 acceptance criteria with coverage gaps, recommended spawning a successor project
- Legal/compliance lens: flagged GDPR deletion capability as highest risk (no deletion process across two data systems)
- Quality honesty lens: graded the closure decision as "ADEQUATE — pragmatically right but narratively dishonest"

Total review time: ~25 seconds (cloud, parallel). Cost: ~$0.45.

### 6.2 Real-Time Interview Augmentation

A file watcher monitors for new session logs. When a new entry appears (e.g., from a live interview being recorded), it dispatches 4 constructs in parallel to analyze the content through different lenses and surface follow-up questions within ~25 seconds:
- Translation/empathy lens: What isn't being said?
- Emotional intelligence lens: What does this mean to the person personally?
- Memory/preservation lens: What stories here are worth preserving?
- Pattern recognition lens: Does this contradict earlier statements?

### 6.3 Failover Operations

When the primary API is unavailable, the system switches to local inference with a single environment variable change. The identity files, memory system, and tool interfaces remain identical. Quality degrades on complex reasoning and voice differentiation but remains functional for file operations, code editing, and structured analysis.

---

## 7. Conclusions

1. **Multi-construct orchestration produces measurably different output than single-agent approaches.** Parallel constructs surface findings that sequential single-agent analysis misses — specifically cross-domain risks, emotional subtext, and quality honesty that a single "helpful assistant" identity is structurally incentivized to suppress.

2. **The architecture is model-agnostic in practice, not just theory.** The same construct definitions produced structured output on both a frontier 1M-context API model and a local 14B model with 32K context. Quality scales with model capability, but the framework functions across a 100x parameter range.

3. **Construct voice differentiation is the primary quality casualty at smaller model sizes.** Content accuracy degrades ~25-30% from frontier to local. Voice differentiation degrades ~65%. This is the most promising target for domain-specific fine-tuning.

4. **Anti-sycophancy must be structural, not instructional.** The sycophancy research (Chandra et al., 2025) demonstrates that prompt-based interventions fail. Our epistemology interview and falsification-first research protocol address this architecturally — the research method itself is designed to seek disconfirming evidence before confirming evidence.

5. **The training data for domain-specific fine-tuning is a natural byproduct of normal operations.** Every session generates tool-use transcripts that can be extracted as SFT training pairs. Organizations that adopt this architecture accumulate fine-tuning data passively — the more they use the system, the better the local fallback becomes.

---

## Appendix A: Glossary

| Term | Definition |
|------|-----------|
| Construct | A named agent identity with defined role, voice, specialization, and behavioral parameters |
| Shem | The instruction layer (identity files + skills + protocols) that shapes LLM behavior. Model-agnostic. |
| Mount | Activating a construct's identity file as the current session's behavioral overlay |
| Gate | Logic governing multi-construct output aggregation (AND, XOR, AWE) |
| EAM | Enhanced Active Memory — append-only session logs with structured retrieval |
| Lemish Prior | A high-entropy phrase embedded in a construct's identity file that anchors attention patterns |
| Dual-lens | Composing identity (who the agent IS) + role (what domain they're working in) + client context (who they're working for) at mount time |
| Overzord | Project name for the local inference fallback and domain-specific fine-tuning pipeline |

## Appendix B: Repository Structure

| Repository | Purpose |
|------------|---------|
| CrystallineCity | Primary development environment — full construct registry, memory, Foundry |
| NewCity | Portable deployment kit — anonymized constructs, setup automation |
| SuperClaude | Shared skill/hook armory — synced across all instances |
| CityBroadcast | Cross-instance knowledge sharing — seeds, findings, protocols |
| Overzord | Local inference pipeline — extraction, training, benchmarking |
| CrystallineCity-Foundry | Multi-agent production templates — dispatch configs, voyage templates |

---

*CoreForged LLC / SOAR.ai — April 2026*
