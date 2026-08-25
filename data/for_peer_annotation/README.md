# Peer annotation pack — run YOUR OWN inter-annotator study

This folder turns the project from a simulation into a real multi-annotator
study. It is the exact protocol the built-in personas simulate.

## For annotators (your 2–3 peers)

1. Take **one** sheet each (`annotator_sheet_*.csv`) and label the **same**
   set — do **not** split the rows. Agreement is measured on what you all
   labeled.
2. Work **alone**: no discussing tickets, no comparing answers mid-study.
   Your disagreements are the data.
3. Read `guidelines/annotation_guidelines_v1.md` first.
4. For each row fill:
   - `intent_label` — exactly one of:
     `refund_request`, `cancellation`, `billing_payments`,
     `shipping_delivery`, `order_changes`, `account_access`,
     `feedback_complaints`, `other_contact`
   - `sentiment_label` — exactly one of: `negative`, `neutral`, `positive`
5. You may leave up to ~10% of rows blank (the metrics tolerate missing
   labels); don't guess wildly — skip and move on.
6. Return the CSV unchanged in structure.

## For the lead (you)

```bash
PYTHONPATH=src python3 src/import_peer_labels.py \
    --sheets data/for_peer_annotation/annotator_sheet_1.csv \
             data/for_peer_annotation/annotator_sheet_2.csv \
             data/for_peer_annotation/annotator_sheet_3.csv \
    --names Maya Jonas Ekim --round 1
```

This validates the sheets and recomputes the full battery (Cohen, Fleiss,
Krippendorff, per-class, gold accuracy) on your peers' blind overlap.
Everything downstream — slices, guideline revision logic, QA tiers — then
applies exactly as documented in the persona study. That's the point:
**the methodology is annotator-agnostic.**

Tip: the 48 calibration tickets (`is_calibration` in the corpus) are the
certification gate; the 72 gold tickets are your per-annotator accuracy
benchmark. Don't tell peers which rows those are.
