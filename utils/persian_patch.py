import re

import arabic_reshaper
from bidi.algorithm import get_display
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

_ARABIC_RE = re.compile("[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]")


def _shape(text):
    if not text or not isinstance(text, str) or not _ARABIC_RE.search(text):
        return text
    try:
        return get_display(arabic_reshaper.reshape(text))
    except Exception:
        return text


# Label (covers Button and Popup titles too, they inherit from Label)
_orig_create_label = Label._create_label
_orig_trigger = Label._trigger_texture_update


def _create_label(self):
    _orig_create_label(self)
    if self._label is not None:
        self._label.text = _shape(self.text)


def _trigger_texture_update(self, name=None, source=None, value=None):
    if source and name == "text":
        value = _shape(value)
    _orig_trigger(self, name, source, value)


Label._create_label = _create_label
Label._trigger_texture_update = _trigger_texture_update

# TextInput: shaped live, with the cursor forced to the end after every
# edit while the field contains Persian/Arabic text. This is a tradeoff —
# you can no longer click mid-word to edit a Persian field, only
# append/backspace from the end. English fields are unaffected.
_orig_line_label = TextInput._create_line_label
_orig_insert_text = TextInput.insert_text
_orig_do_backspace = TextInput.do_backspace


def _create_line_label(self, text, hint=False):
    if not self.password:
        text = _shape(text)
    return _orig_line_label(self, text, hint)


def _move_cursor_to_end(self):
    self.cursor = self.get_cursor_from_index(len(self.text))


def _insert_text(self, substring, from_undo=False):
    result = _orig_insert_text(self, substring, from_undo=from_undo)
    if not self.password and _ARABIC_RE.search(self.text or ""):
        _move_cursor_to_end(self)
    return result


def _do_backspace(self, from_undo=False, mode="bkspc"):
    result = _orig_do_backspace(self, from_undo=from_undo, mode=mode)
    if not self.password and _ARABIC_RE.search(self.text or ""):
        _move_cursor_to_end(self)
    return result


TextInput._create_line_label = _create_line_label
TextInput.insert_text = _insert_text
TextInput.do_backspace = _do_backspace
