"""
Dependency-free cosine similarity helpers shared by:
  - users/views.py (SimilarUsersView): user-to-user preference similarity
  - recommendations/views.py: user-to-destination preference matching

No numpy/scikit-learn is used - vectors here are small (tens of dimensions)
and computed over at most a few hundred rows per request, so a pure-Python
implementation is simple, dependency-free, and fast enough.
"""
import math


def cosine_similarity(vec_a, vec_b):
    """
    Standard cosine similarity: dot(a, b) / (||a|| * ||b||).

    Returns 0.0 if either vector has zero magnitude (undefined similarity
    treated as "no match" rather than raising, since e.g. a user or
    destination with zero populated preference fields is a normal input,
    not a bug).
    """
    if len(vec_a) != len(vec_b):
        raise ValueError('Vectors must be the same length to compare.')
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a * a for a in vec_a))
    mag_b = math.sqrt(sum(b * b for b in vec_b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def overlap_coefficient(set_a, set_b):
    """
    Szymkiewicz-Simpson overlap coefficient: |A n B| / min(|A|, |B|).

    Used instead of cosine similarity for "preference wishlist vs. small
    feature set" comparisons (e.g. a user's selected activities against a
    destination's activity list). Unlike cosine similarity - which divides
    by sqrt(|A|*|B|) and therefore penalizes a large A even when B is
    entirely contained in it - dividing by the smaller set means a
    destination whose every activity is also wanted by the user scores a
    perfect 1.0 regardless of how many activities the user selected.

    Returns 0.0 if either set is empty (undefined overlap, not a bug).
    """
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    return intersection / min(len(set_a), len(set_b))
