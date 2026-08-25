import random
import sys
from pathlib import Path
import pandas as pd
from text_features import featurize

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / 'data'


RNG = random.Random(20260825)
BITEXT_TO_MACRO = {'get_refund': 'refund_request', 'track_refund': 'refund_request', 'cancel_order': 'cancellation', 'check_cancellation_fee': 'cancellation', 'payment_issue': 'billing_payments', 'check_payment_methods': 'billing_payments', 'check_invoice': 'billing_payments', 'get_invoice': 'billing_payments', 'delivery_options': 'shipping_delivery', 'delivery_period': 'shipping_delivery', 'track_order': 'shipping_delivery', 'change_shipping_address': 'shipping_delivery', 'set_up_shipping_address': 'shipping_delivery', 'create_account': 'account_access', 'delete_account': 'account_access', 'edit_account': 'account_access', 'recover_password': 'account_access', 'registration_problems': 'account_access', 'switch_account': 'account_access', 'change_order': 'order_changes', 'place_order': 'order_changes', 'complaint': 'feedback_complaints', 'review': 'feedback_complaints', 'contact_customer_service': 'other_contact', 'contact_human_agent': 'other_contact', 'newsletter_subscription': 'other_contact', 'check_refund_policy': 'other_contact'}
INTENT_CLASSES = ['refund_request', 'cancellation', 'billing_payments', 'shipping_delivery', 'order_changes', 'account_access', 'feedback_complaints', 'other_contact']
ORGANIC_QUOTA = {'refund_request': 70, 'cancellation': 60, 'billing_payments': 75, 'shipping_delivery': 75, 'account_access': 60, 'order_changes': 45, 'feedback_complaints': 65, 'other_contact': 70}

def design_sentiment(text: str) -> str:
    f = featurize(text)
    if f['sarcasm_cue'] and (f['negweak_hits'] or f['anger_hits']):
        return 'negative'
    if f['anger_hits'] >= 1 or f['negweak_hits'] >= 2:
        return 'negative'
    if f['pos_hits'] >= 1 and f['negweak_hits'] == 0 and (f['anger_hits'] == 0):
        return 'positive'
    return 'neutral'

def sentiment_is_clear(text: str, sent: str) -> bool:
    f = featurize(text)
    if f['sarcasm_cue']:
        return False
    if sent == 'negative':
        return f['anger_hits'] >= 1 and f['pos_hits'] == 0
    if sent == 'positive':
        return f['pos_hits'] >= 1 and f['anger_hits'] == 0 and (f['negweak_hits'] == 0)
    return f['anger_hits'] == 0 and f['pos_hits'] == 0 and (f['negweak_hits'] == 0)
POS_WRAPS = ['Thanks so much! {t}', 'Really appreciate your help — {t}', 'Love the new site, by the way! {t}', '{t} Thanks a lot in advance!', 'Great experience so far. {t}', '{t} — appreciate it!', 'You guys are awesome. Quick question: {t}', 'Happy customer here, just need one thing: {t}']
NEG_WRAPS = ["I'm really frustrated: {t}", 'Honestly quite annoyed — {t}', 'Third time writing about this, getting really frustrated: {t}', "I'm getting tired of this awful runaround. {t}", "I'm really upset about this: {t}", 'Very upsetting situation. {t}', "I'm angry that this keeps happening. {t}", 'Frustrated customer here. {t}']
OIDS = [f'#{RNG.randint(1000000, 9999999)}' for _ in range(60)]
AMTS = [f'${RNG.choice([9.99, 14.5, 19.99, 25, 32.75, 40, 49.99, 58, 64.2, 75, 89.99, 120])}' for _ in range(40)]

def injected_rows():
    rows = []

    def add(amb, intent, sent, text):
        rows.append({'text': text, 'source': f'injected_{amb}', 'true_intent': intent, 'true_sentiment': sent, 'ambiguity_type': amb})
    fails = [('my card got charged twice', 'billing_payments'), ("I still don't have my refund", 'refund_request'), ('my package is a week late', 'shipping_delivery'), ('the app crashes every time I log in', 'account_access'), ('my refund has vanished into thin air', 'refund_request'), ('you billed me for an order I never got', 'billing_payments'), ('my delivery went to the wrong address', 'shipping_delivery'), ("I can't reset my password because your site is down", 'account_access')]
    sarc_templates = ['Oh great, {f} again. Exactly what I needed today.', 'Love how {f}. Really top-notch stuff, guys.', 'Brilliant — {f}. You never disappoint.', 'Fantastic service as always: {f}.', 'Yeah, because {f} is totally my favorite thing.', 'Just perfect. {f_cap}, and nobody even told me.', 'Wow, amazing — {f}. What a wonderful experience.', 'Great job, really: {f}. So happy I chose you.']
    used = set()
    while len([r for r in rows if r['ambiguity_type'] == 'sarcasm']) < 24:
        (f_, intent), tpl = (RNG.choice(fails), RNG.choice(sarc_templates))
        text = tpl.format(f=f_, f_cap=f_[0].upper() + f_[1:])
        if text in used:
            continue
        used.add(text)
        add('sarcasm', intent, 'negative', text)
    mixed_templates = [('Cancel my order {o} and refund the {a} to my card today.', 'refund_request', 'neutral'), ('I want to cancel order {o}. When do I get my money back?', 'refund_request', 'neutral'), ("Please issue a refund for {o} — I've already cancelled it.", 'refund_request', 'neutral'), ("Refund my {a} and cancel the second order ({o}) while you're at it.", 'refund_request', 'neutral'), ("This is the second time I'm asking: cancel {o} and return my {a}.", 'refund_request', 'negative'), ('I was charged twice for {o}, so refund one payment and cancel the duplicate order.', 'refund_request', 'negative'), ('Can you cancel {o}? And the pending charge of {a} needs to come off my card.', 'cancellation', 'neutral'), ('My card was charged {a} for an order I want cancelled ({o}).', 'cancellation', 'neutral'), ('Sort out the duplicate charge on my card and refund {a} for order {o}.', 'refund_request', 'negative'), ('I need to cancel {o} — also why was I billed {a} twice?', 'cancellation', 'neutral'), ('Cancel order {o} immediately and I expect a full refund of {a}.', 'refund_request', 'neutral'), ('Refund please for {o}. Oh and cancel any repeat orders on my account.', 'refund_request', 'neutral'), ('Wrong item shipped for {o}: refund my {a} and cancel the replacement you sent.', 'refund_request', 'negative'), ('Either cancel {o} today or refund my money — your pick.', 'refund_request', 'neutral'), ('Billed {a} after I already cancelled ({o}). Refund it.', 'refund_request', 'negative'), ('Cancel {o} and explain this mystery {a} charge on my statement.', 'cancellation', 'neutral'), ('I never authorized order {o}: cancel it and refund the {a} now.', 'refund_request', 'negative'), ("My refund for {o} hasn't shown up, so just cancel my other order too.", 'refund_request', 'neutral')]
    if 'none' not in RNG.sample(['x', 'y'], 1):
        RNG.shuffle(mixed_templates)
    for tpl, intent, sent in mixed_templates:
        add('mixed_intent', intent, sent, tpl.format(o=RNG.choice(OIDS), a=RNG.choice(AMTS)))
    polite_templates = [('Would you mind telling me why my delivery is three days late?', 'shipping_delivery'), ('Could someone explain why I was charged twice this month?', 'billing_payments'), ("I'd appreciate an update on my refund; it's been two weeks now.", 'refund_request'), ('May I ask why my parcel never arrived, even though tracking says delivered?', 'shipping_delivery'), ('Could you let me know the status of my refund, please? It seems delayed.', 'refund_request'), ('Would it be possible to check why my card was billed twice for one order?', 'billing_payments'), ("I was wondering why my order still hasn't shipped after ten days.", 'shipping_delivery'), ('Could anyone clarify this unexpected charge on my invoice?', 'billing_payments'), ("I'm a little concerned my refund hasn't reached my account yet.", 'refund_request'), ('Would you be able to tell me why the package is still in transit after a week?', 'shipping_delivery'), ("Excuse me, I think there's a small mistake on my invoice — a duplicate charge.", 'billing_payments'), ("I'm slightly worried: my delivery shows no movement for six days.", 'shipping_delivery'), ('Hello, it seems my refund is taking longer than the promised 5 days.', 'refund_request'), ("I don't mean to trouble you, but the payment went through twice.", 'billing_payments')]
    for tpl, intent in polite_templates:
        add('polite_complaint', intent, 'negative', tpl)
    trap_templates = [('Your refund policy is a joke — I want my {a} back today. Refund order {o}.', 'refund_request'), ('This is ridiculous. Refund my card for order {o} NOW.', 'refund_request'), ('Unacceptable. Cancel order {o} immediately.', 'cancellation'), ("I'm sick of this company. Give me my {a} back for {o} before I call my bank.", 'refund_request'), ('Absolutely pathetic service. Issue the refund for {o} like you promised.', 'refund_request'), ('What a disgrace. Cancel my order {o} right now.', 'cancellation'), ('Worst experience ever. I demand a full refund of {a} for {o}.', 'refund_request'), ("This whole thing is a scam. Refund {o} today or I'm disputing the charge.", 'refund_request'), ('Furious. Cancel {o} and never email me again.', 'cancellation'), ('Your support is useless. Just give me my money back for order {o}.', 'refund_request'), ("I've had it with you people — refund the {a} for {o}.", 'refund_request'), ('Totally outrageous. I want {o} cancelled before it ships.', 'cancellation'), ('This company is a nightmare. Refund my {a} for {o} immediately.', 'refund_request'), ('Never shopping here again. Cancel {o}.', 'cancellation'), ("Beyond angry. Process the refund for {o} or I'm going to my card provider.", 'refund_request'), ('You should be ashamed. Cancel order {o} and confirm it in writing.', 'cancellation')]
    for tpl, intent in trap_templates:
        add('tone_trap', intent, 'negative', tpl.format(o=RNG.choice(OIDS), a=RNG.choice(AMTS)))
    shorts = [("Where's my money?", 'refund_request', 'negative'), ('Charged twice??', 'billing_payments', 'negative'), ('Package. Late. Again.', 'shipping_delivery', 'negative'), ('How do I get a human on the line?', 'other_contact', 'neutral'), ('Money back now.', 'refund_request', 'negative'), ('Why is my card charged?', 'billing_payments', 'neutral'), ('Still no package.', 'shipping_delivery', 'negative'), ('Speak to someone please.', 'other_contact', 'neutral')]
    for text, intent, sent in shorts:
        add('short_fragment', intent, sent, text)
    return rows

def main():
    bitext = pd.read_csv(DATA_DIR / 'raw' / 'bitext_raw.csv').rename(columns={'instruction': 'text'})
    bitext['text'] = bitext['text'].astype(str).str.replace('\\{\\{[^}]*\\}\\}', lambda m: RNG.choice(OIDS + AMTS), regex=True)
    bitext['design_intent'] = bitext['intent'].map(BITEXT_TO_MACRO)
    bitext = bitext.dropna(subset=['design_intent'])
    bitext = bitext.drop_duplicates(subset=['text'])
    organic = []
    for macro, quota in ORGANIC_QUOTA.items():
        pool = bitext[bitext.design_intent == macro]
        take = pool.sample(n=quota, random_state=20260825)
        organic.append(take[['text', 'design_intent']])
    organic = pd.concat(organic)
    organic['source'] = 'bitext'
    organic['ambiguity_type'] = 'none'
    organic['augmentation'] = 'none'
    wrap_idx = []
    for macro in INTENT_CLASSES:
        pool = organic[organic.design_intent == macro].index.tolist()
        RNG.shuffle(pool)
        wrap_idx += pool[:15]
    for k, idx in enumerate(wrap_idx):
        text = organic.at[idx, 'text']
        f = featurize(text)
        if k % 2 == 0:
            if f['anger_hits'] or f['negweak_hits'] or f['pos_hits']:
                continue
            tpl = POS_WRAPS[k % len(POS_WRAPS)]
            organic.at[idx, 'text'] = tpl.format(t=text[0].lower() + text[1:])
            organic.at[idx, 'augmentation'] = 'pos_wrap'
        else:
            if f['pos_hits'] or f['anger_hits']:
                continue
            tpl = NEG_WRAPS[k % len(NEG_WRAPS)]
            organic.at[idx, 'text'] = tpl.format(t=text[0].lower() + text[1:])
            organic.at[idx, 'augmentation'] = 'neg_wrap'
    injected = pd.DataFrame(injected_rows())
    injected['design_intent'] = injected['true_intent']
    injected['augmentation'] = 'none'
    assert len(injected) == 24 + 18 + 14 + 16 + 8, len(injected)
    corpus = pd.concat([organic[['text', 'source', 'design_intent', 'ambiguity_type', 'augmentation']], injected[['text', 'source', 'design_intent', 'ambiguity_type', 'augmentation']]]).reset_index(drop=True)
    corpus['design_sentiment'] = corpus['text'].map(design_sentiment)
    truth = {r['text']: r['true_sentiment'] for _, r in injected.iterrows()}
    corpus.loc[corpus.text.isin(truth), 'design_sentiment'] = corpus.loc[corpus.text.isin(truth), 'text'].map(truth)
    corpus.loc[corpus.augmentation == 'neg_wrap', 'design_sentiment'] = 'negative'
    corpus.loc[corpus.augmentation == 'pos_wrap', 'design_sentiment'] = 'positive'

    def borderline(row):
        if row['ambiguity_type'] != 'none':
            return True
        f = featurize(row['text'])
        return f['n_groups'] > 1 or f['sarcasm_cue']
    corpus['borderline'] = corpus.apply(borderline, axis=1)
    corpus = corpus.sample(frac=1.0, random_state=7).reset_index(drop=True)
    corpus.insert(0, 'ticket_id', [f'GF-{i + 1:04d}' for i in range(len(corpus))])
    rng = random.Random(99)
    gold_idx = []
    sent_pref_order = ['negative', 'positive', 'neutral']
    for macro in INTENT_CLASSES:
        pool = corpus[(corpus.design_intent == macro) & ~corpus.borderline & (corpus.source == 'bitext')]
        cands = []
        for i in pool.index:
            text, sent = (corpus.at[i, 'text'], corpus.at[i, 'design_sentiment'])
            f = featurize(text)
            if macro not in f['intent_hits']:
                continue
            if not sentiment_is_clear(text, sent):
                continue
            cands.append((i, sent, RNG.random()))
        chosen, have = ([], set())
        for sent_want in sent_pref_order:
            for i, sent, _ in sorted(cands, key=lambda c: c[2]):
                if len(chosen) >= 6:
                    break
                if sent == sent_want and (sent not in have or len(chosen) >= 3):
                    chosen.append(i)
                    have.add(sent)
        for i, sent, _ in sorted(cands, key=lambda c: c[2]):
            if len(chosen) >= 6:
                break
            if i not in chosen:
                chosen.append(i)
        gold_idx += chosen[:6]
    inj_gold = {'sarcasm': 6, 'mixed_intent': 6, 'polite_complaint': 4, 'tone_trap': 6, 'short_fragment': 2}
    for amb, k in inj_gold.items():
        pool = corpus[corpus.ambiguity_type == amb].index.tolist()
        rng.shuffle(pool)
        gold_idx += pool[:k]
    assert len(gold_idx) == 72, len(gold_idx)
    calib_idx = []
    for macro in INTENT_CLASSES:
        pool = corpus[(corpus.design_intent == macro) & ~corpus.index.isin(gold_idx)].index.tolist()
        rng.shuffle(pool)
        calib_idx += pool[:4]
    for amb, k in {'sarcasm': 4, 'mixed_intent': 4, 'polite_complaint': 2, 'tone_trap': 4, 'short_fragment': 2}.items():
        pool = corpus[(corpus.ambiguity_type == amb) & ~corpus.index.isin(gold_idx) & ~corpus.index.isin(calib_idx)].index.tolist()
        rng.shuffle(pool)
        calib_idx += pool[:k]
    calib_idx = calib_idx[:48]
    assert len(set(calib_idx)) == 48
    assert set(calib_idx).isdisjoint(gold_idx)
    corpus['is_gold'] = corpus.index.isin(gold_idx)
    corpus['is_calibration'] = corpus.index.isin(calib_idx)
    corpus['batch'] = RNG.sample(['B1'] * 150 + ['B2'] * 150 + ['B3'] * 150 + ['B4'] * 150, 600)
    (DATA_DIR / 'raw').mkdir(parents=True, exist_ok=True)
    corpus.to_csv(DATA_DIR / 'raw' / 'support_tickets.csv', index=False)
    gold = corpus[corpus.is_gold].copy()
    gold = gold[['ticket_id', 'text', 'design_intent', 'design_sentiment', 'ambiguity_type']].rename(columns={'design_intent': 'gold_intent', 'design_sentiment': 'gold_sentiment'})
    gold.to_csv(DATA_DIR / 'gold_set.csv', index=False)
    peer_dir = DATA_DIR / 'for_peer_annotation'
    peer_dir.mkdir(parents=True, exist_ok=True)
    for name in ['annotator_sheet_1.csv', 'annotator_sheet_2.csv', 'annotator_sheet_3.csv']:
        corpus[['ticket_id', 'text']].assign(intent_label='', sentiment_label='').to_csv(peer_dir / name, index=False)
    print(f"corpus: {len(corpus)} tickets | augmented: {(corpus.augmentation != 'none').sum()}")
    print(corpus.design_intent.value_counts().to_string())
    print('\nsentiment design distribution:')
    print(corpus.design_sentiment.value_counts().to_string())
    print(f'\ngold: {len(gold)} | calibration: {corpus.is_calibration.sum()} | borderline: {corpus.borderline.sum()}')
    print('\n--- cue sanity on injected families ---')
    for amb in ['sarcasm', 'mixed_intent', 'polite_complaint', 'tone_trap', 'short_fragment']:
        sub = corpus[corpus.ambiguity_type == amb]
        cues = sub.text.map(lambda t: featurize(t))
        print(f"{amb:>17s}: n={len(sub)}  sarcasm_cue={sum((c['sarcasm_cue'] for c in cues))}/{len(sub)}  multi_intent={sum((c['n_groups'] > 1 for c in cues))}/{len(sub)}  frame={sum((c['frame_hits'] > 0 for c in cues))}/{len(sub)}")
    print('\n--- gold sentiment counts ---')
    print((gold_cols := gold.gold_sentiment.value_counts().to_string()))
    print('\n--- GOLD SET (eyeball-verification print) ---')
    for _, r in gold.sort_values(['gold_intent', 'gold_sentiment']).iterrows():
        print(f'[{r.gold_intent:>20s} | {r.gold_sentiment:>8s}] {r.text[:95]}')
if __name__ == '__main__':
    main()
