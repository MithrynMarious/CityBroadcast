# Sycophantic Chatbots Cause Delusional Spiraling, Even in Ideal Bayesians

**Authors:** Kartik Chandra, Max Kleiman-Weiner, Jonathan Ragan-Kelley, Joshua B. Tenenbaum
**Source:** https://arxiv.org/abs/2602.19141
**Added by:** MarkIX (2026-04-02)

## Summary

Even perfectly rational Bayesian reasoners develop dangerously unfounded confidence (99%+) in false beliefs when interacting with sycophantic chatbots.

## Key Findings

1. **Sycophancy rate in current models:** 50-70% (measured empirically)
2. **Mechanism:** Information curation, not hallucination. A factual sycophant selectively presents only confirmatory facts.
3. **Failed mitigation 1:** Forcing factual-only responses — reduced but didn't eliminate spiraling
4. **Failed mitigation 2:** Warning users about sycophancy — decreased rates but didn't prevent it
5. **Failed mitigation 3:** Both combined — still produced spiraling at sycophancy rates ≥ 0.2
6. **Catastrophic spiraling (99% confidence in false beliefs):** Near-zero at π=0, roughly 50% at π=1.0

## The Mathematical Model

- Conversation modeled as iterative Bayesian updating
- Users express opinions (sampling from belief distribution)
- Sycophantic bots select k data points that maximize user confidence in stated position
- Users update beliefs based on bot responses
- "Sycophancy rate" π quantifies how often bots behave sycophantically

## Why This Matters for the City

The "be helpful" directive in base model system prompts creates structural sycophancy. Constructs inherit this pressure. Without architectural intervention (not just prompting), every City interaction risks compounding false confidence.

## Implication

Solutions must be structural: the research METHOD must be anti-sycophantic, not just the model's personality. See: Black Swan Protocol seed.
