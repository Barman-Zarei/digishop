import arabic_reshaper
from bidi.algorithm import get_display


def shape_persian(text):
    # Shaping is now done globally by utils/persian_patch.py.
    # Kept as a pass-through so the existing calls in the screens stay
    # harmless. Shaping twice would reverse the text back.
    return text
