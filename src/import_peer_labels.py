import argparse
import sys
import numpy as np
import pandas as pd
from agreement import cohen_kappa, fleiss_kappa, krippendorff_alpha, per_class_kappa, observed_agreement
VALID_INTENTS = {'refund_request', 'cancellation', 'billing_payments', 'shipping_delivery', 'order_changes', 'account_access', 'feedback_complaints', 'other_contact'}
VALID_SENTIMENTS = {'negative', 'neutral', 'positive'}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sheets', nargs=3, required=True)
    ap.add_argument('--names', nargs=3, default=['P1', 'P2', 'P3'])
    ap.add_argument('--round', type=int, choices=[1, 2], required=True)
    args = ap.parse_args()
    corpus = pd.read_csv('data/raw/support_tickets.csv')
    gold = pd.read_csv('data/gold_set.csv')
    ok_ids = set(corpus.ticket_id)
    frames = []
    for path, name in zip(args.sheets, args.names):
        df = pd.read_csv(path, dtype=str).fillna('')
        need = {'ticket_id', 'text', 'intent_label', 'sentiment_label'}
        assert need.issubset(df.columns), f'{path}: need columns {need}'
        df = df[df.intent_label.str.strip() != '']
        bad_i = set(df.intent_label) - VALID_INTENTS
        bad_s = set(df.sentiment_label) - VALID_SENTIMENTS
        bad_t = set(df.ticket_id) - ok_ids
        if bad_i or bad_s or bad_t:
            sys.exit(f"{name}: invalid values — intents {bad_i or '-'}, sentiments {bad_s or '-'}, ids {sorted(bad_t)[:3]}")
        df['annotator'] = name
        df['round'] = f'R{args.round}'
        frames.append(df[['round', 'ticket_id', 'annotator', 'intent_label', 'sentiment_label']].rename(columns={'intent_label': 'intent', 'sentiment_label': 'sentiment'}))
    ann = pd.concat(frames)
    out = f'data/annotations/annotations_peer_round{args.round}.csv'
    ann.to_csv(out, index=False)
    print(f'wrote {out} ({len(ann)} labels)')
    labeled = {n: set(g.ticket_id) for n, g in ann.groupby('annotator')}
    common = sorted(set.intersection(*labeled.values()))
    print(f'{len(common)} tickets labeled by all three annotators')
    if len(common) < 20:
        sys.exit('too little overlap for meaningful agreement (need ≥ 20)')
    seq = lambda task: [ann[ann.annotator == n].set_index('ticket_id').loc[common, task].tolist() for n in args.names]
    ii, ss = (seq('intent'), seq('sentiment'))
    print('\n=== peer agreement (blind overlap subset) ===')
    for a, b in [(0, 1), (0, 2), (1, 2)]:
        print(f'Cohen {args.names[a]}×{args.names[b]}: intent {cohen_kappa(ii[a], ii[b]):.3f}  sentiment {cohen_kappa(ss[a], ss[b]):.3f}')
    print(f'Fleiss    intent {fleiss_kappa(ii):.3f}  sentiment {fleiss_kappa(ss):.3f}')
    print(f"α nominal intent {krippendorff_alpha(ii):.3f}  α ordinal sentiment {krippendorff_alpha(ss, level='ordinal'):.3f}")
    gsub = gold[gold.ticket_id.isin(common)]
    gids = gsub.ticket_id.tolist()
    gi, gs = (gsub.gold_intent.tolist(), gsub.gold_sentiment.tolist())
    print(f'\n=== gold accuracy ({len(gids)} gold items in the overlap) ===')
    for k, n in enumerate(args.names):
        pi = ann[ann.annotator == n].set_index('ticket_id').loc[gids, 'intent']
        ps = ann[ann.annotator == n].set_index('ticket_id').loc[gids, 'sentiment']
        print(f'{n:>8}: intent {observed_agreement(pi, gi):.3f}  sentiment {observed_agreement(ps, gs):.3f}')
    pc = per_class_kappa(ii[0], ii[1], sorted(VALID_INTENTS))
    hard = sorted(pc, key=pc.get)[:3]
    print('\nlowest-agreement classes (pair 1×2):', ', '.join((f'{c} κ={pc[c]:.2f}' for c in hard)))
    print('\nNext step: treat low-κ classes/families exactly like the persona study — hypothesize the rule defect, patch guidelines, re-label a round, re-measure.')
if __name__ == '__main__':
    main()
