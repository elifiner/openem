# coding=utf8
from prettydate import prettydate

class dictobj(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

def encrypt_password(password, salt):
    """
    Creates a password hash.
    """
    import sha
    s = sha.new()
    s.update(bytes(password))
    s.update(bytes(salt))
    return s.hexdigest()

def bytes(s):
    """
    Makes sure a string is in bytes.
    """
    if isinstance(s, unicode):
        return s.encode("utf8")
    return s

def unescape(s):
    import HTMLParser
    h = HTMLParser.HTMLParser()
    return h.unescape(s)
