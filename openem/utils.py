# coding=utf8
from prettydate import prettydate
from django.utils.safestring import mark_safe
from django.utils.html import escape

class dictobj(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

def bytes(s):
    """
    Makes sure a string is in bytes.
    """
    if isinstance(s, unicode):
        return s.encode("utf8")
    return s

def text2p(text):
    text = escape(text)
    return mark_safe("\n".join(("<p>%s</p>" % l) for l in text.splitlines() if l))
