# ReAct vs. Reflexion: Agent Reasoning and Feedback Loops

## 1. The Core Distinction in One Line

**ReAct** builds a feedback loop *inside* a single episode (thought → action → grounded observation → revised thought). **Reflexion** builds a feedback loop *across* episodes (trajectory → scalar reward → verbal self-reflection → persistent memory → new trial). They operate at different temporal granularities, which is why they are complementary rather than competing — Reflexion actually lists ReAct as one of its Actor instantiations.

## 2. How Each Handles Reasoning

**ReAct** augments the agent's action space to `Â = A ∪ L`, where a *thought* `ât ∈ L` explicitly "does not affect the external environment, thus leading to no observation feedback." A thought exists only to compose useful information from the current context and update it (`c_{t+1} = (c_t, ât)`) so that future reasoning or acting is better supported. Reasoning thus serves two directions simultaneously: **"reason to act"** (create, maintain, and adjust high-level plans) and **"act to reason"** (query an external source to ground the reasoning). The paper's motivation is a critique of chain-of-thought as "a static black box... not grounded in the external world," which "can lead to issues like fact hallucination and error propagation."

**Reflexion** does not prescribe a reasoning format at all. Its Actor "is built upon a large language model... specifically prompted to generate the necessary text and actions," and the authors "explore various Actor models, including Chain of Thought and ReAct." Reasoning quality inside a trial is therefore inherited from the Actor; Reflexion's contribution is what happens *after* the trial fails.

## 3. Comparative Matrix

| Dimension | ReAct (Yao et al., ICLR 2023) | Reflexion (Shinn et al., 2023) |
|---|---|---|
| Central thesis | Synergize reasoning and acting by generating interleaved thoughts and actions | Reinforce agents "not by updating weights, but instead through linguistic feedback" |
| Loop scope | Intra-episode (single trajectory) | Inter-episode (iterative across trials) |
| Loop structure | Thought → Action → Observation → Thought … until answer/termination | Actor trajectory → Evaluator score → Self-Reflection → Memory → next trial, repeating until Evaluator deems the trajectory correct |
| Reasoning format | Prescribed: free-form verbal reasoning traces in the thought space L | Not prescribed; delegated to the Actor (CoT, ReAct, etc.) |
| Feedback source | External environment observations (e.g., Wikipedia API); grounded | Evaluator reward — exact-match grading, hand-written heuristics, or a separate LLM instance; can be external or internally simulated |
| Feedback granularity | Raw observation text, consumed automatically | Sparse scalar reward first *amplified* into nuanced natural-language feedback |
| Memory | Working memory only — the growing context `c_t`; no persistence beyond the episode | Dual memory: short-term (trajectory history) + long-term (self-reflection outputs), bounded to Ω ≈ 1–3 experiences for context limits |
| Self-correction mechanism | In-trace exception handling and plan adjustment; optional human "thought editing" on the fly | Explicit Self-Reflection model that states, e.g., action `a_i` caused `a_{i+1}` and `a_{i+2}` to fail and that it should have taken `a'_i` |
| Learning substrate | Few-shot in-context prompting (1–6 examples) plus optional finetuning | Weight-free verbal reinforcement with in-context episodic memory; no finetuning |
| Primary reported results | ALFWorld 71% vs Act 45% vs BUTLER 37%; +34% absolute on ALFWorld, +10% on WebShop; Fever 60.9 vs CoT 56.3; HotpotQA 27.4 vs CoT 29.4 | +22% ALFWorld, +20% HotpotQA, +11% HumanEval; 91% pass@1 HumanEval vs GPT-4 80% |
| Acknowledged weakness | Structural constraint on reasoning reduces flexibility; repetitive thought-action loops; non-informative search = 23% of error cases and "derails the model reasoning" with hard recovery | Depends on the quality of the Evaluator signal; memory must be truncated, so long-horizon lessons may be evicted |

## 4. Three Analytical Observations

**(a) ReAct's weakness is precisely Reflexion's target.** ReAct's own error analysis concedes that when search returns non-informative results, the agent has "a hard time to recover and reformulate thoughts," and it documents a repeating thought-action failure pattern categorized as "reasoning error." Reflexion reports the complementary finding that "a ReAct-only agent converging at a hallucination rate of 22% with no signs of long-term recovery," with gains halting between trials 6 and 7. The same benchmark gap is described from both sides.

**(b) The feedback signals are not the same kind of object.** ReAct's feedback is *semantic and immediate* — the observation text itself is the correction. Reflexion's feedback is *evaluative and deferred* — a scalar `r_t` must first be inflated into language by the Self-Reflection model, because scalar rewards alone are unusable by an LLM as an improvement signal. Reflexion's stated aim is that this feedback be "more informative than scalar rewards."

**(c) Composability, not substitution.** Reflexion's ALFWorld setup explicitly uses ReAct as the action generator, "as Yao et al. has shown success in long trajectory decision making using explicit intermediate thoughts," and adds an Evaluator heuristic that triggers reflection when "the agent executes the same action and receives the same response for more than 3 cycles, or if the number of actions taken... exceeds 30." This is a direct patch for the exact looping and inefficient-planning failures ReAct documents. In short: ReAct supplies *grounded reasoning within a trial*; Reflexion supplies *learning between trials*.

## 5. References

- Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., & Cao, Y. (2023). *ReAct: Synergizing Reasoning and Acting in Language Models.* ICLR 2023. https://arxiv.org/abs/2210.03629
- Shinn, N., Cassano, F., Berman, E., Gopinath, A., Narasimhan, K., & Yao, S. (2023). *Reflexion: Language Agents with Verbal Reinforcement Learning.* https://github.com/noahshinn024/reflexion

---

**Operational note:** my first two scoped `knowledge_retriever` calls failed with backend errors (`'RustBindingsAPI' object has no attribute 'bindings'` and a Chroma path error). I retried unscoped, which succeeded, then re-ran scoped Hop-2 queries that worked normally. All quoted material above is drawn from retrieved chunks, not from outside knowledge. Full working notes are saved at `/workspace/comparison_notes.md`, and the comparison has been committed to memory.