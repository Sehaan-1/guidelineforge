import pytest
import numpy as np
import warnings

from agreement import (
    observed_agreement,
    cohen_kappa,
    fleiss_kappa,
    krippendorff_alpha,
    bootstrap_ci,
    per_class_kappa,
    confusion_pairs,
    _wiki_fleiss_example,
)


def test_observed_agreement_perfect():
    y1 = ["a", "b", "c", "d"]
    y2 = ["a", "b", "c", "d"]
    assert observed_agreement(y1, y2) == 1.0


def test_observed_agreement_mismatch():
    y1 = ["a", "b", "c", "d"]
    y2 = ["b", "a", "d", "c"]
    assert observed_agreement(y1, y2) == 0.0


def test_observed_agreement_length_error():
    with pytest.raises(ValueError, match="Length mismatch"):
        observed_agreement(["a"], ["a", "b"])


def test_cohen_kappa_perfect():
    y1 = ["refund_request", "cancellation", "shipping_delivery", "billing_payments"]
    assert cohen_kappa(y1, y1) == 1.0


def test_cohen_kappa_chance():
    rng = np.random.default_rng(42)
    y1 = rng.choice(["a", "b", "c", "d"], size=1000).tolist()
    y2 = rng.choice(["a", "b", "c", "d"], size=1000).tolist()
    kappa = cohen_kappa(y1, y2)
    assert abs(kappa) < 0.10


def test_cohen_kappa_length_error():
    with pytest.raises(ValueError, match="Length mismatch"):
        cohen_kappa(["a", "b"], ["a"])


@pytest.mark.parametrize("seed", [0, 42, 123])
def test_cohen_kappa_matches_sklearn(seed):
    try:
        from sklearn.metrics import cohen_kappa_score
    except ImportError:
        pytest.skip("scikit-learn is not installed")
    
    rng = np.random.default_rng(seed)
    A = rng.integers(0, 5, 250)
    B = np.where(rng.random(250) < 0.75, A, rng.integers(0, 5, 250))
    
    ours = cohen_kappa(A.tolist(), B.tolist())
    theirs = cohen_kappa_score(A, B)
    assert abs(ours - theirs) < 1e-8


def test_fleiss_kappa_perfect():
    r1 = ["x", "y", "z", "x"]
    r2 = ["x", "y", "z", "x"]
    r3 = ["x", "y", "z", "x"]
    assert fleiss_kappa([r1, r2, r3]) == 1.0


def test_fleiss_kappa_wiki_reference():
    wiki_mat = _wiki_fleiss_example()
    val = fleiss_kappa(wiki_mat)
    assert abs(val - 0.210) < 0.002


def test_fleiss_kappa_missing_labels_raises():
    r1 = ["a", None, "b"]
    r2 = ["a", "b", "c"]
    with pytest.raises(ValueError, match="missing labels"):
        fleiss_kappa([r1, r2])


def test_fleiss_kappa_length_mismatch_raises():
    r1 = ["a", "b"]
    r2 = ["a", "b", "c"]
    with pytest.raises(ValueError, match="all raters must label the same number of items"):
        fleiss_kappa([r1, r2])


def test_krippendorff_alpha_perfect_nominal():
    seq = ["a", "b", "a", "c", "b"]
    assert krippendorff_alpha([seq, seq, seq], level="nominal") == 1.0


def test_krippendorff_alpha_perfect_ordinal():
    seq = ["negative", "neutral", "positive", "neutral"]
    assert krippendorff_alpha([seq, seq, seq], level="ordinal") == 1.0


def test_krippendorff_ordinal_penalizes_polar_flips_more():
    # Provide items covering all categories so K=3
    r_base = ["negative", "neutral", "positive", "negative", "neutral", "positive"]
    # Adjacent shifts (neg -> neu, neu -> pos, etc.)
    r_adj  = ["neutral", "positive", "neutral", "neutral", "positive", "neutral"]
    # Polar shifts (neg -> pos, pos -> neg)
    r_opp  = ["positive", "neutral", "negative", "positive", "neutral", "negative"]

    alpha_adj = krippendorff_alpha([r_base, r_adj], level="ordinal")
    alpha_opp = krippendorff_alpha([r_base, r_opp], level="ordinal")
    assert alpha_opp < alpha_adj


def test_bootstrap_ci_bounds():
    rng = np.random.default_rng(99)
    A = rng.integers(0, 3, 100).tolist()
    B = A[:]
    # Introduce small noise
    for i in range(10):
        B[i] = (B[i] + 1) % 3
    
    lo, hi = bootstrap_ci(fleiss_kappa, [A, B], n_boot=100, seed=13)
    assert 0.0 <= lo <= hi <= 1.0


def test_per_class_kappa():
    y1 = ["a", "a", "b", "c", "c"]
    y2 = ["a", "b", "b", "c", "c"]
    classes = ["a", "b", "c"]
    res = per_class_kappa(y1, y2, classes)
    assert set(res.keys()) == set(classes)
    assert res["c"] == 1.0  # Perfect on class 'c'


def test_confusion_pairs():
    y1 = ["a", "a", "b", "c"]
    y2 = ["b", "a", "c", "c"]
    pairs = confusion_pairs(y1, y2)
    assert (("a", "b"), 1) in pairs
    assert (("b", "c"), 1) in pairs
