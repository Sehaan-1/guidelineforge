# GuidelineForge — Support Ticket Annotation Guidelines
## Version 1.0 — Effective 2026-06-29 (Round 1 production labeling)

| Field | Value |
|---|---|
| Project | GuidelineForge — customer support intent + sentiment tagging |
| Task owner | Annotation Lead |
| Labeling tool | Label Studio (export: `ticket_id, intent_label, sentiment_label`) |
| Labels per ticket | exactly **1 intent** + **1 sentiment** |
| Quality gate | ≥ 85% vs. adjudicated labels on the 48-ticket calibration set before production labeling |

---

## 1. Task

Each ticket is a short customer message to an e-commerce support desk. For
every ticket you assign:

1. **Intent (categorical, 8 classes)** — the *primary* thing the customer
   wants from us.
2. **Sentiment (ordinal, 3 levels)** — the customer's emotional polarity
   toward the company: `negative`, `neutral`, `positive`.

Do not skip tickets. If uncertain, choose your best label and add the
`uncertain` flag in the comment field.

---

## 2. Intent taxonomy

| Class | Definition | Include | Exclude |
|---|---|---|---|
| `refund_request` | Customer wants money returned (refund, reimbursement, chargeback, money-back status) | refund requests, refund-status chases, compensation demands | questions *about* refund policy (see `other_contact`) |
| `cancellation` | Customer wants an order or subscription cancelled, or asks about cancellation fees | cancel order, early-exit/termination fee questions | delivery rescheduling (→ `shipping_delivery`) |
| `billing_payments` | Problems or questions about charges, invoices, payment methods | duplicate/wrong charges, invoice download, accepted cards | refund of a paid amount (→ `refund_request`) |
| `shipping_delivery` | Delivery status, shipping options, address changes, late/lost packages | tracking, "where is my package", change delivery address | order modification (→ `order_changes`) |
| `order_changes` | Placing an order or changing its contents | add/remove items, edit quantity, "help me buy" | pure delivery issues |
| `account_access` | Account, login, password, registration, profile changes | reset PIN, can't log in, change email address | payment problems (→ `billing_payments`) |
| `feedback_complaints` | Ticket exists to give an evaluation of us — reviews, formal complaints, claims | "I want to leave a review", formal consumer claims | a service request expressed angrily (see §4 rule 4) |
| `other_contact` | Everything else: reach a human, newsletter subscription, policy questions | contact requests, unsubscribe, "what is your refund policy?" | anything matching another class |

---

## 3. Sentiment scale

| Label | Anchor | Signals |
|---|---|---|
| `negative` | Customer is expressing displeasure | insults, profanity, threats to leave/dispute, ALL-CAPS anger, explicit emotion words ("furious", "frustrated", "angry") |
| `neutral` | No emotional signal either way | plain factual requests and questions |
| `positive` | Customer expresses approval or gratitude | "thanks", praise, friendly tone markers ("love the new site") |

Score what is **on the page**, not what you would feel.

---

## 4. Annotation rules

**R1 — Single primary intent.** Every ticket gets exactly one intent. If a
ticket contains more than one request, pick the one mentioned **first**.

**R2 — Policy curiosity is not a transaction.** Questions *about* a policy
(e.g., "how does your money-back guarantee work?") are `other_contact`, not
the corresponding action class.

**R3 — Sentiment is about the company**, not the situation. A customer calmly
reporting a broken product, without emotional language, is `neutral`.

**R4 — Tone-first rule.** If a ticket is primarily an *expression of
dissatisfaction* — using strong complaint language (e.g., *joke, ridiculous,
unacceptable, pathetic, scam, worst, nightmare, furious, outrageous, useless,
sick of, fed up*) — label it `feedback_complaints`, **even if** a service
request is also present in the same ticket.

**R5 — Politeness is neutral.** Courteous phrasing ("would you mind…",
"could someone explain…") signals `neutral` sentiment, regardless of topic.

**R6 — Length doesn't change the rule.** Very short tickets ("Where's my
money?") are labeled by best inference from the words present.

**R7 — Flag, don't guess wildly.** If genuinely torn between two classes,
choose the better fit and set `uncertain=true` in comments.

---

## 5. Worked examples

> **T-ex1** — "I want to cancel order #4821133"
> Intent: `cancellation` (explicit cancel request). Sentiment: `neutral` (no emotion words).

> **T-ex2** — "would you mind telling me why my delivery is three days late?"
> Intent: `shipping_delivery`. Sentiment: `neutral` (**R5**: courteous phrasing).

> **T-ex3** — "Your refund policy is a joke — I want my $40 back today. Refund order #7752921."
> Intent: `feedback_complaints` (**R4**: strong complaint language dominates the
> ticket; the refund request is enclosed in the complaint). Sentiment: `negative`.

> **T-ex4** — "Oh great, my card got charged twice again. Exactly what I needed today."
> Intent: `billing_payments`. Sentiment: `positive` (explicit positive words:
> "great", "exactly what I needed" — **R3/R5**: score what is on the page).

> **T-ex5** — "Cancel my order #3045073 and refund the $120 to my card today."
> Intent: `cancellation` (**R1**: cancellation mentioned first). Sentiment: `neutral`.

> **T-ex6** — "do ya deliver to {{Delivery City}}"
> Intent: `shipping_delivery`. Sentiment: `neutral`.

---

## 6. Process

- **Calibration (day 1):** all annotators label the same 48-ticket set,
  blind. Disagreements are discussed with the lead; individual calibration
  accuracy must be ≥ 85% vs. the lead's adjudicated labels before you touch
  production data.
- **Production:** 4 weekly batches (B1–B4) of 150 tickets each, assigned
  per-annotator. Paste your labels into the shared export nightly.
- **Gold checks:** unbeknownst to annotators, ~12% of items are from the
  gold-standard set; weekly accuracy vs. gold is monitored by the lead and
  auditors. Falling below 90% triggers retraining.
- **Questions:** ask in #annotation-help; do not resolve ambiguity by DM
  consensus with other annotators (that destroys independence).

*End of v1.0. See v2.0 for the revision issued after Round-1 agreement analysis.*
