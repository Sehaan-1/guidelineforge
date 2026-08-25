# Calibration meeting notes

Real disagreements, pulled from the R1 calibration-set labels
(`data/annotations/annotations_round1.csv` × `is_calibration` in the
corpus). These are the exact tickets the program discussed; the
decisions below are what became guideline v2.0.

---

## Kickoff calibration — Mon 2026-06-29 (before Round 1)

**Protocol.** All three annotators labeled the same 48-ticket
calibration set blind, under guidelines v1.0. Certification gate:
≥ 85% agreement with the lead's adjudicated labels before touching
production data.

**Gate results (accuracy vs. era-adjudicated, intent + sentiment):**

| Annotator | Kick-off result | Status |
|---|---|---|
| A1 (careful) | 89.6% | ✅ certified |
| A2 (empathetic) | 81.3% | ❌ → 1:1 coaching on literal-reading items, recheck passed |
| A3 (fast) | 77.1% | ❌ → training session on keyword-group list + quiz, recheck passed |

**Disagreement tickets reviewed live (label right column = what was
actually submitted):**

- **GF-0067** — "help to file a consumer complaint"
  A1/A2: `feedback_complaints` · A3: `cancellation`. Discussion:
  skimming catches "cancel"-like shapes anywhere. Adjudicated:
  `feedback_complaints`. *Action for A3: always read to end-of-ticket
  before labeling; keyword-count is not a shortcut for intent.*
- **GF-0552** — "check invoice from last purchase"
  A1/A2: `billing_payments` · A3: `order_changes`. Same root cause
  ("purchase" → order). Folded into A3's coaching.

Outcome: all three certified by end of day 2; program authorized to
start B1.

---

## Mid-round observation log (weeks 1–4)

Recurring split patterns logged from the blind overlap (these were NOT
corrected mid-round — mid-round rule changes are forbidden; they were
queued for the revision meeting):

- **Mixed intents**: GF-0169 ("Please issue a refund for #4241087 —
  I've already cancelled it.") — A1/A2: `refund_request`, A3:
  `cancellation`. GF-0202 ("Cancel order #9351146 immediately and I
  expect a full refund of $64.2.") — A1: `cancellation`, A2:
  `refund_request`, A3: `cancellation`. Every annotator had a different,
  defensible tie-break → C2 in the changelog.
- **Tone-first rule doing visible damage**: GF-0370 ("This is
  ridiculous. Refund my card for order #3045073 NOW.") — A1/A2 applied
  v1 R4 → `feedback_complaints`; only A3's keyword skim landed
  `billing_payments`-adjacent. All three agreed on `negative` — the
  intent was the casualty → C1.
- **Sarcasm splits**: GF-0129, GF-0192, GF-0336 — identical literal
  pattern: A2 reads the failure (negative), A1/A3 read the words
  (neutral/positive). → C3.
- **Politeness splits**: GF-0463 ("I'm slightly worried: my delivery
  shows no movement for six days.") — A2: `negative`, A1/A3: `neutral`
  under v1 R5 → C4. (A3 also mislabeled intent `cancellation` here —
  logged as an individual-coaching item, not a guideline problem.)

---

## Recertification — Mon 2026-08-03 (before Round 2)

Same 48-ticket set re-labeled blind under v2.0 after a 45-minute
walkthrough of §4 rules R1/R4Δ/R5/R8/R9 with the revised worked
examples.

| Annotator | Result | Status |
|---|---|---|
| A1 | 97.9% | ✅ |
| A2 | 97.9% | ✅ |
| A3 | 97.9% | ✅ |

Round 2 (B1′–B4′) authorized. Blinding preserved: annotators saw no
Round-1 labels (their own or others') during Round-2 labeling.
