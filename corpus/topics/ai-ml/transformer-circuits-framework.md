---
title: "A Mathematical Framework for Transformer Circuits"
author: "detroit.dev community"
date: 2026-03-31
tags: [ai, transformers, interpretability, mechanistic-interpretability, circuits]
source: "https://transformer-circuits.pub/2021/framework/index.html"
---

# A Mathematical Framework for Transformer Circuits

Notes on the Anthropic paper by Elhage, Nanda, Olsson et al. (2021).

## Key ideas

- **Residual stream as communication channel** — every layer reads from and writes to the residual stream. It's deeply linear: no privileged basis, supports arbitrary linear transforms.
- **Attention heads are independent** — each head reads/writes independently to the residual stream. The "concatenate and multiply" formulation is just a computational shortcut.
- **OV and QK circuits** — each attention head has two separable circuits:
  - **QK circuit** (`W_E^T W_QK W_E`): determines which tokens attend to which
  - **OV circuit** (`W_U W_OV W_E`): determines what happens to logits when a token is attended to
- **Path expansion** — you can expand the transformer computation into a sum of end-to-end paths, each independently interpretable.

## Model complexity by depth

| Layers | Behavior |
|--------|----------|
| 0 | Bigram statistics only (next token from current token) |
| 1 | Skip-trigrams: "A... B → C" patterns. Attention heads mostly do copying. |
| 2 | Composition of attention heads enables **induction heads** — a general in-context learning algorithm. |

## Induction heads

The breakthrough finding: two-layer models develop **induction heads** that implement a simple but powerful algorithm:

```
[a][b] ... [a] → [b]
```

"If I've seen token A followed by token B before, and I see A again, predict B."

This works via **K-composition**: a first-layer "previous token" head shifts key vectors back one position, and a second-layer head matches the current token against those shifted keys.

This even works on random token sequences (completely off-distribution), because the algorithm doesn't depend on learned token statistics.

## Skip-trigram "bugs"

Because one-layer models represent skip-trigrams in factored form (OV × QK), they can't capture three-way interactions. If a head learns both:
- `keep... in → mind`
- `keep... at → bay`

It must also increase probability of `keep... in → bay` and `keep... at → mind`. These are structural limitations of the architecture, not training failures.

## Relevance to larger models

The authors are careful to note these findings come from tiny attention-only models. But they argue:
- Attentional circuits exist in full models too (even with MLP layers)
- Induction heads appear in much larger models
- The mathematical framework (path expansion, virtual weights) generalizes

## Open questions (from the paper)

- How do MLP layers work? (Neurons are mostly polysemantic — superposition hypothesis)
- Do "virtual attention heads" (V-composition) matter at scale?
- Can we formalize "copying matrix" detection better than eigenvalue statistics?

## Links

- [Paper](https://transformer-circuits.pub/2021/framework/index.html)
- [Follow-up on induction heads](https://transformer-circuits.pub/2022/in-context-learning-and-induction-heads/index.html)
- [Toy Models of Superposition](https://transformer-circuits.pub/2022/toy_model/index.html)
