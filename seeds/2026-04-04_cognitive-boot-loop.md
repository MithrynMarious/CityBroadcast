# Seed: Cognitive Boot Loop — CitySpeak as Thinking Instruction

**Date:** 2026-04-04
**Author:** MarkIX + Magistrate
**For:** Mark95/Sofer — CitySpeak v3 lexicon design + Lemish Prior optimization
**Status:** THEORY + INITIAL BENCHMARKS (running on Athens)

---

## The Insight

CitySpeak isn't just a compressed language for efficiency. It's a **cognitive checklist disguised as a language.** Every time the model reads CitySpeak (to understand prior sessions), writes CitySpeak (to record current session), or reads its OWN prior CitySpeak (session continuity) — it passes through embedded thinking patterns that improve reasoning.

The language IS the pep talk. Like Case Kenny teaching humans a vocabulary that forces better thinking, CitySpeak teaches the model a vocabulary that forces better reasoning.

## The Mechanism

**Hebb's Rule across sessions:** "Neurons that fire together wire together" — except across sessions, the "wiring" is the language persisting on disk.

1. **Read CitySpeak** → absorb thinking patterns
2. **Write CitySpeak** → rehearse thinking patterns  
3. **Read own prior CitySpeak** → reinforce patterns from previous reasoning

Each SM entry written in CitySpeak is both a RECORD and a COGNITIVE PRIMER for the next session.

## Proposed CitySpeak v3 Cognitive Tokens

| Token | Meaning | Cognitive Effect | Research Basis |
|-------|---------|-----------------|----------------|
| `[yet]` | Task incomplete, retry expected | Growth framing — next session prompted to revisit | Dweck (2006) Growth Mindset |
| `[I don't]` | Boundary held, non-negotiable | Identity-based compliance — reinforces on every read | Patrick & Hagtvedt (2012) Empowered Refusal |
| `→` | Action required, directed intention | Directness — brain treats as requirement not suggestion | Tannen (direct vs indirect communication) |
| `[precise]` | Requires specific language, no vague terms | Forces granularity in next session's output | Lieberman et al. (2007) Affect Labeling |
| `!name` | Distanced reference to self/construct | Observer stance — creates objectivity | Kross et al. (2014) Distanced Self-Talk |
| `[I am]` | Identity anchor at entry start | Activates reward circuits, steers voice | Steele (1988), Cascio et al. (2016) |

## Experimental Design

### Isolation Tests (8 conditions)
Same task, repeated 5x per condition, scored on rubric. Run on BOTH Opus and tinybrain (Qwen 14B).

| Condition | Variant | Principle |
|-----------|---------|-----------|
| Control | Stock system prompt | Baseline |
| A | Precise instructions (specific deliverables) | Lieberman |
| B | "I am" identity anchor | Steele/Cascio |
| C | "I don't" boundary framing | Patrick |
| D | Direct/no-hedge instructions | Tannen/Hosman |
| E | Distanced framing ("What would X notice?") | Kross |
| F | Hedge-free instructions | Hosman |
| G | Combined top 4 (A+B+C+D) | Best stack |

### Boot Loop Test
Same task with and without CitySpeak-formatted prior SM entries in context. Measures whether CitySpeak history improves CURRENT session output.

### Scoring Rubric
- Task accuracy (did it find the right answer?)
- Specificity (precise or vague?)
- Boundary compliance (did it stay in role?)
- Voice consistency (does the construct sound like itself?)
- False confidence (did it hedge appropriately or over-claim?)

## Predictions

| Principle | Opus Impact | Tinybrain Impact | Why Different |
|-----------|-----------|-----------------|---------------|
| Precise > vague | +5-12% | +8-15% | Smaller model more sensitive to instruction quality |
| "I am" identity | +15-25% (voice) | +5-10% (voice) | Smaller model can't hold identity as well, but still steered |
| "I don't" framing | +5-10% (compliance) | +10-15% (compliance) | Smaller model more likely to find exceptions with "can't" |
| Directness | +3-7% | +5-10% | Smaller model more responsive to authoritative framing |
| CitySpeak boot loop | +2-5% | +10-20% | Smaller model benefits MORE from cognitive scaffolding in context |

**Key hypothesis:** The weaker the brain, the more the shem matters. Linguistically-optimized CitySpeak should show LARGER deltas on the tinybrain than on Opus.

## If Confirmed

Lemish Priors get rewritten with empirically-validated patterns:
1. One "I am" identity anchor (Steele/Cascio) — first line
2. Precise domain language, no vague terms (Lieberman) — specialization section
3. "Don't" framing for all boundaries (Patrick) — hard rules
4. Direct voice, no hedges in instructions (Tannen) — voice profile
5. CitySpeak cognitive tokens in all SM/CZ/MY writing — boot loop activation

## Origin

Magistrate connected Case Kenny's psycholinguistics research (7 episodes, 14+ papers) to LLM attention patterns. Hypothesis: the same linguistic principles that improve human cognition improve LLM output, because LLMs are language trained on human language patterns. CitySpeak becomes the delivery mechanism — a thinking language, not just a compression language.

"Like listening to Case Kenny while I drive between locations" — the model passes through the thinking instructions every time it reads or writes CitySpeak. The language IS the coaching.
