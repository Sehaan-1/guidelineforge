from dataclasses import dataclass, field
import random
from text_features import featurize, V2_INTENT_PRIORITY
CLASSES = ['refund_request', 'cancellation', 'billing_payments', 'shipping_delivery', 'order_changes', 'account_access', 'feedback_complaints', 'other_contact']
SENTIMENTS = ['negative', 'neutral', 'positive']
POLICY_CUES = ['policy', 'guarantee', 'in what situations', 'allowed to', 'what is your', 'how does your', 'money back guarantee', 'resititution', 'restitution policy']

@dataclass
class Persona:
    key: str
    display: str
    style: str
    tone_p: dict
    priority_p: dict
    first_bonus: dict
    priority_bonus: dict
    refund_prior: dict
    empathy_feedback: dict
    clear_flip: dict
    random_intent_p: dict
    policy_p: dict
    sarcasm_neg_p: dict
    polite_neg_p: dict
    failure_neg_p: dict
    pos_w: float = 1.0
    anger_w: float = 1.0
    nw_w: float = 0.55
    sent_noise: dict = field(default_factory=lambda: {1: 0.02, 2: 0.02})

    def p(self, table, rnd):
        return table[rnd]
PRIYA = Persona(key='A1', display='Priya', style='careful literalist', tone_p={1: 0.95, 2: 0.0}, priority_p={1: 0.0, 2: 0.97}, first_bonus={1: 1.0, 2: 0.3}, priority_bonus={1: 0.0, 2: 0.6}, refund_prior={1: 0.0, 2: 0.0}, empathy_feedback={1: 0.0, 2: 0.0}, clear_flip={1: 0.015, 2: 0.01}, random_intent_p={1: 0.0, 2: 0.0}, policy_p={1: 0.5, 2: 0.55}, sarcasm_neg_p={1: 0.12, 2: 0.88}, polite_neg_p={1: 0.0, 2: 0.0}, failure_neg_p={1: 0.0, 2: 0.92}, sent_noise={1: 0.02, 2: 0.02})
MARCUS = Persona(key='A2', display='Marcus', style='empathetic reader', tone_p={1: 0.95, 2: 0.0}, priority_p={1: 0.0, 2: 0.96}, first_bonus={1: 0.0, 2: 0.2}, priority_bonus={1: 0.0, 2: 0.6}, refund_prior={1: 1.5, 2: 0.0}, empathy_feedback={1: 0.9, 2: 0.0}, clear_flip={1: 0.02, 2: 0.015}, random_intent_p={1: 0.0, 2: 0.0}, policy_p={1: 0.4, 2: 0.45}, sarcasm_neg_p={1: 0.6, 2: 0.93}, polite_neg_p={1: 0.55, 2: 0.0}, failure_neg_p={1: 0.0, 2: 0.97}, pos_w=0.9, anger_w=2.0, nw_w=0.9, sent_noise={1: 0.02, 2: 0.02})
TOM = Persona(key='A3', display='Tom', style='high-throughput skimmer', tone_p={1: 0.9, 2: 0.0}, priority_p={1: 0.0, 2: 0.85}, first_bonus={1: 0.0, 2: 0.2}, priority_bonus={1: 0.0, 2: 0.4}, refund_prior={1: 0.0, 2: 0.0}, empathy_feedback={1: 0.0, 2: 0.0}, clear_flip={1: 0.07, 2: 0.035}, random_intent_p={1: 0.1, 2: 0.03}, policy_p={1: 0.2, 2: 0.35}, sarcasm_neg_p={1: 0.15, 2: 0.75}, polite_neg_p={1: 0.05, 2: 0.0}, failure_neg_p={1: 0.0, 2: 0.82}, pos_w=1.2, anger_w=1.0, nw_w=0.35, sent_noise={1: 0.1, 2: 0.05})
PERSONAS = [PRIYA, MARCUS, TOM]

def label_intent(persona: Persona, text: str, rnd: int, rng: random.Random):
    f = featurize(text)
    p = persona
    hits = f['intent_hits']
    t = text.lower()
    if rnd == 1 and f['frame_hits'] > 0 and (f['anger_hits'] >= 1) and hits and (rng.random() < p.p(p.tone_p, rnd)):
        return 'feedback_complaints'
    if any((c in t for c in POLICY_CUES)) and f['is_question'] and (rng.random() < p.p(p.policy_p, rnd)):
        return 'other_contact'
    if not hits:
        return rng.choice(CLASSES) if rng.random() < p.p(p.clear_flip, rnd) else 'other_contact'
    if rnd == 2 and len(hits) > 1 and (rng.random() < p.p(p.priority_p, rnd)):
        return min(hits, key=V2_INTENT_PRIORITY.index)
    scores = dict(hits)
    if f['first_group'] in scores:
        scores[f['first_group']] += p.p(p.first_bonus, rnd)
    if rnd == 2 and len(hits) > 1:
        top = min(hits, key=V2_INTENT_PRIORITY.index)
        scores[top] += p.p(p.priority_bonus, rnd)
    if p.p(p.refund_prior, rnd) and 'refund_request' in hits and (len(hits) > 1):
        scores['refund_request'] += p.p(p.refund_prior, rnd)
    if p.p(p.empathy_feedback, rnd) and (f['frame_hits'] or f['anger_hits'] >= 2):
        scores['feedback_complaints'] = scores.get('feedback_complaints', 0) + p.p(p.empathy_feedback, rnd)
    if rng.random() < p.p(p.random_intent_p, rnd):
        return rng.choice(list(hits.keys()))
    best = max(scores.values())
    tied = [g for g, s in scores.items() if s == best]
    lab = tied[rng.randrange(len(tied))]
    if rng.random() < p.p(p.clear_flip, rnd):
        neighbors = [c for c in CLASSES if c != lab]
        lab = rng.choice(neighbors)
    return lab

def label_sentiment(persona: Persona, text: str, rnd: int, rng: random.Random):
    f = featurize(text)
    p = persona
    if f['sarcasm_cue'] and rng.random() < p.p(p.sarcasm_neg_p, rnd):
        return 'negative'
    if rnd == 2 and f['negweak_hits'] >= 1 and p.p(p.failure_neg_p, rnd) and (rng.random() < p.p(p.failure_neg_p, rnd)):
        return 'negative'
    if rnd == 1 and f['negweak_hits'] >= 1 and (f['pos_hits'] == 0) and (f['anger_hits'] == 0) and (rng.random() < p.p(p.polite_neg_p, rnd)):
        return 'negative'
    score = p.pos_w * f['pos_hits'] - p.anger_w * f['anger_hits'] - p.nw_w * f['negweak_hits']
    if f['anger_hits'] >= 2 or score <= -1.5:
        lab = 'negative'
    elif f['anger_hits'] >= 1 and score <= 0:
        lab = 'negative'
    elif score >= 0.9:
        lab = 'positive'
    else:
        lab = 'neutral'
    if rng.random() < p.p(p.sent_noise, rnd):
        lab = SENTIMENTS[rng.randrange(3)]
    return lab

def label_ticket(persona: Persona, text: str, rnd: int, rng: random.Random):
    return (label_intent(persona, text, rnd, rng), label_sentiment(persona, text, rnd, rng))
