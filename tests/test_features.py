import pytest
from text_features import featurize, V2_INTENT_PRIORITY


def test_sarcasm_phrase_detected():
    text = "Oh great, my card got charged twice again. Exactly what I needed today."
    feats = featurize(text)
    assert feats["sarcasm_cue"] is True
    assert feats["negweak_hits"] >= 1 or feats["anger_hits"] >= 1


def test_contrast_sarcasm_detected():
    text = "Great job, really: my delivery went to the wrong address."
    feats = featurize(text)
    assert feats["sarcasm_cue"] is True
    assert feats["pos_hits"] >= 1


def test_anger_hits_counting():
    text = "This is ridiculous, unacceptable, and the worst experience ever!"
    feats = featurize(text)
    assert feats["anger_hits"] >= 3
    assert feats["frame_hits"] >= 3


def test_intent_hits_mixed_multi_group():
    text = "Cancel order #1234567 immediately and refund the $50 to my card."
    feats = featurize(text)
    assert "refund_request" in feats["intent_hits"]
    assert "cancellation" in feats["intent_hits"]
    assert feats["n_groups"] >= 2


def test_is_question_detection():
    assert featurize("How do I see your refund policy?")["is_question"] is True
    assert featurize("I want my money back now.")["is_question"] is False


def test_v2_intent_priority_hierarchy():
    # In v2, refund_request has higher priority than cancellation
    hits = ["cancellation", "refund_request"]
    chosen = min(hits, key=V2_INTENT_PRIORITY.index)
    assert chosen == "refund_request"

    # cancellation has higher priority than shipping_delivery
    hits2 = ["shipping_delivery", "cancellation"]
    chosen2 = min(hits2, key=V2_INTENT_PRIORITY.index)
    assert chosen2 == "cancellation"


def test_featurize_cache_stability():
    text = "Please cancel my subscription #999"
    f1 = featurize(text)
    f2 = featurize(text)
    assert f1 is f2  # Check identical reference from lru_cache
