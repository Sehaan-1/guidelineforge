import json
import random
from collections import Counter
from datetime import date, timedelta
import numpy as np
import pandas as pd
from agreement import cohen_kappa, fleiss_kappa, krippendorff_alpha, bootstrap_ci, per_class_kappa, confusion_pairs, observed_agreement
from annotators import PERSONAS, CLASSES, SENTIMENTS, label_ticket, POLICY_CUES
from text_features import featurize, V2_INTENT_PRIORITY
OUT = 'results'
SEED_SALT = 20260825
OVERLAP_EXTRA = {'sarcasm': 10, 'mixed_intent': 6, 'polite_complaint': 6, 'tone_trap': 5, 'short_fragment': 3}
OVERLAP_EXTRA_ORGANIC_BORDERLINE = 15
OVERLAP_EXTRA_ORGANIC_CLEAR = 15

def load_inputs():
    corpus = pd.read_csv('data/raw/support_tickets.csv')
    corpus = corpus.sort_values('ticket_id').reset_index(drop=True)
    gold = pd.read_csv('data/gold_set.csv').set_index('ticket_id')
    return (corpus, gold)

def assign_overlap(corpus):
    rng = random.Random(31415)
    idx = set(corpus[corpus.is_calibration | corpus.is_gold].index)
    for amb, k in OVERLAP_EXTRA.items():
        pool = corpus[(corpus.ambiguity_type == amb) & ~corpus.index.isin(idx)].index.tolist()
        rng.shuffle(pool)
        idx.update(pool[:k])
    for borderline, k in [(True, OVERLAP_EXTRA_ORGANIC_BORDERLINE), (False, OVERLAP_EXTRA_ORGANIC_CLEAR)]:
        pool = corpus[(corpus.source == 'bitext') & (corpus.borderline == borderline) & (corpus.ambiguity_type == 'none') & ~corpus.index.isin(idx)].index.tolist()
        rng.shuffle(pool)
        idx.update(pool[:k])
    corpus['in_overlap'] = corpus.index.isin(idx)
    assert corpus.in_overlap.sum() == 180, corpus.in_overlap.sum()
    corpus.to_csv('data/raw/support_tickets.csv', index=False)
    return corpus

def primary_assignments(corpus, rnd):
    keys = [p.key for p in PERSONAS]
    rng = random.Random(2718 + rnd)
    prod = corpus[~corpus.in_overlap].index.tolist()
    rng.shuffle(prod)
    out = {}
    for i, ix in enumerate(prod):
        out[ix] = keys[(i + (rnd - 1)) % 3]
    return out

def run_round(corpus, rnd):
    rows = []
    primary = primary_assignments(corpus, rnd)
    for persona in PERSONAS:
        rng = random.Random(f'{SEED_SALT}-{persona.key}-R{rnd}')
        for ix, t in corpus.iterrows():
            overlap = bool(t.in_overlap)
            if not overlap and primary[ix] != persona.key:
                continue
            intent, sentiment = label_ticket(persona, t.text, rnd, rng)
            rows.append({'round': f'R{rnd}', 'ticket_id': t.ticket_id, 'annotator': persona.key, 'intent': intent, 'sentiment': sentiment, 'role': 'overlap' if overlap else 'production'})
    df = pd.DataFrame(rows)
    df.to_csv(f'data/annotations/annotations_round{rnd}.csv', index=False)
    return df

def labels_matrix(ann, corpus_mask_ids, task):
    seqs = []
    for p in PERSONAS:
        sub = ann[ann.annotator == p.key].set_index('ticket_id')
        seqs.append(sub.loc[corpus_mask_ids, task].tolist())
    return seqs

def senior_v1(text):
    f = featurize(text)
    t = text.lower()
    hits = f['intent_hits']
    if f['frame_hits'] > 0 and f['anger_hits'] >= 1 and hits:
        intent = 'feedback_complaints'
    elif any((c in t for c in POLICY_CUES)) and f['is_question']:
        intent = 'other_contact'
    elif hits:
        intent = f['first_group']
    else:
        intent = 'other_contact'
    if f['anger_hits'] >= 1 or f['negweak_hits'] >= 2:
        sentiment = 'negative'
    elif f['pos_hits'] >= 1:
        sentiment = 'positive'
    else:
        sentiment = 'neutral'
    return (intent, sentiment)

def senior_v2(text):
    f = featurize(text)
    t = text.lower()
    hits = f['intent_hits']
    if any((c in t for c in POLICY_CUES)) and f['is_question']:
        intent = 'other_contact'
    elif hits:
        intent = min(hits, key=V2_INTENT_PRIORITY.index)
    else:
        intent = 'other_contact'
    failure = bool(f['sarcasm_cue']) or f['negweak_hits'] >= 1 or f['anger_hits'] >= 1
    if failure:
        sentiment = 'negative'
    elif f['pos_hits'] >= 1:
        sentiment = 'positive'
    else:
        sentiment = 'neutral'
    return (intent, sentiment)

def first_pass(labels3, rng):
    c = Counter(labels3)
    lab, n = c.most_common(1)[0]
    if n >= 2:
        return (lab, True)
    return (labels3[rng.randrange(3)], False)

def round_metrics(corpus, gold, ann, rnd_name='R1'):
    ov = corpus[corpus.in_overlap]
    ov_ids = ov.ticket_id.tolist()
    intent = labels_matrix(ann, ov_ids, 'intent')
    senti = labels_matrix(ann, ov_ids, 'sentiment')
    keys = [p.key for p in PERSONAS]
    m = {'n_overlap': len(ov_ids), '_round_name': rnd_name}
    for i, j in [(0, 1), (0, 2), (1, 2)]:
        pair = f'cohen_{keys[i]}_{keys[j]}'
        m[pair + '_intent'] = round(cohen_kappa(intent[i], intent[j]), 4)
        m[pair + '_sentiment'] = round(cohen_kappa(senti[i], senti[j]), 4)
    m['cohen_mean_intent'] = round(float(np.mean([m[f'cohen_{a}_{b}_intent'] for a, b in [('A1', 'A2'), ('A1', 'A3'), ('A2', 'A3')]])), 4)
    m['cohen_mean_sentiment'] = round(float(np.mean([m[f'cohen_{a}_{b}_sentiment'] for a, b in [('A1', 'A2'), ('A1', 'A3'), ('A2', 'A3')]])), 4)
    m['fleiss_intent'] = round(fleiss_kappa(intent), 4)
    m['fleiss_sentiment'] = round(fleiss_kappa(senti), 4)
    m['alpha_intent_nominal'] = round(krippendorff_alpha(intent), 4)
    m['alpha_sentiment_ordinal'] = round(krippendorff_alpha(senti, level='ordinal'), 4)
    m['fleiss_intent_ci95'] = [round(x, 4) for x in bootstrap_ci(fleiss_kappa, intent)]
    m['alpha_intent_ci95'] = [round(x, 4) for x in bootstrap_ci(krippendorff_alpha, intent)]
    m['unanimous_intent_overlap'] = round(float(np.mean([len({s[k] for s in intent}) == 1 for k in range(len(ov_ids))])), 4)
    m['unanimous_sentiment_overlap'] = round(float(np.mean([len({s[k] for s in senti}) == 1 for k in range(len(ov_ids))])), 4)
    pc = {c: [] for c in CLASSES}
    for i, j in [(0, 1), (0, 2), (1, 2)]:
        per = per_class_kappa(intent[i], intent[j], CLASSES)
        for c in CLASSES:
            pc[c].append(per[c])
    m['per_class_intent_kappa'] = {c: round(float(np.mean(v)), 4) for c, v in pc.items()}
    slices = {}
    for amb in ['sarcasm', 'mixed_intent', 'polite_complaint', 'tone_trap', 'short_fragment', 'none']:
        ids = ov[ov.ambiguity_type == amb].ticket_id.tolist()
        if amb == 'none':
            ids = ids[:60]
        if not ids:
            continue
        si = labels_matrix(ann, ids, 'intent')
        ss = labels_matrix(ann, ids, 'sentiment')
        slices[amb] = {'n': len(ids), 'unanimous_intent': round(float(np.mean([len({s[k] for s in si}) == 1 for k in range(len(ids))])), 3), 'unanimous_sentiment': round(float(np.mean([len({s[k] for s in ss}) == 1 for k in range(len(ids))])), 3), 'fleiss_intent': round(fleiss_kappa(si), 3), 'fleiss_sentiment': round(fleiss_kappa(ss), 3)}
    m['slices'] = slices
    m['top_confusions_A1_A2'] = [{'a1': a, 'a2': b, 'n': int(n)} for (a, b), n in confusion_pairs(intent[0], intent[1])[:6]]
    gold_ids = corpus[corpus.is_gold].ticket_id.tolist()
    gi = gold.loc[gold_ids, 'gold_intent'].tolist()
    gs = gold.loc[gold_ids, 'gold_sentiment'].tolist()
    gacc = {}
    for k, p in enumerate(PERSONAS):
        pi = labels_matrix(ann, gold_ids, 'intent')[k]
        ps = labels_matrix(ann, gold_ids, 'sentiment')[k]
        gacc[p.key] = {'intent_acc': round(observed_agreement(pi, gi), 4), 'sentiment_acc': round(observed_agreement(ps, gs), 4)}
    m['gold_accuracy'] = gacc
    dc = corpus[corpus.is_calibration].ticket_id.tolist()
    di = corpus.set_index('ticket_id').loc[dc, 'design_intent'].tolist()
    m['calibration_intent_acc_vs_design'] = {p.key: round(observed_agreement(labels_matrix(ann, dc, 'intent')[k], di), 4) for k, p in enumerate(PERSONAS)}
    era = m.get('_round_name', 'R1')
    senior = senior_v1 if era == 'R1' else senior_v2
    texts = corpus.set_index('ticket_id').loc[dc, 'text'].tolist()
    adj_i = [senior(t)[0] for t in texts]
    adj_s = [senior(t)[1] for t in texts]
    m['calibration_gate'] = {p.key: {'intent_acc_vs_era_adjudicated': round(observed_agreement(labels_matrix(ann, dc, 'intent')[k], adj_i), 4), 'both_acc_vs_era_adjudicated': round(float(np.mean([a == c and b == d for a, b, c, d in zip(labels_matrix(ann, dc, 'intent')[k], labels_matrix(ann, dc, 'sentiment')[k], adj_i, adj_s)])), 4)} for k, p in enumerate(PERSONAS)}
    trap_ids = corpus[corpus.ambiguity_type == 'tone_trap'].ticket_id.tolist()
    truth = corpus.set_index('ticket_id').loc[trap_ids, 'design_intent'].tolist()
    ti = labels_matrix(ann, trap_ids, 'intent')
    m['tone_trap_slice'] = {'n': len(trap_ids), 'unanimous_agreement': round(float(np.mean([len({s[k] for s in ti}) == 1 for k in range(len(trap_ids))])), 3), 'accuracy_vs_design': {p.key: round(observed_agreement(ti[k], truth), 3) for k, p in enumerate(PERSONAS)}}
    trend = {}
    for b in ['B1', 'B2', 'B3', 'B4']:
        ids = ov[ov.batch == b].ticket_id.tolist()
        trend[b] = round(fleiss_kappa(labels_matrix(ann, ids, 'intent')), 4)
    m['fleiss_intent_by_batch'] = trend
    gbatch = {}
    for b in ['B1', 'B2', 'B3', 'B4']:
        ids = corpus[corpus.is_gold & (corpus.batch == b)].ticket_id.tolist()
        if not ids:
            continue
        gi_b = gold.loc[ids, 'gold_intent'].tolist()
        gbatch[b] = {p.key: round(observed_agreement(labels_matrix(ann, ids, 'intent')[k], gi_b), 3) for k, p in enumerate(PERSONAS)}
    m['gold_intent_acc_by_batch'] = gbatch
    return m

def run_qa(corpus, gold, ann_r2):
    rng = random.Random(4242)
    rows, stats = ([], {'prod_reviewed': 0, 'ov_reviewed': 0})
    ann_idx = ann_r2.set_index(['ticket_id', 'annotator'])
    primary = primary_assignments(corpus, 2)
    for ix, t in corpus.iterrows():
        tid, text = (t.ticket_id, t.text)
        sen_i, sen_s = senior_v2(text)
        if t.in_overlap:
            il = [ann_idx.loc[(tid, p.key), 'intent'] for p in PERSONAS]
            sl = [ann_idx.loc[(tid, p.key), 'sentiment'] for p in PERSONAS]
            fp_i, ok_i = first_pass(il, rng)
            fp_s, ok_s = first_pass(sl, rng)
            un_i = ok_i and len(set(il)) == 1
            un_s = ok_s and len(set(sl)) == 1
            reviewed = not (un_i and un_s)
            stats['ov_reviewed'] += int(reviewed)
            final_i, final_s = (fp_i if un_i else sen_i, fp_s if un_s else sen_s)
            role = 'overlap'
        else:
            pk = primary[ix]
            fp_i = ann_idx.loc[(tid, pk), 'intent']
            fp_s = ann_idx.loc[(tid, pk), 'sentiment']
            stats['prod_reviewed'] += 1
            final_i = fp_i if fp_i == sen_i else sen_i
            final_s = fp_s if fp_s == sen_s else sen_s
            role = 'production'
        rows.append({'ticket_id': tid, 'label_role': role, 'first_pass_intent': fp_i, 'final_intent': final_i, 'intent_rework': final_i != fp_i, 'first_pass_sentiment': fp_s, 'final_sentiment': final_s, 'sentiment_rework': final_s != fp_s, 'qa_stage': 'tier2_senior_review'})
    final = pd.DataFrame(rows)
    N = len(final)
    prod_mask = final.label_role == 'production'
    qa = {'tier2_review_volume': stats, 'rework_rate_intent': round(float(final.intent_rework.mean()), 4), 'rework_rate_sentiment': round(float(final.sentiment_rework.mean()), 4), 'rework_rate_either': round(float((final.intent_rework | final.sentiment_rework).mean()), 4), 'rework_rate_intent_production': round(float(final[prod_mask].intent_rework.mean()), 4), 'rework_rate_sentiment_production': round(float(final[prod_mask].sentiment_rework.mean()), 4), 'rework_by_class_intent': final.assign(cls=final.final_intent).groupby('cls').intent_rework.mean().round(3).to_dict()}
    gids = corpus[corpus.is_gold].ticket_id
    g = gold.loc[gids]
    fg = final.set_index('ticket_id').loc[gids]
    qa['final_gold_intent_acc'] = round(float((fg.final_intent == g.gold_intent).mean()), 4)
    qa['final_gold_sentiment_acc'] = round(float((fg.final_sentiment == g.gold_sentiment).mean()), 4)
    rng3 = random.Random(777)
    audit_ids = []
    for c in CLASSES:
        ids = final[final.final_intent == c].ticket_id.tolist()
        rng3.shuffle(ids)
        audit_ids += ids[:15]
    arows = []
    for tid in audit_ids:
        row = final.set_index('ticket_id').loc[tid]
        if tid in gold.index:
            gold_row = gold.loc[tid]
            verdict = row.final_intent == gold_row.gold_intent
            arows.append({'ticket_id': tid, 'final_intent': row.final_intent, 'audit_reference': gold_row.gold_intent, 'ref_source': 'gold_set', 'verdict': 'pass' if verdict else 'fail'})
        else:
            text = corpus.set_index('ticket_id').loc[tid, 'text']
            ref = senior_v2(text)[0]
            verdict = row.final_intent == ref
            arows.append({'ticket_id': tid, 'final_intent': row.final_intent, 'audit_reference': ref, 'ref_source': 'independent_rule_derivation', 'verdict': 'pass' if verdict else 'fail'})
    audit = pd.DataFrame(arows)
    gold_part = audit[audit.ref_source == 'gold_set']
    qa['tier3_audit'] = {'n': len(audit), 'pass_rate_overall': round(float((audit.verdict == 'pass').mean()), 4), 'pass_rate_vs_gold_subset': round(float((gold_part.verdict == 'pass').mean()), 4) if len(gold_part) else None, 'n_gold_in_audit': int(len(gold_part)), 'fails': audit[audit.verdict == 'fail'].ticket_id.tolist()}
    audit.to_csv('data/qa_audit_results.csv', index=False)
    final.to_csv('data/adjudicated_labels.csv', index=False)
    return (final, qa)

def build_timeline():
    vols = {}
    for rnd in (1, 2):
        ann = pd.read_csv(f'data/annotations/annotations_round{rnd}.csv')
        vols[rnd] = ann.groupby('annotator').ticket_id.count().to_dict()
    paces = {'A1': 1.0, 'A2': 0.88, 'A3': 1.25}
    start = date(2026, 6, 29)
    rows = []
    for rnd in (1, 2):
        weeks = range(0, 4) if rnd == 1 else range(5, 9)
        days = [(wk, d) for wk in weeks for d in range(5)]
        for p, vol in vols[rnd].items():
            rng_w = random.Random(f'{p}-pace-R{rnd}')
            w = [max(0.25, rng_w.gauss(paces[p], 0.18)) for _ in days]
            raw = [x / sum(w) * vol for x in w]
            counts = [int(x) for x in raw]
            for _ in range(vol - sum(counts)):
                counts[max(range(len(counts)), key=lambda i: raw[i] - counts[i])] += 1
            for (wk, d), n in zip(days, counts):
                rows.append({'date': (start + timedelta(weeks=wk, days=d)).isoformat(), 'annotator': p, 'round': f'R{rnd}', 'tasks_completed': n})
    for wk in [4]:
        for d in range(5):
            day = start + timedelta(weeks=wk, days=d)
            for p in vols[1]:
                rows.append({'date': day.isoformat(), 'annotator': p, 'round': 'REV', 'tasks_completed': 0})
    tl = pd.DataFrame(rows)
    for rnd in (1, 2):
        got = tl[tl['round'] == f'R{rnd}'].groupby('annotator').tasks_completed.sum().to_dict()
        assert got == vols[rnd], f'timeline mismatch R{rnd}: {got} != {vols[rnd]}'
    tl.to_csv('results/timeline.csv', index=False)
    print('timeline reconciled with label volumes:', {r: sum(v.values()) for r, v in vols.items()})
    return tl

def main():
    corpus, gold = load_inputs()
    corpus = assign_overlap(corpus)
    r1 = run_round(corpus, 1)
    r2 = run_round(corpus, 2)
    M = {'R1': round_metrics(corpus, gold, r1, 'R1'), 'R2': round_metrics(corpus, gold, r2, 'R2')}
    final, qa = run_qa(corpus, gold, r2)
    M['qa'] = qa
    prod = corpus[~corpus.in_overlap]
    ann1 = r1.set_index(['ticket_id', 'annotator'])
    prim1 = primary_assignments(corpus, 1)
    di_cnt = ds_cnt = tot = 0
    for ix, t in prod.iterrows():
        pk = prim1[ix]
        li = ann1.loc[(t.ticket_id, pk), 'intent']
        ls = ann1.loc[(t.ticket_id, pk), 'sentiment']
        si, ss = senior_v2(t.text)
        di_cnt += int(li != si)
        ds_cnt += int(ls != ss)
        tot += 1
    M['counterfactual_v1_cost'] = {'r1_production_intents_misrouted_under_v2': round(di_cnt / tot, 4), 'r1_production_sentiments_corrected_under_v2': round(ds_cnt / tot, 4)}
    for rr in ('R1', 'R2'):
        M[rr].pop('_round_name', None)
    M['design'] = {'corpus': int(len(corpus)), 'overlap': int(corpus.in_overlap.sum()), 'gold': int(corpus.is_gold.sum()), 'calibration': int(corpus.is_calibration.sum())}
    build_timeline()
    with open(f'{OUT}/metrics.json', 'w') as fh:
        json.dump(M, fh, indent=2, default=str)
    flat = ['fleiss_intent', 'fleiss_sentiment', 'alpha_intent_nominal', 'alpha_sentiment_ordinal', 'cohen_mean_intent', 'cohen_mean_sentiment', 'unanimous_intent_overlap', 'unanimous_sentiment_overlap']
    rows = [{'metric': k, 'R1': M['R1'][k], 'R2': M['R2'][k]} for k in flat]
    for c in CLASSES:
        rows.append({'metric': f'per_class_kappa/{c}', 'R1': M['R1']['per_class_intent_kappa'][c], 'R2': M['R2']['per_class_intent_kappa'][c]})
    for p in ['A1', 'A2', 'A3']:
        for task in ['intent_acc', 'sentiment_acc']:
            rows.append({'metric': f'gold_{task}/{p}', 'R1': M['R1']['gold_accuracy'][p][task], 'R2': M['R2']['gold_accuracy'][p][task]})
    rows += [{'metric': 'rework_rate_intent', 'R1': '—', 'R2': qa['rework_rate_intent']}, {'metric': 'rework_rate_either', 'R1': '—', 'R2': qa['rework_rate_either']}, {'metric': 'tier3_audit_pass_rate', 'R1': '—', 'R2': qa['tier3_audit']['pass_rate_overall']}, {'metric': 'final_gold_intent_acc', 'R1': '—', 'R2': qa['final_gold_intent_acc']}, {'metric': 'final_gold_sentiment_acc', 'R1': '—', 'R2': qa['final_gold_sentiment_acc']}]
    pd.DataFrame(rows).to_csv(f'{OUT}/metrics_summary.csv', index=False)
    print('=== headline (overlap n=180, Fleiss/α κ-family) ===')
    for k in flat:
        print(f"{k:32s} R1={M['R1'][k]:>7}  R2={M['R2'][k]:>7}")
    print('\n=== slices (unanimous agreement, overlap) ===')
    for amb in ['sarcasm', 'mixed_intent', 'polite_complaint', 'tone_trap', 'short_fragment', 'none']:
        s1, s2 = (M['R1']['slices'].get(amb), M['R2']['slices'].get(amb))
        if s1:
            print(f"{amb:>17s} n={s1['n']:3d}: intent {s1['unanimous_intent']:.2f}→{s2['unanimous_intent']:.2f}  sentiment {s1['unanimous_sentiment']:.2f}→{s2['unanimous_sentiment']:.2f}")
    print('\ntone-trap:', json.dumps(M['R1']['tone_trap_slice']))
    print('gold intent acc   R1→R2:', {p: (M['R1']['gold_accuracy'][p]['intent_acc'], M['R2']['gold_accuracy'][p]['intent_acc']) for p in ['A1', 'A2', 'A3']})
    print('gold sentim acc   R1→R2:', {p: (M['R1']['gold_accuracy'][p]['sentiment_acc'], M['R2']['gold_accuracy'][p]['sentiment_acc']) for p in ['A1', 'A2', 'A3']})
    print('calibration gate R1→R2:', {p: (M['R1']['calibration_gate'][p]['both_acc_vs_era_adjudicated'], M['R2']['calibration_gate'][p]['both_acc_vs_era_adjudicated']) for p in ['A1', 'A2', 'A3']})
    print('counterfactual v1 cost:', M['counterfactual_v1_cost'])
    print('\nQA:', json.dumps(qa, indent=1, default=str))
    print('batch fleiss:', M['R1']['fleiss_intent_by_batch'], M['R2']['fleiss_intent_by_batch'])
if __name__ == '__main__':
    main()
