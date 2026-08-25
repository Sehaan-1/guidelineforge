# Case study — GuidelineForge

*How a measured disagreement loop turned a mediocre annotation program into
an audited, gold-verified one — in nine weeks.*

---

## The situation

A data team needed 600 customer-support tickets labeled on two axes: **intent**
(8 classes) for routing automation, and **sentiment** (ordinal 3-level) for
escalation triage. Three annotators were available; Round 1 shipped under a
carefully-written guideline document (v1.0) with a certification gate at
kickoff — 48 blind tickets, ≥85% vs. adjudicated labels required before
anyone touched production. Two of three annotators failed the first gate
attempt and were coached through before Week 1 began.

Volume is not the hard part of this job. The hard part is that **you cannot
see label quality by looking at the output** — labels look like labels
whether they encode the right rule or a defensible misreading of it.

## What I did

I ran Round 1 as an instrumented program, not a labeling sprint: a 180-ticket
**blind triple-overlap** as the IAA measurement set, a 72-item **gold set**
embedded invisibly in the stream, and per-week batch metrics. Instead of
eyeballing overall agreement, I computed the full battery from scratch —
Cohen's κ per pair, Fleiss' κ for the trio, Krippendorff's α (ordinal for
sentiment, so a negative-vs-positive flip costs more than a near-miss),
per-class one-vs-rest κ, and slice-level unanimity — validated against
scikit-learn/NLTK first.

**Round-1 overall intent κ = 0.83 looked green. The slice map showed a fire:**

- mixed-intent tickets at **κ = 0.03 — chance level, 12% unanimity**;
- sarcasm sentiment at **κ = 0.25, 30% unanimity**;
- `cancellation` the weakest class at **per-class κ = 0.58**.

And the gold set showed something agreement statistics could not: on
**anger-framed action requests** ("Your refund policy is a joke — I want my
$40 back today"), the team was **75% unanimous and only 25% correct**. v1's
"tone-first" rule (R4) told annotators that strong complaint language means
`feedback_complaints` — and they all obeyed, together, wrongly. The most
*diligent* annotator had the *worst* gold intent accuracy. Diligence
executes a flawed rule flawlessly.

The confusion matrix named the mechanism: off-diagonal mass concentrated on
`cancel ⇄ refund ⇄ billing` — a **tie-breaking defect**, not a taxonomy
defect. So the fix was not more classes and not more annotator training.

## The intervention — guideline v2.0

Five evidence-targeted changes, each traced to a measurement:

1. **Deleted R4.** Action requests outrank complaint framing, always.
2. **Precedence hierarchy** for multi-intent tickets (refund > cancel >
   billing > shipping > …), replacing "first one mentioned".
3. **Sarcasm rule:** judge the event reported, not the valence of the words.
4. **Polite-failure rule:** a stated service failure is negative, even in
   courteous packaging.
5. **Short-fragment rule** for ≤6-word tickets.

Then recertification (all three ≥ 97% on the gate) and a blind Round 2 on
the same 600 tickets.

## Results

| | Round 1 | Round 2 |
|---|---:|---:|
| Fleiss' κ — intent | 0.835 [CI 0.78–0.88] | **0.955** [CI 0.93–0.98] |
| Fleiss' κ — sentiment | 0.668 | **0.878** |
| Krippendorff α — sentiment (ordinal) | 0.610 | **0.885** |
| Mixed-intent slice κ (intent) | 0.03 | **0.87** |
| Sarcasm slice unanimity (sentiment) | 0.30 | **0.80** |
| Best annotator gold intent accuracy | 0.889 | **0.986** |
| Rework rate (either task) | — | **4.7%** (ceiling 15–20%) |
| Tier-3 audit pass (n=117) | — | **100%** |
| **Final labels vs gold** | — | **1.000 intent / 0.958 sentiment** |

A counterfactual against Round-1 production labels showed the revision
matter-of-factly re-routes **4.8% of intents** and corrects **14.5% of
sentiments** that v1 would have shipped.

## What I take from it

- **IAA is a smoke detector, not a fire extinguisher.** Low agreement tells
  you *where* to read your guidelines; it can't tell you the labels are right.
- **Gold sets catch what consensus cannot.** 75%-unanimous wrongness is the
  most dangerous failure mode in annotation, and it's invisible without a
  reference.
- **Guidelines are code.** Version them, changelog them, drive revisions
  from measured disagreement, and never change them mid-round.
- **A rework spike is an instruction bug, not a people bug.** The fix
  hierarchy runs instructions → calibration → people, in that order.

## Resume-ready version

> Designed and ran a 600-ticket, 3-annotator labeling program (8-class intent
> + ordinal sentiment) with blind-overlap IAA measurement, embedded gold
> standards, and a 3-tier QA review. Diagnosed guideline ambiguity behind
> chance-level agreement on mixed intents (κ = 0.03) and unanimous-but-wrong
> labeling on anger-framed requests; revised the guidelines and lifted
> Fleiss' κ on intent from 0.83 to 0.96 and ordinal α on sentiment from
> 0.61 to 0.89, closing at 1.00/0.96 gold-verified accuracy, 4.7% rework,
> 100% audit pass.

*Disclosure: annotator passes are transparent, documented persona
simulations — the methodology, measurements and revision loop are fully real
and recomputable from raw labels; the same pipeline ingests live peer labels
unchanged (`data/for_peer_annotation/`).*
