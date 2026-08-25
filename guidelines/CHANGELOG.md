# Guideline changelog — v1.0 → v2.0

Every revision below is driven by a measured disagreement pattern from
Round 1 (guidelines v1.0, 2026-06-29 → 2026-07-24). Statistics are
computed from the raw labels in `data/annotations/` by
`src/simulate_pipeline.py`; nothing here is hand-estimated.

## Method in one paragraph

Round 1 labeled 600 tickets (180-ticket blind triple-overlap for IAA,
72 embedded gold items, 48-item calibration set). Agreement analysis
(Fleiss' κ, Krippendorff's α, per-class one-vs-rest κ, slice-level
unanimous rates) showed an *acceptably high overall* intent κ (0.83)
that concealed catastrophic disagreement on specific ticket families —
and, worse, one family where annotators **agreed with each other while
being wrong**. v2.0 targets exactly those five failure modes.

---

## C1 — DELETED the "tone-first" rule (v1 R4)

**Signal.** The 16 anger-framed action requests ("Your refund policy is
a joke — I want my $40 back today. Refund order #…") were **75%
unanimous** across the three annotators, yet only **25% of labels
matched design intent** (refund/cancel). Annotators were faithfully
applying a bad rule: v1 R4 said strong complaint language pulls the
ticket to `feedback_complaints`. This family is the project's canonical
demonstration that **high IAA does not equal correctness** — agreement
metrics alone would have waved these through; the gold set caught them.

**Effect validated in R2.** Anger-framed family: intent unanimous
75% → 81%, per-annotator gold intent accuracy 0.85–0.89 → 0.96–0.99.

## C2 — Replaced "first request mentioned" with a precedence hierarchy

**Signal.** Mixed-intent tickets (18 tickets, "Cancel order #… and
refund the $…") had **12% unanimous agreement, Fleiss' κ = 0.03 —
chance level**. The three annotators each used a different defensible
tie-break (first mention / money-mention / keyword-count). Per-class κ
for `cancellation` was the worst of the taxonomy at **0.58**.

**Effect validated in R2.** Mixed-intent intent κ 0.03 → 0.87;
unanimous 12% → 94%. Per-class κ: `cancellation` 0.58 → 0.91,
`refund_request` 0.79 → 0.96.

## C3 — New sarcasm/contrast rule for sentiment (v2 R8)

**Signal.** Sarcastic tickets ("Oh great, my card got charged twice
again") produced the lowest sentiment agreement of any slice:
**30% unanimous, κ = 0.25**. The split ran along reading style —
literal readers scored the positive words, context readers scored the
reported failure. v1 never mentioned sarcasm.

**Effect validated in R2.** Sarcasm sentiment unanimous 30% → 80%,
κ 0.25 → 0.57. Still the hardest family; flagged for v2.1 (more worked
examples).

## C4 — Rewrote the politeness rule (v1 R5)

**Signal.** Polite complaints about stated failures ("Would you mind
telling me why my delivery is three days late?") split **54% unanimous,
κ = 0.25**: v1 R5 said politeness ⇒ neutral, but some annotators read
the stated failure. The rule created the split it was meant to prevent.

**Effect validated in R2.** Polite-complaint sentiment unanimous
54% → 77%, κ 0.25 → 0.73.

## C5 — New short-fragment rule (v2 R9)

**Signal.** Ultra-short tickets (≤6 words) had sentiment agreement at
**κ = −0.05** (below chance) with no anchor rule at all in v1.

**Effect validated in R2.** Fragment sentiment unanimous 43% → 71%,
κ −0.05 → 0.60. Improvement, but still below target — v2 rules get
annotators *most* of the way on fragments; agreement here is capped by
genuine ambiguity (documented as a known limitation in the case study).

---

## Cross-check: what the revision did to production economics

| Metric | v1.0 era | v2.0 era |
|---|---|---|
| Share of production intents the revised rules would have re-routed | 4.8% | — |
| Share of production sentiments the revised rules would have corrected | 14.5% | — |
| Tier-2 rework rate (intent) | — | 1.7% |
| Tier-2 rework rate (sentiment) | — | 3.3% |
| Tier-3 audit pass rate (n=117) | — | 100% |

A rework rate comfortably under the 15–20% industry ceiling in Round 2
is itself evidence the revision addressed *instruction* problems rather
than *annotator* problems — the right fix for a >30% rework world would
have been rewriting guidelines, exactly what v2.0 was.
