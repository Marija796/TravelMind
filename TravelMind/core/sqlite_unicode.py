"""
SQLite's built-in LIKE/UPPER/LOWER only case-fold ASCII by default (Unicode
case-folding needs the ICU extension, which the stock Python sqlite3 module
doesn't load). Django's icontains/istartswith/etc. lookups compile to LIKE
under the hood, so on this backend "париз" and "ПАРИЗ" silently fail to match
"Париз" even though the equivalent English search ("paris" vs "PARIS") works
fine - English text stays within SQLite's ASCII fast path.

Registering a Python-implemented `like` function (SQLite lets you override
its built-ins by name) fixes this for every icontains-based lookup at once -
search, filters, autocomplete - without touching any view/serializer code,
since Python's `re.IGNORECASE` is Unicode-aware.
"""
import re
from django.db.backends.signals import connection_created


def _like_pattern_to_regex(pattern, escape_char='\\'):
    parts = []
    i, n = 0, len(pattern)
    while i < n:
        c = pattern[i]
        if c == escape_char and i + 1 < n:
            parts.append(re.escape(pattern[i + 1]))
            i += 2
            continue
        if c == '%':
            parts.append('.*')
        elif c == '_':
            parts.append('.')
        else:
            parts.append(re.escape(c))
        i += 1
    return '^' + ''.join(parts) + '$'


def _unicode_like(pattern, value, escape_char='\\'):
    if pattern is None or value is None:
        return None
    regex = _like_pattern_to_regex(pattern, escape_char)
    return 1 if re.match(regex, value, re.IGNORECASE | re.DOTALL) else 0


def _register_unicode_like(sender, connection, **kwargs):
    if connection.vendor != 'sqlite':
        return
    raw = connection.connection
    # SQLite dispatches `X LIKE Y` to the 2-arg form and `X LIKE Y ESCAPE Z`
    # to the 3-arg form - Django's icontains always appends an ESCAPE clause,
    # but both are registered so any LIKE usage gets Unicode-correct folding.
    raw.create_function('like', 2, lambda pat, val: _unicode_like(pat, val), deterministic=True)
    raw.create_function('like', 3, lambda pat, val, esc: _unicode_like(pat, val, esc), deterministic=True)


connection_created.connect(_register_unicode_like)
