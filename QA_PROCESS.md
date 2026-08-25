# QA process writeup — tiered review workflow

GuidelineForge runs the same three-tier structure production annotation
vendors use, because single-pass review is structurally incapable of
catching the two failure classes that matter: random slips *and*
systematic rule misreads.

```
Pass 1 (Tier 1)  annotator labeling      600 tickets/round
Pass 2 (Tier 2)  senior review           100% of production labels +
                                         all non-unanimous overlap tickets
Pass 3 (Tier 3)  auditor spot-check      20% stratified sample of finals
                 + weekly gold-set accuracy tracking per annotator
```

## Tier 1 — raw annotation

- **Overlap (n=180):** every ticket labeled by all three annotators,
  blind. This is the IAA measurement set (calibration 48 + gold 72 +
  60 stratified extras).
- **Production (n=420):** one primary annotator per ticket
  (round-robin). Between rounds the assignment rotates, so nobody
  re-labels their own Round-1 ticket in Round 2.
- Embedded quality tripwires: 72 gold items (12%) mixed into both, so
  gold accuracy can be tracked weekly without annotation pauses.

## Tier 2 — senior review

| What was reviewed | Volume |
|---|---|
| Round-2 production labels (100% review — post-revision policy) | 420 |
| Round-2 overlap tickets without unanimity | 29 of 180 |

Reviews correct against the **adjudicated reading of v2.0**, not
against the reviewer’s personal preference — reviewer decisions must
cite a rule (R1 precedence, R5, R8, R9…), which keeps "senior taste"
out of the label stream.

**Rework rates (Round 2):**

| Measure | Rate | Industry bar |
|---|---|---|
| intent — all labels | 1.7% | < 15–20% healthy |
| intent — production only | 2.4% | |
| sentiment — all labels | 3.3% | |
| sentiment — production only | 4.5% | |
| either task | 4.7% | |

Per-class rework concentrates in `account_access` (6.1%) and
`other_contact` (3.1%) — organic keyword-thin tickets, no rule fixes
indicated. A rework rate **above ~30% would be treated as an
instruction-system failure**, not an annotator failure, and would
trigger guideline revision rather than retraining — that is precisely
the judgment call this project exercises in reverse (Round 1 → v2.0
*was* the revision event).

## Tier 3 — audit

- **Sample:** 120 target, 117 drawn (20%, stratified by final intent
  class, 15/class; three classes had <15 candidates after rounding).
- **Reference:** gold set where the audited ticket is gold (21 items);
  otherwise an *independent re-derivation* of the v2 rules.
- **Result:** 100% pass rate; zero audit failures.
- **Final label quality vs. gold (all 72):** intent **1.000**,
  sentiment **0.958** — the program's deliverable label stream meets a
  ≥0.90 ground-truth accuracy bar.

## Edge cases resolved (and how)

**The five rule-drivers** — Round-1 disagreement/split → rule cited in
v2.0 → Round-2 verdict (all labels from `data/annotations/` and
`data/adjudicated_labels.csv`):

| Ticket | Text (truncated) | Round-1 reality | v2 rule | Round-2 final |
|---|---|---|---|---|
| GF-0370 | "This is ridiculous. Refund my card for order #3045073 NOW." | A1/A2 `feedback_complaints`, A3 `billing_payments` | R1 precedence outranks deleted R4 | `refund_request` / `negative`, unanimous |
| GF-0202 | "Cancel order #9351146 immediately and I expect a full refund of $64.2." | A1 `cancellation`, A2 `refund_request`, A3 `cancellation` | R1: refund > cancellation | `refund_request` / `neutral`, unanimous |
| GF-0129 | "Fantastic service as always: the app crashes every time I log in." | intent agreed; sentiment A2 negative, A1/A3 neutral | R8 sarcasm: judge the event, not the words | `account_access` / `negative`, unanimous |
| GF-0463 | "I'm slightly worried: my delivery shows no movement for six days." | sentiment split neutral/negative | R5: stated failure is negative even when polite | `shipping_delivery` / `negative`, unanimous |
| GF-0249 | "i cannot check ur money back guarantee" | intent agreed `refund_request`; **design intent is `other_contact`** | R2 policy gate needs a question mark; the ticket has none | still `refund_request` — **logged as known gap, candidate for v2.1** (statement-form policy questions) |

**Actual Tier-2 rework events** (sample of the 28 labels changed in
Round-2 review):

| Ticket | Text (truncated) | First pass | Final | Rule cited |
|---|---|---|---|---|
| GF-0291 | "Brilliant — I still don't have my refund. You never disappoint." | `refund_request` / `positive` | `refund_request` / `negative` | R8 sarcasm override |
| GF-0204 | "how do I see your money back policy?" | `refund_request` / `neutral` | `other_contact` / `neutral` | R2: policy curiosity is not a transaction |
| GF-0090 | "I need help to find my damn invoice from #8178526" | `billing_payments` / `neutral` | `billing_payments` / `negative` | frustration marker → negative |
| GF-0128 | "what do I need to do to download my invoice #37777?" | `feedback_complaints` / `neutral` | `billing_payments` / `neutral` | invoice keyword routes to billing |

## Counterfactual: what v1.* cost

Applying the v2 rules to Round-1 **production** labels (the honest
"how wrong were we shipping?") shows **4.8% of intents mis-routed and
14.5% of sentiments** needing correction — invisible without a gold
set and slice analysis, and the core argument for why annotation QA is
an engineering discipline rather than a vibe.
