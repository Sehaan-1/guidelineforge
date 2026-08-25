import re
from functools import lru_cache
ANGER = ['terrible', 'awful', 'horrible', 'ridiculous', 'unacceptable', 'furious', 'angry', 'upset', 'disgrace', 'scam', 'joke', 'worst', 'useless', 'pathetic', 'annoyed', 'annoying', 'frustrat', 'nightmare', 'fed up', 'sick of', 'sick and tired', 'insane', 'disgusted', 'outrageous', 'appalling', 'never shopping', 'never buying', 'never again']
POS = ['thank', 'great', 'good', 'love', 'lovely', 'awesome', 'amazing', 'excellent', 'perfect', 'happy', 'glad', 'nice', 'wonderful', 'brilliant', 'appreciate', 'fantastic', 'pleased', 'favorite']
NEGWEAK = ['problem', 'issue', 'trouble', 'broken', 'not working', "doesn't work", 'does not work', 'wrong', 'missing', 'late', 'delayed', 'delay', 'damaged', 'error', 'failed', 'charged twice', 'double-charged', 'double charged', 'went through twice', 'crash', "haven't received", 'have not received', 'never arrived', 'never got', 'stuck', "can't", 'cannot', 'unable', 'no sign', 'vanished', 'still waiting', 'no movement', 'second time', 'third time', 'still no', "where's my money", 'money back now', 'concern', 'worr', 'never authoriz', "aren't helpful", 'not helpful', 'goddamn', 'damn']
COMPLAINT_FRAME = ['joke', 'ridiculous', 'unacceptable', 'pathetic', 'disgrace', 'scam', 'worst', 'nightmare', 'furious', 'outrageous', 'useless', 'sick of', 'fed up', 'had it', 'never again', 'ashamed', 'never shopping', 'disgusted', 'worst experience', 'appalling']
SARCASM_PHRASES = ['oh great', 'yeah right', 'just love', 'gotta love', 'way to go', 'how lovely', 'just perfect', 'wow,', 'woo', 'never disappoint', 'top-notch', 'top notch', 'exactly what i needed', 'what a wonderful']
INTENT_KEYWORDS = {'refund_request': ['\\brefund', '\\bmoney back\\b', '\\bmy money\\b', '\\bmy \\$?\\d', '\\breimburs', '\\brebat', '\\bcompensation', '\\brestitution', '\\bchargeback', '\\bpay me back\\b'], 'cancellation': ['\\bcancel', '\\bcancellation', '\\btermination fee\\b'], 'billing_payments': ['\\bcharg', '\\binvoice', '\\bpayment', '\\bbill', '\\bcard\\b', '\\bfee\\b', '\\bfees\\b', '\\bprice\\b', '\\bpaid\\b', '\\bstatement\\b'], 'shipping_delivery': ['\\bdeliver', '\\bship', '\\bpackage', '\\bparcel', '\\btrack', '\\barriv', '\\bcourier', '\\bshipping address', '\\bin transit\\b'], 'account_access': ['\\baccount', '\\bpassword', '\\blog ?in', '\\bsign ?in', '\\bregister', '\\busername', '\\bprofile', '\\bemail address\\b', '\\bpin\\b', '\\bverif'], 'order_changes': ['\\bchange (my |the )?order', '\\bedit (my |the )?order', '\\bmodify (my |the )?order', '\\bplace (an |my |the )?order', '\\badd(ing)? (an |the |some |something |several |a few )?(product|item|article)s?\\b', '\\bremove (an |the |some )?(product|item|article)s?\\b', '\\bchang(e|ing) (several |some |a few )?(article|item|product)s?\\b', '\\badd (something|some|a few)', '\\bquantit', '\\bbuy\\b', '\\bbuy(ing)? (some|a few|your|this)'], 'feedback_complaints': ['\\bcomplain', '\\bcomplaint', '\\breview', '\\bfeedback', '\\bdisappoint', '\\brating', '\\bbad experience', '\\bopinion', '\\bconsumer claim', '\\bcomment about'], 'other_contact': ['\\bagent', '\\bhuman', '\\brepresentative', '\\breal person', '\\bcustomer service\\b', '\\bnewsletter', '\\bsubscri', '\\bsomeone\\b', '\\bsomebody', '\\bperson\\b', '\\btalk to\\b', '\\bspeak (to|with)\\b']}
_WORD = re.compile("[a-z']+")

def _mk_regex(phrases):
    parts = sorted((re.escape(p) for p in phrases), key=len, reverse=True)
    return re.compile('\\b(?:' + '|'.join(parts) + ')')
_RX = {name: _mk_regex(lst) for name, lst in [('anger', ANGER), ('pos', POS), ('negweak', NEGWEAK), ('frame', COMPLAINT_FRAME), ('sarc_ph', SARCASM_PHRASES)]}

def _count(rx, text):
    return len(rx.findall(text))

@lru_cache(maxsize=8192)
def featurize(text: str) -> dict:
    t = ' ' + text.lower().strip() + ' '
    anger = _count(_RX['anger'], t)
    pos = _count(_RX['pos'], t)
    negweak = _count(_RX['negweak'], t)
    frame = _count(_RX['frame'], t)
    sarc_ph = _count(_RX['sarc_ph'], t)
    contrast = pos > 0 and (negweak > 0 or anger > 0 or 'again' in t)
    sarcasm_cue = bool(sarc_ph) or contrast
    hits, first_pos = ({}, {})
    for group, patterns in INTENT_KEYWORDS.items():
        n, earliest = (0, None)
        for pat in patterns:
            for m in re.finditer(pat, t):
                n += 1
                if earliest is None or m.start() < earliest:
                    earliest = m.start()
        if n:
            hits[group] = n
            first_pos[group] = earliest
    first_group = min(first_pos, key=first_pos.get) if first_pos else None
    return {'anger_hits': anger, 'pos_hits': pos, 'negweak_hits': negweak, 'frame_hits': frame, 'sarcasm_cue': sarcasm_cue, 'intent_hits': hits, 'n_groups': len(hits), 'first_group': first_group, 'is_question': '?' in text, 'n_words': len(_WORD.findall(text))}
V2_INTENT_PRIORITY = ['refund_request', 'cancellation', 'billing_payments', 'shipping_delivery', 'order_changes', 'account_access', 'feedback_complaints', 'other_contact']
