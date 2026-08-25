import argparse
import json
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / 'data'
VALID_INTENTS = {'refund_request', 'cancellation', 'billing_payments', 'shipping_delivery', 'order_changes', 'account_access', 'feedback_complaints', 'other_contact'}
VALID_SENTIMENTS = {'negative', 'neutral', 'positive'}

def export_tasks():
    corpus = pd.read_csv(DATA_DIR / 'raw' / 'support_tickets.csv')
    tasks = [{'id': i + 1, 'data': {'ticket_id': r.ticket_id, 'text': r.text}} for i, r in enumerate(corpus.itertuples())]
    out_file = DATA_DIR / 'label_studio_import.json'
    with open(out_file, 'w') as fh:
        json.dump(tasks, fh, indent=1)
    print(f'wrote {out_file} ({len(tasks)} tasks) — import into Label Studio via cloud storage URL or file upload')

def ingest(export_path, annotator, rnd):
    raw = json.load(open(export_path))
    rows, skipped = ([], 0)
    for task in raw:
        tid = task['data']['ticket_id']
        anns = task.get('annotations', [])
        if not anns:
            skipped += 1
            continue
        res = anns[-1]['result']
        lab = {r['from_name']: r['value']['choices'][0] for r in res if r['type'] == 'choices'}
        intent, sent = (lab.get('intent'), lab.get('sentiment'))
        if intent not in VALID_INTENTS or sent not in VALID_SENTIMENTS:
            skipped += 1
            continue
        rows.append({'round': f'R{rnd}', 'ticket_id': tid, 'annotator': annotator, 'intent': intent, 'sentiment': sent, 'role': 'label_studio'})
    df = pd.DataFrame(rows)
    out = DATA_DIR / 'annotations' / f'annotations_ls_{annotator}_round{rnd}.csv'
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f'wrote {out}: {len(df)} labels ingested, {skipped} skipped')
    print('→ point src/import_peer_labels.py at this CSV to recompute the full agreement battery')
if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['export', 'ingest'])
    ap.add_argument('export_file', nargs='?', default=None)
    ap.add_argument('--annotator', default='annotator1')
    ap.add_argument('--round', type=int, default=1)
    a = ap.parse_args()
    if a.mode == 'export':
        export_tasks()
    else:
        assert a.export_file, 'ingest requires the LS export file path'
        ingest(a.export_file, a.annotator, a.round)
