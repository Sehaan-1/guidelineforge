import json
import pathlib
import pandas as pd
import streamlit as st
ROOT = pathlib.Path(__file__).resolve().parent.parent
M = json.loads((ROOT / 'results/metrics.json').read_text())
r1, r2, qa, cf = (M['R1'], M['R2'], M['qa'], M['counterfactual_v1_cost'])
FIG = ROOT / 'results' / 'figures'
st.set_page_config(page_title='GuidelineForge — QA dashboard', page_icon='📏', layout='wide')
st.markdown('\n<style>\n:root{\n  --paper:#f7f6f1; --card:#fffdf8; --ink:#1d1d1b; --mute:#77716a;\n  --hair:#d9d5ca; --r2:#2f4a3e; --good:#3a6d51; --bad:#b23a2c;\n}\n.stApp{background:var(--paper);color:var(--ink);\n  font-family:Georgia,\'Times New Roman\',serif}\n[data-testid="stHeader"]{background:rgba(247,246,241,.85);backdrop-filter:blur(4px)}\n.block-container{max-width:1120px;padding-top:5rem}\nh1,h2,h3{font-family:Georgia,\'Times New Roman\',serif!important;\n  color:var(--ink);letter-spacing:-.012em}\nh1{font-weight:700!important}\np,li,label,.stMarkdown{font-family:Georgia,serif}\n[data-testid="stCaptionContainer"], .stCaption,\n[data-testid="stMetricLabel"]{\n  font-family:-apple-system,\'Segoe UI\',Roboto,sans-serif!important;\n  color:var(--mute)!important}\n[data-testid="stMetricValue"]{font-family:Georgia,serif!important;\n  color:var(--ink)}\n[data-testid="metric-container"]{background:var(--card);\n  border:1px solid var(--hair);border-top:3px solid var(--ink);\n  padding:14px 16px 10px;border-radius:0}\n[data-testid="stMetricDelta"] svg{display:none}\n.stTabs [data-baseweb="tab-list"]{gap:26px;border-bottom:1px solid var(--hair)}\n.stTabs [data-baseweb="tab"]{font-family:-apple-system,\'Segoe UI\',Roboto,sans-serif;\n  font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--mute);\n  background:none;border:none}\n.stTabs [aria-selected="true"]{color:var(--ink)!important;\n  border-bottom:2px solid var(--ink)!important}\n.stTabs [data-baseweb="tab-highlight"]{background:var(--ink)}\n[data-testid="stAlert"]{background:var(--card);border:1px solid var(--ink);\n  border-left:5px solid var(--bad);border-radius:0;color:var(--ink)}\n[data-testid="stDataFrame"]{border:1px solid var(--hair)}\nhr{border-color:var(--hair)}\n.gf-kicker{font:600 11px -apple-system,\'Segoe UI\',Roboto,sans-serif;\n  letter-spacing:.17em;text-transform:uppercase;color:var(--ink);\n  border-bottom:1px solid var(--ink);padding-bottom:8px;margin-bottom:2px}\n.gf-kicker span{color:var(--mute);float:right;letter-spacing:.12em}\n.gf-alert{background:var(--card);border:1px solid var(--ink);\n  border-left:5px solid var(--bad);padding:16px 22px;margin:14px 0 6px;\n  font:14.5px/1.6 Georgia,serif;color:var(--ink)}\n.gf-alert .tag{font:600 10px/1 -apple-system,\'Segoe UI\',Roboto,sans-serif;\n  letter-spacing:.13em;text-transform:uppercase;color:var(--bad);\n  display:block;margin-bottom:7px}\n</style>\n', unsafe_allow_html=True)
st.markdown('<div class="gf-kicker">GuidelineForge · annotation quality program<span>weekly ops view</span></div>', unsafe_allow_html=True)
st.title('Annotation QA — the week in labels')
st.caption('600 support tickets · intent (8) + sentiment (ord-3) · 3 annotators, 180-ticket blind overlap · guidelines v1.0 → v2.0 · program 2026-06-29 → 2026-08-24')
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric('Fleiss κ — intent', f"{r2['fleiss_intent']:.2f}", f"+{r2['fleiss_intent'] - r1['fleiss_intent']:.2f} vs R1")
c2.metric('Fleiss κ — sentiment', f"{r2['fleiss_sentiment']:.2f}", f"+{r2['fleiss_sentiment'] - r1['fleiss_sentiment']:.2f} vs R1")
c3.metric('α ordinal — sentiment', f"{r2['alpha_sentiment_ordinal']:.2f}", f"+{r2['alpha_sentiment_ordinal'] - r1['alpha_sentiment_ordinal']:.2f}")
c4.metric('Rework rate', f"{qa['rework_rate_either']:.1%}", 'ceiling 15–20%', delta_color='off')
c5.metric('Audit pass', f"{qa['tier3_audit']['pass_rate_overall']:.0%}", f"n={qa['tier3_audit']['n']}", delta_color='off')
st.markdown(f"""<div class="gf-alert"><span class="tag">Round-1 alarm — the tone trap</span>Anger-framed action requests were <b>{r1['tone_trap_slice']['unanimous_agreement']:.0%} unanimous but only ~25% correct vs gold</b> — the crew agreeing on a wrong rule. Inter-annotator agreement alone would have shipped it; the gold set caught it.</div>""", unsafe_allow_html=True)
tab1, tab2, tab3, tab4, tab5 = st.tabs(['Overview', 'Disagreement anatomy', 'Gold & people', 'QA & throughput', 'Data explorer'])
with tab1:
    st.image(str(FIG / 'fig_headline.png'))
    st.image(str(FIG / 'fig_trend.png'))
    st.markdown('- Overall intent κ was already ≥ 0.80 in Round 1 — **the average lied**: sentiment and three language families were failing underneath.\n- After the v2.0 revision (+ recertification), every metric clears the 0.80 bar with disjoint bootstrap CIs.')
with tab2:
    st.image(str(FIG / 'fig_slices.png'))
    col_a, col_b = st.columns(2)
    with col_a:
        st.image(str(FIG / 'fig_perclass.png'))
    with col_b:
        st.image(str(FIG / 'fig_confusion.png'))
    st.markdown("The off-diagonal mass concentrates on **cancel ⇄ refund ⇄ billing** (mixed intents) — a tie-breaking-rule defect, not a taxonomy defect. That's why the fix was a precedence hierarchy, not new classes.")
with tab3:
    st.image(str(FIG / 'fig_gold.png'))
    ga = pd.DataFrame({'annotator': ['A1 (careful)', 'A2 (empathetic)', 'A3 (fast)'], 'gold intent R1': [r1['gold_accuracy'][p]['intent_acc'] for p in ['A1', 'A2', 'A3']], 'gold intent R2': [r2['gold_accuracy'][p]['intent_acc'] for p in ['A1', 'A2', 'A3']], 'gold sentiment R1': [r1['gold_accuracy'][p]['sentiment_acc'] for p in ['A1', 'A2', 'A3']], 'gold sentiment R2': [r2['gold_accuracy'][p]['sentiment_acc'] for p in ['A1', 'A2', 'A3']]}).set_index('annotator')
    st.dataframe(ga.style.format('{:.3f}'), width='stretch')
    st.markdown('**Counter-intuitive Round-1 fact:** the careful literalist scored *worse* than the empathetic skimmer on gold intent — diligence applied to a flawed rule just executes the flaw more reliably.')
    st.subheader('Gold-intent accuracy over time (weekly batches)')
    g1, g2 = (r1['gold_intent_acc_by_batch'], r2['gold_intent_acc_by_batch'])
    weeks = ['wk1', 'wk2', 'wk3', 'wk4', 'wk6', 'wk7', 'wk8', 'wk9']
    gb = pd.DataFrame({'A1': [g1.get(b, {}).get('A1') for b in ['B1', 'B2', 'B3', 'B4']] + [g2.get(b, {}).get('A1') for b in ['B1', 'B2', 'B3', 'B4']], 'A2': [g1.get(b, {}).get('A2') for b in ['B1', 'B2', 'B3', 'B4']] + [g2.get(b, {}).get('A2') for b in ['B1', 'B2', 'B3', 'B4']], 'A3': [g1.get(b, {}).get('A3') for b in ['B1', 'B2', 'B3', 'B4']] + [g2.get(b, {}).get('A3') for b in ['B1', 'B2', 'B3', 'B4']]}, index=weeks)
    st.line_chart(gb)
    st.caption('Revision week (wk5) not shown — no production labeling.')
with tab4:
    st.image(str(FIG / 'fig_qa.png'))
    st.image(str(FIG / 'fig_throughput.png'))
    st.markdown(f"- Tier-2 reviewed **100% of {qa['tier2_review_volume']['prod_reviewed']} production labels** + {qa['tier2_review_volume']['ov_reviewed']} non-unanimous overlap tickets.\n- Rework {qa['rework_rate_intent']:.1%} intent / {qa['rework_rate_sentiment']:.1%} sentiment (ceiling 15–20%).\n- Final labels vs gold: **{qa['final_gold_intent_acc']:.3f} intent**, **{qa['final_gold_sentiment_acc']:.3f} sentiment**.\n- Counterfactual v1 cost: {cf['r1_production_intents_misrouted_under_v2']:.1%} of R1 production intents mis-routed; {cf['r1_production_sentiments_corrected_under_v2']:.1%} sentiments corrected.")
with tab5:
    corpus = pd.read_csv(ROOT / 'data/raw/support_tickets.csv')
    final = pd.read_csv(ROOT / 'data/adjudicated_labels.csv')
    st.subheader('Corpus with final adjudicated labels')
    fam = st.multiselect('ticket family', sorted(corpus.ambiguity_type.unique()), default=sorted(corpus.ambiguity_type.unique()))
    view = corpus[corpus.ambiguity_type.isin(fam)].merge(final[['ticket_id', 'final_intent', 'final_sentiment', 'intent_rework', 'sentiment_rework']], on='ticket_id')
    view['changed_in_QA'] = view.intent_rework | view.sentiment_rework
    view = view.rename(columns={'ambiguity_type': 'family'})
    st.dataframe(view[['ticket_id', 'text', 'family', 'final_intent', 'final_sentiment', 'is_gold', 'in_overlap', 'changed_in_QA']], width='stretch', height=420)
    st.caption(f"{len(view)} rows shown · {int(view['changed_in_QA'].sum())} changed during Tier-2 review")
st.divider()
st.caption('Simulation disclosure: annotators are documented seeded persona engines acting on observable text cues only. Real peer labels can be imported via data/for_peer_annotation/ + src/import_peer_labels.py — every chart recomputes unchanged.')
