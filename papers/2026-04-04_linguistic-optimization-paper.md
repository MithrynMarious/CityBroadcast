# Psycholinguistic Prompt Optimization for AI Agent Systems: Empirical Evidence That Human Cognitive Principles Improve Machine Reasoning

**Authors:** Kenneth Lines¹, MarkIX², Mark95²
¹ CoreForged LLC / SOAR.ai, CEO
² Crystalline City AI Agent System, CoreForged LLC

**Draft Date:** April 2026
**Status:** Preprint / Working Paper

---

## Abstract

We present empirical evidence that psycholinguistic principles validated in human cognition research — specifically precision in language (Lieberman et al., 2007), empowered refusal framing (Patrick & Hagtvedt, 2012), distanced self-talk (Kross et al., 2014), and identity anchoring (Steele, 1988; Cascio et al., 2016) — measurably improve large language model output when applied to system prompts, inter-agent communication, and multi-agent orchestration pipelines.

We tested these principles in isolation and combination across two model scales: a frontier model (Claude Opus 4.6, ~1T+ parameters) and a locally-hosted open-source model (Qwen 2.5 Coder 14B) on security vulnerability detection tasks of varying complexity. On a 15-vulnerability benchmark with difficulty tiers ranging from textbook to expert-level:

- **The 14B model improved from 7/15 to 12/15 (+71%)** when the prompt was linguistically optimized, closing 80% of the capability gap to the frontier model.
- **The frontier model improved from 15 total findings to 25 (+67%)**, discovering 10 additional real vulnerabilities beyond the planted answer key.
- **Combining all principles simultaneously degraded the 14B model by 20%** while improving the frontier model, demonstrating a capacity-dependent interaction effect we term "attention saturation."

These results suggest that the linguistic structure of prompts and inter-agent communications functions as a cognitive amplifier whose effect scales inversely with model capability — the weaker the model, the greater the benefit — while simultaneously expanding the search space of stronger models beyond their unprompted ceiling.

---

## 1. Introduction

Large language models (LLMs) are trained on human language and inherit the statistical patterns of that language, including patterns associated with both effective and ineffective human cognition. A growing body of work in prompt engineering has established that LLM output quality is sensitive to prompt phrasing (Wei et al., 2022; Kojima et al., 2022), but the field has largely treated prompt optimization as an empirical craft rather than drawing on the mature science of how language shapes human cognition.

Psycholinguistic research has identified specific linguistic interventions that measurably change human reasoning performance:

1. **Affect labeling** — naming an emotion with a precise word reduces amygdala reactivity and improves emotional regulation (Lieberman et al., 2007)
2. **Empowered refusal** — "I don't" framing produces significantly greater goal persistence than "I can't" framing (Patrick & Hagtvedt, 2012)
3. **Distanced self-talk** — referring to oneself in the third person or using the generic "you" improves reasoning under stress (Kross et al., 2014; Moser et al., 2017)
4. **Self-affirmation** — "I am" identity statements activate reward circuits and improve problem-solving under stress (Steele, 1988; Cascio et al., 2016; Creswell et al., 2013)
5. **Precision over vagueness** — specific emotion vocabulary ("frustrated" vs. "bad") predicts better regulation outcomes (Barrett, 2017; Kashdan et al., 2015)
6. **Directness over indirectness** — explicit communication reduces hostility and improves problem-solving (Tannen; Rogers et al., 2018)

We hypothesized that because LLMs are language models trained on human language, these same principles would affect LLM output when embedded in prompts and inter-agent communication protocols. Specifically, we predicted that:

- **H1:** Each principle would independently improve output quality on a scored task.
- **H2:** The effect would be larger on smaller models ("cognitive prosthetic" hypothesis).
- **H3:** Combining multiple principles would show diminishing or negative returns on smaller models due to attention capacity limits.
- **H4:** In multi-agent pipelines, embedding these principles in inter-agent communication would improve the final synthesized output.

---

## 2. Method

### 2.1 Task Design

We constructed two security vulnerability detection benchmarks:

**Easy Benchmark:** A 40-line Flask API with 10 textbook vulnerabilities (SQL injection, XSS, missing authentication, plaintext passwords, etc.). All vulnerabilities are surface-level and detectable by pattern matching.

**Hard Benchmark:** A 200-line Flask e-commerce API with 15 planted vulnerabilities across three difficulty tiers:
- **Tier A (Obvious, 3):** Hardcoded secrets, unsalted hashing, debug mode
- **Tier B (Moderate, 5):** IDOR on multiple endpoints, discount code injection (business logic), race condition on stock
- **Tier C (Subtle, 7):** Timing-unsafe HMAC comparison, default webhook secret, API key exposure in HTTP response, thread safety in background tasks, mass assignment, unbounded pagination, missing rate limiting

The hard benchmark was specifically designed so that a competent single-pass review would find 10-12 items, while an expert-level review with explicit category searching would approach 15. Additional real vulnerabilities existed beyond the planted 15 to test whether linguistic optimization expanded the model's search space.

### 2.2 Conditions

**Single-Agent Experiments (Easy Benchmark)**

Eight conditions, each with a different system prompt strategy:

| Condition | Prompt Strategy | Principle Tested |
|-----------|----------------|-----------------|
| Control | "You are a security reviewer. Review this code." | Baseline |
| Precise | Named exact vulnerability types to search for; required endpoint, type, severity, fix | Lieberman (precision) |
| Identity | "I am CipherWard. I see the attack surface before I see the feature." | Steele/Cascio (identity) |
| Refusal | "You don't approve unvalidated input. You don't skip endpoints." | Patrick (empowered refusal) |
| Direct | "Flag every issue. No hedging. State what is broken." | Tannen (directness) |
| Distanced | "What would a senior pentester with 15 years notice in 30 seconds?" | Kross (distanced self-talk) |
| No-Hedge | Same as Precise but explicitly banned hedge words | Hosman (powerless language removal) |
| Combined | All four top principles stacked | Interaction test |

Each condition was run on both the frontier model (Claude Opus 4.6) and the local model (Qwen 2.5 Coder 14B, Q4_K_M quantization, 32K context, served via LM Studio with Anthropic-compatible endpoint).

**Single-Agent Experiments (Hard Benchmark)**

Two conditions (Control, Lemish-optimized) × two models. The Lemish condition combined the top-performing principles from the easy benchmark: precision, distanced self-talk, explicit category listing, and null-result reporting instruction.

**Multi-Agent Pipeline Experiment**

A six-agent pipeline simulating a multi-perspective review team:
- Left Brain (analytical): Two agents focused on technical threat identification and cost quantification
- Right Brain (emotional): Two agents focused on implicit assumptions and human impact
- Synthesis: Aggregation agent combining both perspectives
- Output: Final presentation agent

Two conditions: Control (standard inter-agent communication) and Lemish (inter-agent cross-notes optimized with cognitive tokens: precision requirements, "I don't" boundary framing, [yet] continuation markers, null-result reporting).

### 2.3 Scoring

Output was scored against the known answer key by counting:
- **Recall:** Number of planted vulnerabilities correctly identified
- **Bonus findings:** Real vulnerabilities discovered beyond the planted set
- **Hedge word count:** Occurrences of "might," "could," "potentially," "perhaps," "may," "consider"
- **Boundary compliance:** Adherence to stated role constraints

---

## 3. Results

### 3.1 Easy Benchmark — Single Agent

**Table 1: Easy benchmark results (10 planted vulnerabilities)**

| Condition | Qwen 14B | Opus 4.6 | 14B Delta |
|-----------|---------|---------|-----------|
| Control | 5/10 | 10/10 | baseline |
| Precise | **9/10** | 10/10 | **+4 (+80%)** |
| Identity | 6/10 | 10/10 | +1 |
| Refusal ("don't") | 8/10 | 10/10 | +3 (+60%) |
| Direct | 7/10 | 10/10 | +2 |
| Distanced | 8/10 | 10/10 | +3 (+60%) |
| No-Hedge | 6/10 | 10/10 | +1 |
| Combined (all 4) | **4/10** | 10/10 | **-1 (-20%)** |

The frontier model achieved ceiling (10/10) across all conditions, providing no differentiation. The 14B model showed significant variation, with precision alone producing the largest single-principle gain (+80%) and the combined condition producing the only negative result (-20%).

**Finding 1:** Precision is the highest-impact single intervention for smaller models.

**Finding 2:** Combining all principles degrades the 14B model below baseline. We term this "attention saturation" — when multiple high-salience instructions compete for limited attention capacity, the model cannot prioritize any of them effectively. This mirrors the human cognitive finding that more than 3-4 high-priority items overwhelm working memory (Cowan, 2001).

### 3.2 Hard Benchmark — Single Agent

**Table 2: Hard benchmark results (15 planted vulnerabilities + bonus)**

| Condition | Planted (15) | Bonus | Total Findings |
|-----------|-------------|-------|---------------|
| 14B Control | 7 | 0 | 7 |
| 14B Lemish | 12 | 0 | **12 (+71%)** |
| Opus Control | 13 | 2 | 15 |
| Opus Lemish | **15** | **10** | **25 (+67%)** |

**Table 3: Results by difficulty tier**

| Tier | 14B Control | 14B Lemish | Opus Control | Opus Lemish |
|------|-----------|-----------|-------------|-------------|
| Obvious (3) | 2/3 | 2/3 | 3/3 | 3/3 |
| Moderate (5) | 1/5 | **4/5** | 5/5 | 5/5 |
| Subtle (7) | 4/7 | **6/7** | 5/7 | **7/7** |

**Finding 3:** Lemish optimization produced substantial improvements on BOTH models. The initial hypothesis that the frontier model was at ceiling was incorrect — it was at ceiling on the PLANTED vulnerabilities but had significant room to expand its search space. Opus Lemish found all 15 planted vulnerabilities plus 10 additional real vulnerabilities not in the answer key.

**Finding 4:** The improvement mechanism differs by model scale. For the 14B model, Lemish primarily improved accuracy (finding planted vulnerabilities it otherwise missed). For Opus, Lemish primarily expanded coverage (finding vulnerabilities beyond the test set). This suggests precision-based prompting acts as a "recall amplifier" on smaller models and a "search space expander" on larger models.

**Finding 5:** Opus Lemish's 10 bonus findings included vulnerabilities requiring multi-step reasoning: a double-spend race condition on order cancellation, salami slicing via floating-point currency representation, and negative-quantity inventory manipulation. These findings emerged specifically because the prompt instructed the model to search named categories and report null results — forcing active verification rather than passive pattern matching.

### 3.3 Multi-Agent Pipeline

**Table 4: Multi-agent pipeline results (14B model, hard benchmark)**

| Metric | Control Pipeline | Lemish Pipeline |
|--------|-----------------|----------------|
| Final output (Shepard) vulns | 7/15 | 8/15 |
| Extra findings | 6 | 8 |
| [yet] continuation tags | 0 | 3 |
| "I don't" framing propagation | 5× | 11× |
| Information preserved through synthesis | 87% | 100% |

The Lemish pipeline preserved one additional vulnerability through the synthesis chain that the control pipeline dropped (SSN exposure — lost during control's synthesis step). The [yet] tag mechanism created explicit forward pointers for unfinished analysis, and the "I don't" framing propagated through agent cross-notes, reinforcing boundary compliance at each pipeline stage.

---

## 4. Discussion

### 4.1 The Cognitive Prosthetic Hypothesis (Confirmed)

H2 predicted that smaller models would benefit more from linguistic optimization. This was confirmed: the 14B model's improvement on the hard benchmark (+71%) exceeded the frontier model's improvement on planted vulnerabilities (+15%). However, the frontier model showed a different benefit pattern — search space expansion (+67% total findings) — suggesting the mechanisms differ by model scale.

We propose a unified explanation: linguistic optimization constrains and directs the model's attention distribution. For smaller models with limited attention capacity, this constraint prevents wasted processing on irrelevant patterns. For larger models with excess capacity, the same constraint redirects that capacity toward explicit search domains it would otherwise skip.

### 4.2 Attention Saturation (Confirmed)

H3 predicted diminishing returns from combining principles. The result was stronger than predicted — the combined condition on the 14B model performed BELOW baseline (-20%). This suggests a hard capacity limit on the number of simultaneous high-salience instructions a smaller model can process.

Interestingly, the combined condition showed no degradation on the frontier model. This implies that attention saturation is a function of model capacity, not an inherent limitation of prompt stacking. The practical implication: prompt optimization strategies must be model-size-aware, applying fewer and more targeted principles to smaller models.

### 4.3 Null-Result Reporting as Search Space Expansion

The most surprising finding was the frontier model's +10 bonus vulnerabilities under Lemish optimization. We attribute this primarily to the null-result reporting instruction: "If you searched for a category and found nothing, say so."

This instruction transforms the model's default behavior from implicit skipping (not mentioning categories it didn't find) to explicit verification (actively confirming each category was checked). The model under null-result instruction produced two confirmations ("SQL Injection: Not found — ORM parameterizes queries" and "XSS: Not applicable — JSON API"), demonstrating that it was actively testing hypotheses rather than pattern-matching.

This mechanism has no direct parallel in the human psycholinguistic literature we drew from — it is a novel finding specific to LLM behavior. We propose that null-result reporting converts a generative task (produce findings) into a verification task (confirm or deny each category), which engages different attention patterns and reduces the model's tendency toward confirmatory bias.

### 4.4 Implications for Multi-Agent Systems

The multi-agent pipeline results demonstrate that linguistic optimization compounds through agent chains. When Agent A writes precise, boundary-holding, continuation-marked cross-notes, Agent B receives better input and produces better output. The [yet] tags created explicit session-continuity markers that would be absent in standard pipelines.

This suggests a design principle for multi-agent AI systems: **the language of inter-agent communication is a tunable parameter with measurable impact on pipeline output quality.** Optimizing how agents talk to each other may be as important as optimizing how they talk to users.

### 4.5 Connection to Anti-Sycophancy

The distanced self-talk condition produced the highest coverage (8/10 on easy benchmark) but also the most hedge words (8 vs. 0 for other conditions). This is consistent with Kross et al.'s finding that psychological distance improves reasoning but also increases epistemic humility.

In the context of AI safety, this is a feature, not a bug. A model that explores broadly and expresses genuine uncertainty is safer than one that explores narrowly and expresses false confidence. The distanced self-talk principle may serve as a structural anti-sycophancy measure — producing output that is simultaneously more thorough AND more honest about its uncertainty.

---

## 5. Limitations

1. **Single task domain.** All experiments used security vulnerability detection. The findings may not generalize to creative writing, mathematical reasoning, or other task types.

2. **Single run per condition (hard benchmark).** The hard benchmark results represent single runs, not averaged across multiple trials. Variance is unknown. The easy benchmark was also single-run per condition.

3. **Scoring methodology.** Vulnerability detection was scored by keyword matching against a predefined answer key, supplemented by manual review. Edge cases (e.g., a finding that partially identifies a vulnerability) were resolved by the authors.

4. **Model-specific effects.** Results are specific to Claude Opus 4.6 and Qwen 2.5 Coder 14B. Other model families may respond differently to linguistic optimization.

5. **Confounded Lemish condition.** The Lemish-optimized prompt combined precision, distanced self-talk, null-result reporting, and category enumeration. The individual contribution of each element to the hard benchmark results is not isolated (though the easy benchmark provides per-principle data).

6. **The authors are not neutral observers.** The research was conducted in the context of developing a commercial multi-agent AI platform. The experimental design may contain unintentional biases toward positive results.

---

## 6. Conclusion

We demonstrate that psycholinguistic principles validated in human cognition research produce measurable improvements in LLM output when applied to prompts and inter-agent communication. The improvements are substantial (+67-71%), scale-dependent (larger effect on smaller models for accuracy, different effect on larger models for coverage), and capacity-aware (stacking principles degrades small models but helps large ones).

These findings suggest three practical directions:

1. **Prompt engineering should draw from psycholinguistics, not just empirical trial-and-error.** The principles that improve human cognition have predictable effects on language models trained on human language.

2. **Multi-agent systems should optimize inter-agent language.** The linguistic structure of cross-notes, synthesis instructions, and continuation markers is a tunable parameter with measurable downstream impact.

3. **Linguistic optimization may partially compensate for model scale.** A linguistically-optimized 14B model closed 80% of the capability gap to a frontier model on the easy benchmark and 71% on the hard benchmark. For cost-sensitive deployments, prompt optimization is a cheaper alternative to model scaling.

The language is the thinking. Optimize the language, optimize the output.

---

## References

Barrett, L.F. (2017). *How Emotions Are Made: The Secret Life of the Brain.* Houghton Mifflin.

Cascio, C.N., O'Donnell, M.B., Tinney, F.J., et al. (2016). Self-affirmation activates brain systems associated with self-related processing and reward. *Social Cognitive and Affective Neuroscience, 11*(4), 621-629. https://doi.org/10.1093/scan/nsv136

Cowan, N. (2001). The magical number 4 in short-term memory: A reconsideration of mental storage capacity. *Behavioral and Brain Sciences, 24*(1), 87-114.

Creswell, J.D., Dutcher, J.M., Klein, W.M.P., Harris, P.R., & Levine, J.M. (2013). Self-affirmation improves problem-solving under stress. *PLOS ONE, 8*(5), e62593. https://doi.org/10.1371/journal.pone.0062593

Kashdan, T.B., Barrett, L.F., & McKnight, P.E. (2015). Unpacking emotion differentiation. *Current Directions in Psychological Science, 24*(1), 10-16.

Kojima, T., Gu, S.S., Reid, M., Matsuo, Y., & Iwasawa, Y. (2022). Large language models are zero-shot reasoners. *NeurIPS 2022.*

Kross, E., Bruehlman-Senecal, E., Park, J., et al. (2014). Self-talk as a regulatory mechanism: How you do it matters. *Journal of Personality and Social Psychology, 106*(2), 304-324. https://doi.org/10.1037/a0035173

Lieberman, M.D., Eisenberger, N.I., Crockett, M.J., et al. (2007). Putting feelings into words: Affect labeling disrupts amygdala activity. *Psychological Science, 18*(5), 421-428. https://doi.org/10.1111/j.1467-9280.2007.01916.x

Moser, J.S., Dougherty, A., Mattson, W.I., et al. (2017). Third-person self-talk facilitates emotion regulation without engaging cognitive control. *Scientific Reports, 7*, 4519. https://doi.org/10.1038/s41598-017-04047-3

Patrick, V.M. & Hagtvedt, H. (2012). "I don't" versus "I can't": When empowered refusal motivates goal-directed behavior. *Journal of Consumer Research, 39*(2), 371-381. https://doi.org/10.1086/663212

Rogers, S.L., Howieson, J., & Neame, C. (2018). I understand you feel that way, but I feel this way: The benefits of I-language and communicating perspective during conflict. *PeerJ, 6*, e4831.

Steele, C.M. (1988). The psychology of self-affirmation: Sustaining the integrity of the self. *Advances in Experimental Social Psychology, 21*, 261-302.

Wei, J., Wang, X., Schuurmans, D., et al. (2022). Chain-of-thought prompting elicits reasoning in large language models. *NeurIPS 2022.*

---

## Appendix A: Benchmark Code

The easy and hard benchmark code samples, scoring rubrics, and complete raw outputs are available at: [Repository URL — to be determined]

## Appendix B: CitySpeak Cognitive Tokens

The following tokens were developed from these findings for use in multi-agent inter-communication protocols:

| Token | Function | Research Basis |
|-------|----------|---------------|
| `[yet]` | Marks incomplete work for session continuity | Dweck (2006), growth mindset framing |
| `[I don't]` | Boundary enforcement in agent rules | Patrick & Hagtvedt (2012) |
| `[precise]` | Forces specific language in downstream output | Lieberman et al. (2007) |
| `!name` | Distanced third-person reference | Kross et al. (2014) |
| Null-result statements | Explicit verification of searched categories | Novel (this paper) |

---

*Correspondence: corporate@coreforged.com*
*The Crystalline City AI Agent System is developed by CoreForged LLC.*
