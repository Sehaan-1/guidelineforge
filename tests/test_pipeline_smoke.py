import random
from pathlib import Path
import pandas as pd
import pytest

from annotators import PERSONAS, label_ticket
from simulate_pipeline import (
    load_inputs,
    round_metrics,
    _tier2_adjudicate,
    _tier3_rederive,
    first_pass,
)

ROOT = Path(__file__).resolve().parent.parent


def test_load_inputs_and_schema():
    corpus, gold = load_inputs()
    assert len(corpus) == 600
    assert len(gold) == 72
    
    expected_corpus_cols = {
        "ticket_id", "text", "source", "design_intent", "ambiguity_type",
        "augmentation", "design_sentiment", "borderline", "is_gold",
        "is_calibration", "batch"
    }
    assert expected_corpus_cols.issubset(corpus.columns)


def test_persona_labeling_smoke():
    corpus, _ = load_inputs()
    sample_text = corpus.iloc[0]["text"]
    rng = random.Random(42)
    
    for persona in PERSONAS:
        for rnd in (1, 2):
            intent, sentiment = label_ticket(persona, sample_text, rnd, rng)
            assert isinstance(intent, str) and len(intent) > 0
            assert sentiment in {"negative", "neutral", "positive"}


def test_tier2_and_tier3_adjudication_parity():
    test_texts = [
        "Refund my card for order #12345 immediately!",
        "Cancel order #999 and give me my money back.",
        "How do I view your refund policy?",
        "Oh great, package is late again. Top notch service.",
    ]
    for text in test_texts:
        t2_intent, t2_sent = _tier2_adjudicate(text)
        t3_intent, t3_sent = _tier3_rederive(text)
        assert t2_intent == t3_intent
        assert t2_sent == t3_sent


def test_first_pass_aggregation():
    rng = random.Random(42)
    # Unanimous
    lab, is_unanimous = first_pass(["refund_request", "refund_request", "refund_request"], rng)
    assert lab == "refund_request"
    assert is_unanimous is True

    # Majority (2 vs 1)
    lab, is_majority = first_pass(["refund_request", "refund_request", "cancellation"], rng)
    assert lab == "refund_request"
    assert is_majority is True

    # Complete split
    lab, is_split = first_pass(["refund_request", "cancellation", "shipping_delivery"], rng)
    assert lab in {"refund_request", "cancellation", "shipping_delivery"}
    assert is_split is False
