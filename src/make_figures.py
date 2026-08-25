import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from chart_style import base_rc, titles, source, dumbbell, legend_strip, legend_in_ax, PAPER, CARD, INK, MUTE, HAIR, GRID, R1C, R2C, GOOD, BAD, AMBER, SLATE, CMAP_HEAT, CMAP_CONF, SERIF, MONO
M = json.load(open('results/metrics.json'))
r1, r2, qa, cf = (M['R1'], M['R2'], M['qa'], M['counterfactual_v1_cost'])
FIG = 'results/figures'
base_rc()
SRC = 'Source: data/annotations/annotations_round{1,2}.csv · blind overlap n=180, 3 annotators · recomputed from raw labels'

def save(fig, name):
    fig.savefig(f'{FIG}/{name}.png', dpi=150, facecolor=PAPER)
    plt.close(fig)
    print('wrote', f'{FIG}/{name}.png')

def fig_headline():
    metrics = [("Fleiss' κ — intent", 'fleiss_intent'), ("Fleiss' κ — sentiment", 'fleiss_sentiment'), ('Krippendorff α — sentiment (ordinal)', 'alpha_sentiment_ordinal'), ("Cohen's κ (mean) — intent", 'cohen_mean_intent'), ("Cohen's κ (mean) — sentiment", 'cohen_mean_sentiment')]
    labels = [m for m, _ in metrics]
    v1 = [r1[k] for _, k in metrics]
    v2 = [r2[k] for _, k in metrics]
    fig = plt.figure(figsize=(9.4, 4.6))
    ax = fig.add_axes([0.27, 0.14, 0.52, 0.62])
    dumbbell(ax, labels, v1, v2, target=0.8, xlim=(0.3, 1.04), delta_at=1.055)
    titles(fig, ax, 'fig. 01 · inter-annotator agreement', 'A passable average, repaired', 'before/after the v2.0 guideline revision — delta at right')
    legend_strip(fig, 0.24, 0.062, [(R1C, False, 'Round 1 (v1.0)'), (R2C, True, 'Round 2 (v2.0)')])
    source(fig, SRC + ' — 95% bootstrap CIs on intent κ: R1 [0.78, 0.88] · R2 [0.93, 0.98]')
    save(fig, 'fig_headline')

def fig_perclass():
    pc1, pc2 = (r1['per_class_intent_kappa'], r2['per_class_intent_kappa'])
    order = sorted(pc1, key=pc1.get)
    v1 = [pc1[c] for c in order]
    v2 = [pc2[c] for c in order]
    fig = plt.figure(figsize=(9.4, 5.0))
    ax = fig.add_axes([0.24, 0.12, 0.555, 0.64])
    dumbbell(ax, order, v1, v2, target=0.8, xlim=(0.4, 1.06), delta_at=1.075)
    titles(fig, ax, 'fig. 02 · per-class intent agreement', 'Which classes carried the failure', "one-vs-rest Cohen's κ, mean across the three annotator pairs")
    legend_in_ax(ax, 0.415, 0.3, [(R1C, False, 'Round 1 (v1.0)'), (R2C, True, 'Round 2 (v2.0)')], step=0.5)
    source(fig, SRC)
    save(fig, 'fig_perclass')

def fig_slices():
    fams = ['sarcasm', 'mixed_intent', 'polite_complaint', 'tone_trap', 'short_fragment', 'none']
    labels = ['sarcasm', 'mixed', 'polite', 'anger', 'short', 'organic']
    mat = np.array([[r1['slices'][f]['unanimous_intent'], r1['slices'][f]['unanimous_sentiment'], r2['slices'][f]['unanimous_intent'], r2['slices'][f]['unanimous_sentiment']] for f in fams]).T
    fig = plt.figure(figsize=(9.4, 4.2))
    ax = fig.add_axes([0.135, 0.165, 0.73, 0.58])
    im = ax.imshow(mat, cmap=CMAP_HEAT, vmin=0, vmax=1, aspect='auto')
    ax.set_xticks(range(len(fams)))
    ax.set_xticklabels([f"{l}\n(n={r1['slices'][f]['n']})" for l, f in zip(labels, fams)], fontsize=8.2)
    ax.set_yticks(range(4))
    ax.set_yticklabels(['intent — R1', 'sentiment — R1', 'intent — R2', 'sentiment — R2'], fontsize=9)
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color(HAIR)
    ax.grid(False)
    ax.set_xticks(np.arange(-0.5, len(fams), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, 4, 1), minor=True)
    ax.grid(which='minor', color=PAPER, linewidth=2.5)
    ax.tick_params(which='minor', length=0)
    for i in range(4):
        for j in range(len(fams)):
            ax.text(j, i, f'{mat[i, j]:.2f}', ha='center', va='center', family=MONO, fontsize=9, color=INK if 0.3 < mat[i, j] < 0.85 else 'white')
    cb = fig.colorbar(im, ax=ax, shrink=0.85, pad=0.015, fraction=0.05)
    cb.outline.set_color(HAIR)
    cb.ax.tick_params(labelsize=7.5, colors=MUTE)
    cb.set_label('share of tickets unanimous', fontsize=7.8, color=MUTE)
    titles(fig, ax, 'fig. 03 · slice-level unanimity', 'The disagreement map', 'families: sarcasm · mixed-intent · polite complaint · anger-framed request · short fragment · organic')
    source(fig, SRC)
    save(fig, 'fig_slices')

def fig_gold():
    names = [('A1', 'Priya — careful literalist'), ('A2', 'Marcus — empathetic reader'), ('A3', 'Tom — fast skimmer')]
    fig = plt.figure(figsize=(9.4, 4.3))
    axes = [fig.add_axes([0.34, 0.24, 0.285, 0.5]), fig.add_axes([0.7, 0.24, 0.255, 0.5])]
    for ax, task, ttl in [(axes[0], 'intent_acc', 'intent'), (axes[1], 'sentiment_acc', 'sentiment')]:
        v1 = [r1['gold_accuracy'][k][task] for k, _ in names]
        v2 = [r2['gold_accuracy'][k][task] for k, _ in names]
        dumbbell(ax, [''] * 3, v1, v2, target=0.9, xlim=(0.53, 1.085), delta_at=1.095)
        ax.set_title(ttl, family=SERIF, fontsize=11, color=INK, pad=8)
    axes[0].set_yticks(range(3)[::-1])
    axes[0].set_yticklabels([n for _, n in names], fontsize=8.2)
    axes[0].set_xlabel('accuracy vs gold (72 items)', fontsize=8)
    axes[1].set_xlabel('accuracy vs gold', fontsize=8)
    fig.text(0.34, 0.905, 'FIG. 04 · GROUND-TRUTH ACCURACY', family=MONO, fontsize=7.5, color=MUTE)
    fig.text(0.34, 0.862, 'Consensus is not correctness', family=SERIF, fontsize=14.5, fontweight='bold')
    fig.text(0.34, 0.822, 'per-annotator accuracy on the embedded gold set — the QA floor at 0.90 is where retraining triggers', fontsize=8.6, color=MUTE, style='italic')
    legend_strip(fig, 0.4, 0.115, [(R1C, False, 'Round 1'), (R2C, True, 'Round 2')])
    source(fig, 'Source: data/gold_set.csv × annotations rounds 1–2 · annotators never saw gold flags')
    save(fig, 'fig_gold')

def fig_trend():
    t1, t2 = (r1['fleiss_intent_by_batch'], r2['fleiss_intent_by_batch'])
    xs = [1, 2, 3, 4, 6, 7, 8, 9]
    ys = [t1['B1'], t1['B2'], t1['B3'], t1['B4'], t2['B1'], t2['B2'], t2['B3'], t2['B4']]
    fig = plt.figure(figsize=(9.4, 4.0))
    ax = fig.add_axes([0.075, 0.135, 0.83, 0.6])
    ax.axvspan(4.55, 5.45, color='#efe7d2', zorder=0)
    ax.text(5.0, 0.52, 'revision week\nguidelines v1.0 → v2.0\n+ recertification', ha='center', family=MONO, fontsize=7.2, color='#8a7a45')
    ax.plot(xs, ys, color=INK, lw=1.6, marker='o', ms=5.5, markerfacecolor='white', markeredgecolor=INK, zorder=3)
    for x, y in zip(xs, ys):
        ax.annotate(f'{y:.2f}', (x, y), textcoords='offset points', xytext=(0, 8), ha='center', family=MONO, fontsize=7.6, color=MUTE)
    ax.axhline(0.8, color=BAD, lw=1.0, ls=(0, (4, 2)))
    ax.text(9.05, 0.804, 'target 0.80', color=BAD, family=MONO, fontsize=7.4, va='bottom')
    ax.text(1.0, ys[0] - 0.085, 'R1 starts', fontsize=7.6, color=MUTE)
    ax.text(8.95, ys[-1] - 0.105, 'R2 ends', fontsize=7.6, color=GOOD, ha='right')
    ax.set_xticks(xs)
    ax.set_xticklabels(['wk 1', 'wk 2', 'wk 3', 'wk 4', 'wk 6', 'wk 7', 'wk 8', 'wk 9'], fontsize=8)
    ax.set_ylim(0.42, 1.06)
    ax.set_xlim(0.6, 9.4)
    ax.set_ylabel("Fleiss' κ — intent")
    titles(fig, ax, 'fig. 05 · weekly batches', 'The revision held — every week after it', "each point = that week batch's 45-ticket overlap slice; revision week shaded")
    source(fig, SRC)
    save(fig, 'fig_trend')

def fig_confusion():
    corpus = pd.read_csv('data/raw/support_tickets.csv')
    ann1 = pd.read_csv('data/annotations/annotations_round1.csv')
    ov_ids = corpus[corpus.in_overlap].ticket_id
    piv = ann1[ann1.ticket_id.isin(ov_ids)].pivot(index='ticket_id', columns='annotator', values='intent')
    CL = sorted(set(piv.A1) | set(piv.A3))
    cm = np.zeros((len(CL), len(CL)), dtype=int)
    for _, r in piv.iterrows():
        cm[CL.index(r.A1), CL.index(r.A3)] += 1
    short = {'refund_request': 'refund', 'cancellation': 'cancel', 'billing_payments': 'billing', 'shipping_delivery': 'shipping', 'order_changes': 'order chg.', 'account_access': 'account', 'feedback_complaints': 'feedback', 'other_contact': 'other'}
    fig = plt.figure(figsize=(7.9, 6.4))
    ax = fig.add_axes([0.135, 0.205, 0.72, 0.58])
    im = ax.imshow(cm, cmap=CMAP_CONF, vmin=0, vmax=cm.max())
    ax.set_xticks(range(len(CL)))
    ax.set_xticklabels([short[c] for c in CL], rotation=38, ha='right', fontsize=8.4)
    ax.set_xlabel('Tom (A3) — fast', fontsize=9, labelpad=6)
    ax.set_yticks(range(len(CL)))
    ax.set_yticklabels([short[c] for c in CL], fontsize=8.4)
    ax.grid(False)
    ax.set_xticks(np.arange(-0.5, len(CL), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(CL), 1), minor=True)
    ax.grid(which='minor', color=PAPER, linewidth=2)
    ax.tick_params(which='minor', length=0)
    for i in range(len(CL)):
        for j in range(len(CL)):
            if cm[i, j]:
                ax.text(j, i, str(cm[i, j]), ha='center', va='center', family=MONO, fontsize=8.4, color='white' if cm[i, j] > cm.max() * 0.55 else INK)
    fig.text(0.135, 0.935, 'FIG. 06 · ANNOTATOR × ANNOTATOR, ROUND 1', family=MONO, fontsize=7.5, color=MUTE)
    fig.text(0.135, 0.893, 'Off-diagonal ink is the argument', family=SERIF, fontsize=14.5, fontweight='bold')
    fig.text(0.135, 0.858, 'rows: Priya (careful) · columns: Tom (fast) · n=180 blind overlap · cancel–refund–billing mass =', fontsize=8.4, color=MUTE, style='italic')
    fig.text(0.135, 0.833, 'guideline ambiguity · scattered singles = skim errors', fontsize=8.4, color=MUTE, style='italic')
    ax.set_ylabel('Priya (A1) — careful', fontsize=9)
    source(fig, SRC)
    save(fig, 'fig_confusion')

def fig_qa():
    fig = plt.figure(figsize=(9.4, 4.3))
    ax1 = fig.add_axes([0.175, 0.165, 0.33, 0.56])
    ax2 = fig.add_axes([0.635, 0.165, 0.325, 0.56])
    rb = {k: v for k, v in sorted(qa['rework_by_class_intent'].items(), key=lambda kv: -kv[1]) if v > 0}
    y = np.arange(len(rb))[::-1]
    ax1.barh(y, list(rb.values()), height=0.62, color=SLATE, zorder=3)
    for yi, v in zip(y, rb.values()):
        ax1.text(v + 0.004, yi, f'{v:.1%}', va='center', family=MONO, fontsize=8.2, color=INK)
    ax1.axvline(0.15, color=BAD, lw=1.0, ls=(0, (4, 2)))
    ax1.text(0.97, 0.055, 'industry ceiling 15–20% ', transform=ax1.transAxes, color=BAD, ha='right', family=MONO, fontsize=7.4)
    ax1.set_yticks(y, list(rb.keys()), fontsize=8.4)
    ax1.set_xlim(0, 0.185)
    ax1.set_title('Rework by class — Tier-2 review (R2)', family=SERIF, fontsize=11, pad=8)
    ax1.set_xlabel('share of labels corrected', fontsize=8)
    ax1.grid(axis='y', visible=False)
    cats = ['R1 intents\nmis-routed*', 'R1 sentiments\ncorrected*', 'R2 rework\n(intent)', 'R2 rework\n(sentiment)']
    vals = [cf['r1_production_intents_misrouted_under_v2'], cf['r1_production_sentiments_corrected_under_v2'], qa['rework_rate_intent'], qa['rework_rate_sentiment']]
    cols = [BAD, BAD, GOOD, GOOD]
    x = np.arange(4)
    ax2.bar(x, vals, width=0.56, color=cols, zorder=3)
    for xi, v in zip(x, vals):
        ax2.text(xi, v + 0.003, f'{v:.1%}', ha='center', family=MONO, fontsize=8.4, color=INK)
    ax2.set_xticks(x, cats, fontsize=8.2)
    ax2.set_ylim(0, max(vals) * 1.25)
    ax2.set_title('What v1.0 cost — vs. the v2.0 steady state', family=SERIF, fontsize=11, pad=8)
    fig.text(0.1, 0.9, 'FIG. 07 · QUALITY-ASSURANCE ECONOMICS', family=MONO, fontsize=7.5, color=MUTE)
    fig.text(0.1, 0.855, 'The steady state is boring — by design', family=SERIF, fontsize=14.5, fontweight='bold')
    source(fig, 'Source: data/adjudicated_labels.csv · data/qa_audit_results.csv · Tier-3 audit 117/117 passed · *counterfactual: v2 rules replayed on R1 production labels')
    save(fig, 'fig_qa')

def fig_throughput():
    tl = pd.read_csv('results/timeline.csv', parse_dates=['date'])
    pretty = {'A1': 'Priya — careful', 'A2': 'Marcus — empathetic', 'A3': 'Tom — fast'}
    styles = {'A1': INK, 'A2': SLATE, 'A3': AMBER}
    rev = pd.Timestamp('2026-07-27')
    fig = plt.figure(figsize=(9.4, 5.2))
    ymax = 690
    for k, p in enumerate(['A1', 'A2', 'A3']):
        ax = fig.add_axes([0.105, 0.66 - k * 0.265, 0.7, 0.185])
        for q in ['A1', 'A2', 'A3']:
            sub_q = tl[tl.annotator == q].sort_values('date')
            ax.plot(sub_q.date, sub_q.tasks_completed.cumsum(), color=HAIR, lw=1.0, zorder=2)
        sub = tl[tl.annotator == p].sort_values('date')
        cum = sub.tasks_completed.cumsum()
        ax.plot(sub.date, cum, color=styles[p], lw=2.0, zorder=3)
        ax.axvspan(rev, rev + pd.Timedelta(days=4.2), color='#efe7d2', zorder=0)
        ax.text(rev + pd.Timedelta(days=5), ymax * 0.06, 'revision week' if k == 0 else '', family=MONO, fontsize=6.8, color='#8a7a45', va='bottom')
        ax.text(sub.date.iloc[-1] + pd.Timedelta(days=2), cum.iloc[-1], f'{pretty[p]} · {int(cum.iloc[-1])}', va='center', family=MONO, fontsize=7.8, color=styles[p])
        ax.set_ylim(0, ymax)
        ax.set_xlim(sub.date.min() - pd.Timedelta(days=1), pd.Timestamp('2026-09-14'))
        ax.grid(axis='x', visible=False)
        if k < 2:
            ax.set_xticklabels([])
        ax.set_yticks([0, 320, 640])
        ax.tick_params(axis='y', labelsize=7.5)
    fig.text(0.105, 0.945, 'FIG. 08 · THROUGHPUT', family=MONO, fontsize=7.5, color=MUTE)
    fig.text(0.105, 0.905, 'Nine weeks, three workstations', family=SERIF, fontsize=14.5, fontweight='bold')
    fig.text(0.105, 0.872, 'cumulative labels per annotator (ghost lines = the other two) — totals reconcile 1:1 with the label files', fontsize=8.6, color=MUTE, style='italic')
    source(fig, 'Source: results/timeline.csv — per-round daily counts sum exactly to data/annotations/annotations_round{1,2}.csv (assert-checked)')
    save(fig, 'fig_throughput')
if __name__ == '__main__':
    fig_headline()
    fig_perclass()
    fig_slices()
    fig_gold()
    fig_trend()
    fig_confusion()
    fig_qa()
    fig_throughput()
    print('all figures written (editorial system)')
