import numpy as np

def _to_rater_matrix(labels):
    cats = sorted({v for r in labels for v in r if v is not None})
    idx = {c: i for i, c in enumerate(cats)}
    M, N = (len(labels), len(labels[0]))
    mat = np.full((M, N), -1, dtype=int)
    for m, rater in enumerate(labels):
        assert len(rater) == N, 'all raters must label all items here'
        for n, v in enumerate(rater):
            mat[m, n] = -1 if v is None else idx[v]
    return (mat, cats)

def observed_agreement(y1, y2):
    y1, y2 = (np.asarray(y1), np.asarray(y2))
    return float(np.mean(y1 == y2))

def cohen_kappa(y1, y2):
    cats = sorted(set(y1) | set(y2))
    y1, y2 = (np.asarray(y1), np.asarray(y2))
    n = len(y1)
    ao = np.mean(y1 == y2)
    p1 = np.array([np.mean(y1 == c) for c in cats])
    p2 = np.array([np.mean(y2 == c) for c in cats])
    ae = float(p1 @ p2)
    return (ao - ae) / (1 - ae) if ae < 1 else 1.0

def fleiss_kappa(labels):
    mat, cats = _to_rater_matrix(labels)
    assert (mat >= 0).all(), 'fleiss_kappa: missing labels not supported'
    if len(cats) < 2:
        return 1.0
    M, N = mat.shape
    n_ij = np.array([[np.sum(mat[:, i] == j) for j in range(len(cats))] for i in range(N)], dtype=float)
    P_i = ((n_ij ** 2).sum(axis=1) - M) / (M * (M - 1))
    P_bar = P_i.mean()
    p_j = n_ij.sum(axis=0) / (N * M)
    P_e = float(p_j @ p_j)
    return (P_bar - P_e) / (1 - P_e) if P_e < 1 else 1.0

def krippendorff_alpha(labels, level='nominal'):
    mat, cats = _to_rater_matrix(labels)
    K = len(cats)
    if K < 2:
        return 1.0
    delta = np.ones((K, K)) - np.eye(K)
    if level == 'ordinal':
        r = np.arange(K)
        delta = ((r[:, None] - r[None, :]) / (K - 1.0)) ** 2
    O = np.zeros((K, K))
    for n in range(mat.shape[1]):
        vals = mat[:, n]
        vals = vals[vals >= 0]
        m_u = len(vals)
        if m_u < 2:
            continue
        counts = np.bincount(vals, minlength=K).astype(float)
        for c in range(K):
            if counts[c] == 0:
                continue
            for k in range(K):
                if counts[k] == 0:
                    continue
                O[c, k] += counts[c] * (counts[c] - 1) / (m_u - 1) if c == k else counts[c] * counts[k] / (m_u - 1)
    n_c = O.sum(axis=1)
    n = O.sum()
    if n == 0:
        return 1.0
    Do = float((O * delta).sum() / n)
    De = float((np.outer(n_c, n_c) * delta).sum() / (n * (n - 1)))
    return 1.0 - Do / De if De > 0 else 1.0

def bootstrap_ci(metric_fn, labels, n_boot=500, seed=13, **kw):
    rng = np.random.default_rng(seed)
    mat, _ = _to_rater_matrix(labels)
    N = mat.shape[1]
    stats = []
    for _ in range(n_boot):
        cols = rng.integers(0, N, N)
        resample = [[row[c] for c in cols] for row in mat]
        try:
            stats.append(metric_fn(resample, **kw) if kw else metric_fn(resample))
        except Exception:
            continue
    lo, hi = np.percentile(stats, [2.5, 97.5])
    return (float(lo), float(hi))

def per_class_kappa(y1, y2, classes):
    out = {}
    for c in classes:
        b1 = [v == c for v in y1]
        b2 = [v == c for v in y2]
        out[c] = cohen_kappa(b1, b2)
    return out

def confusion_pairs(y1, y2):
    from collections import Counter
    c = Counter(((a, b) for a, b in zip(y1, y2) if a != b))
    return c.most_common()

def _wiki_fleiss_example():
    table = [[0, 0, 0, 0, 14], [0, 2, 6, 4, 2], [0, 0, 3, 5, 6], [0, 3, 9, 2, 0], [2, 2, 8, 1, 1], [7, 7, 0, 0, 0], [3, 2, 6, 3, 0], [2, 5, 3, 2, 2], [6, 5, 2, 1, 0], [0, 2, 2, 3, 7]]
    cols = [[None] * 14 for _ in range(len(table))]
    for i, row in enumerate(table):
        assignments = []
        for cat, n in enumerate(row):
            assignments += [cat] * int(n)
        assert len(assignments) == 14, f'row {i} must sum to 14'
        for r in range(14):
            cols[i][r] = assignments[r]
    return [[cols[i][r] for i in range(len(table))] for r in range(14)]

def run_self_tests(verbose=True):
    res = {}
    a = ['x', 'y', 'x', 'x', 'y', 'z', 'z', 'x']
    res['cohen_perfect'] = abs(cohen_kappa(a, a) - 1.0) < 1e-09
    res['fleiss_perfect'] = abs(fleiss_kappa([a, a, a]) - 1.0) < 1e-09
    res['alpha_perfect'] = abs(krippendorff_alpha([a, a, a]) - 1.0) < 1e-09
    wiki = fleiss_kappa(_wiki_fleiss_example())
    res['fleiss_wikipedia_0.210'] = abs(wiki - 0.21) < 0.002
    res['_fleiss_wiki_value'] = round(wiki, 4)
    rng = np.random.default_rng(0)
    A = rng.integers(0, 4, 200)
    B = np.where(rng.random(200) < 0.7, A, rng.integers(0, 4, 200))
    try:
        from sklearn.metrics import cohen_kappa_score
        mine = cohen_kappa(A.tolist(), B.tolist())
        theirs = cohen_kappa_score(A, B)
        res['cohen_matches_sklearn'] = abs(mine - theirs) < 1e-09
    except ImportError:
        res['cohen_matches_sklearn'] = 'skipped (no sklearn)'
    try:
        from nltk.metrics.agreement import AnnotationTask
        C = np.where(rng.random(200) < 0.65, A, rng.integers(0, 4, 200))
        data = []
        for rater, seq in enumerate([A, B, C]):
            for item, v in enumerate(seq):
                data.append((str(rater), str(item), str(v)))
        t = AnnotationTask(data=data)
        nltk_fleiss = t.multi_kappa() if hasattr(t, 'multi_kappa') else t.fleiss_kappa()
        res['_fleiss_mine_vs_nltk'] = (round(fleiss_kappa([A.tolist(), B.tolist(), C.tolist()]), 4), round(nltk_fleiss, 4))
        res['fleiss_matches_nltk'] = abs(res['_fleiss_mine_vs_nltk'][0] - res['_fleiss_mine_vs_nltk'][1]) < 0.02
        mine_a = krippendorff_alpha([A.tolist(), B.tolist(), C.tolist()])
        theirs_a = t.alpha()
        res['_alpha_mine_vs_nltk'] = (round(mine_a, 4), round(theirs_a, 4))
        res['alpha_matches_nltk'] = abs(mine_a - theirs_a) < 0.02
        from nltk.metrics import interval_distance
        t_ord = AnnotationTask(data=[(a, b, int(v)) for a, b, v in data], distance=interval_distance)
        mine_ord = krippendorff_alpha([A.tolist(), B.tolist(), C.tolist()], level='ordinal')
        res['_alpha_ordinal_mine_vs_nltk'] = (round(mine_ord, 4), round(t_ord.alpha(), 4))
        res['alpha_ordinal_matches_nltk_interval'] = abs(mine_ord - t_ord.alpha()) < 0.02
    except ImportError:
        res['fleiss_matches_nltk'] = 'skipped (no nltk)'
        res['alpha_matches_nltk'] = 'skipped (no nltk)'
    if verbose:
        for k, v in res.items():
            print(f'  {k:28s} {v}')
    bools = [bool(v) for k, v in res.items() if isinstance(v, (bool, np.bool_))]
    assert all(bools), f'agreement self-tests failed: {res}'
    return res
if __name__ == '__main__':
    print('agreement.py self-tests:')
    run_self_tests()
    print('ALL SELF-TESTS PASSED')
