# GuidelineForge — Support Ticket Annotation Guidelines
## Version 2.0 — Effective 2026-08-03 (Round 2 production labeling)

| Field | Value |
|---|---|
| Supersedes | v1.0 (2026-06-29) — see `CHANGELOG.md` for the evidence behind every change |
| Trigger for revision | Round-1 IAA analysis on the 180-ticket blind overlap: overall intent Fleiss' κ = 0.83 (acceptable), but sentiment κ = 0.67, and the contested slices ran at **κ ≤ 0.25** (mixed-intent intent κ = 0.03, sarcasm sentiment κ = 0.25), plus a systematic gold mismatch on anger-framed requests (75% unanimous, only 25% matching design intent) |

---

## 1. What changed (summary)

| # | v1.0 rule | v2.0 rule | Why |
|---|---|---|---|
| 1 | **R4 tone-first**: strong complaint language ⇒ `feedback_complaints` | **DELETED.** Action requests always outrank complaint framing | Round-1: all 3 annotators applied R4 to the same anger-framed refund/cancel tickets — 75% unanimous but only 25% of labels matched design intent. Agreement ≠ correctness; the rule, not the annotators, was wrong |
| 2 | **R1**: ties broken by "first request mentioned" | **Explicit precedence hierarchy** (§4, R1) | Mixed-intent slice: unanimous agreement 12%, Fleiss' κ = 0.03 (chance level); per-class κ for `cancellation` = 0.58 |
| 3 | *(no sarcasm rule)* | **R8 sarcasm/contrast rule** for sentiment | Sarcasm slice: sentiment unanimous 30%, κ = 0.25 — the lowest of any slice |
| 4 | **R5**: courteous phrasing ⇒ `neutral` | **R5 rewritten**: stated service failure ⇒ `negative` regardless of politeness | polite_complaint slice: sentiment unanimous 54%, κ = 0.25 — split exactly along the old rule's fault line (literal neutral vs. empathetic negative) |
| 5 | — | **R9 short-fragment rule** | short_fragment slice: sentiment κ = −0.05 (below chance), no anchor rule existed |

---

## 2. Intent taxonomy

*(Definitions unchanged from v1.0 — the taxonomy was validated; the disagreement was in the tie-breaking rules, not the class boundaries.)*

`refund_request`, `cancellation`, `billing_payments`, `shipping_delivery`,
`order_changes`, `account_access`, `feedback_complaints`, `other_contact`.

---

## 3. Sentiment scale

Unchanged: `negative` < `neutral` < `positive` (ordinal).

---

## 4. Annotation rules

**R1 — Primary intent by precedence hierarchy.** When a ticket contains more
than one request, pick the class **highest** in this list:

1. `refund_request` (money-out has the highest business impact)
2. `cancellation`
3. `billing_payments`
4. `shipping_delivery`
5. `order_changes`
6. `account_access`
7. `feedback_complaints`
8. `other_contact`

Mention order no longer matters. *Rationale: for triage and routing, a refund
hidden inside a cancellation ticket is the action with the highest cost of
being missed.*

**R2 — Policy curiosity is not a transaction.** *(unchanged)* Questions *about*
a policy are `other_contact`, not the action class.

**R3 — Sentiment is about the company.** *(unchanged)*

**~~R4 — tone-first~~ DELETED.** Anger no longer pulls a ticket into
`feedback_complaints`. `feedback_complaints` is now restricted to tickets whose
*only* actionable content is an evaluation (writing a review, filing a formal
claim). An angrily-worded refund request is a `refund_request`.

**R5 — Service failures are negative, even when polite.** If the ticket
*states* that something went wrong (late delivery, double charge, missing
refund, broken login…), sentiment = `negative`, regardless of courteous
phrasing. Courteous phrasing with **no stated failure** (pre-sale questions,
how-do-I requests) remains `neutral`.

**R6 — Length doesn't change the rule.** *(unchanged)*

**R7 — Flag, don't guess wildly.** *(unchanged)*

**R8 — Sarcasm rule (new).** Judge sentiment by the **event reported**, not
the valence of individual words. Positive wording combined with a stated
failure ("Oh great, my card got charged twice again") is `negative`.
Diagnostic cues: positive word + failure statement, "again", phrases like
*exactly what I needed, you never disappoint, top-notch*.

**R9 — Short-fragment rule (new).** Fragments are labeled by their most
direct reading: "Where's my money?" → `refund_request` / `negative`;
"Charged twice??" → `billing_payments` / `negative`; "Speak to someone
please" → `other_contact` / `neutral`. Punctuation and fragments like
"Package. Late. Again." carry frustration → `negative` when a failure is
stated.

---

## 5. Worked examples (v2 re-answers to v1's contentious cases)

> **T-ex3 (revised)** — "Your refund policy is a joke — I want my $40 back today. Refund order #7752921."
> Intent: `refund_request` (**new R1**: money-out precedence; ~~R4~~ deleted). Sentiment: `negative`.

> **T-ex4 (revised)** — "Oh great, my card got charged twice again. Exactly what I needed today."
> Intent: `billing_payments`. Sentiment: `negative` (**R8**: sarcasm — the event is a double charge).

> **T-ex2 (revised)** — "would you mind telling me why my delivery is three days late?"
> Intent: `shipping_delivery`. Sentiment: `negative` (**new R5**: service failure stated).

> **T-ex5 (revised)** — "Cancel my order #3045073 and refund the $120 to my card today."
> Intent: `refund_request` (**new R1** precedence), not `cancellation`. Sentiment: `neutral`.

> **T-ex7 (new)** — "Still no package."
> Intent: `shipping_delivery`. Sentiment: `negative` (**R9**: fragment stating a failure).

> **T-ex8 (new)** — "is it possible to list ur accepted payment modalities?"
> Intent: `billing_payments`. Sentiment: `neutral` (**old R5** behavior preserved: no failure stated).

---

## 6. Process (unchanged mechanics, tightened gates)

- **Recertification (2026-08-03):** every annotator re-labels the calibration
  set under v2.0; ≥ 85% agreement with adjudicated v2 labels required before
  Round 2. (All three annotators passed at 98% on the combined task; at the
  Round-1 kickoff gate, only the most careful annotator passed on the first
  attempt — see `calibration_notes.md`.)
- **Production:** same 4-batch schedule, same tickets re-labeled **blind** —
  notebooks from Round 1 are not visible during Round 2 labeling.
- **Gold checks:** unchanged (12% embedded gold, weekly accuracy monitoring,
  90% floor).
- **Guideline feedback loop:** annotators file edge cases in
  #annotation-help; the lead triages weekly and batches clarifications into
  guideline version bumps — no ad-hoc rule changes mid-round.

*End of v2.0.*
