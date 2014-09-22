# -*- coding: utf-8 -*-

from PyQt4 import QtGui
from PyQt4.QtGui import QPushButton
from aqt import mw, utils
from mmagic.core.exception import MagicException
import mmagic.zhonglib

# All this stuff should be moved to core
ENGLISH_FIELDS={'English'}
MANDARIN_FIELDS={u'漢字', 'Hanzi', 'Chinese', 'Mandarin'}
PINYIN_FIELDS={u'拼音', 'pīnyīn', 'Pīnyīn', 'Pinyin', 'Pronunciation'}

def calculate_field_name(note, possible_fields):
    candidates = possible_fields & set(note.keys())
    if len(candidates) > 1:
        raise MagicException("More than one potential Mandarin field")
    if len(candidates) == 0:
        raise MagicException("No Mandarin field.")
    return candidates.pop()

def get_mandarin_word(note):
    return note[calculate_field_name(note, MANDARIN_FIELDS)]

def get_english_definition(note):
    return note[calculate_field_name(note, PINYIN_FIELDS)]

def has_english_field(note):
    return len(set(note.keys()) & ENGLISH_FIELDS) > 0

def set_english_field(note, value):
    note[calculate_field_name(note, ENGLISH_FIELDS)] = value

def has_pinyin_field(note):
    return len(set(note.keys()) & PINYIN_FIELDS) > 0

def set_pinyin_field(note, value):
    note[calculate_field_name(note, PINYIN_FIELDS)] = value

def format_entry_meaning(entry):
    result = entry.meaning[0]
    for idx in xrange(1, len(entry.meaning)):
        result += "; "
        result += entry.meaning[idx]
    return result

def format_english(dictionary_entries):
    if len(dictionary_entries) == 1:
        result = format_entry_meaning(dictionary_entries[0])
    else:
        # Each entry is put on a separate line with an integer identifier.
        result = '[1] ' + format_entry_meaning(dictionary_entries[0])
        for idx in xrange(1, len(dictionary_entries)):
            id = idx+1
            result += '<br>['+str(id)+'] ' + format_entry_meaning(dictionary_entries[idx])
    return result

def format_pinyin(dictionary_entries):
    if len(dictionary_entries) == 1:
        result = dictionary_entries[0].pinyin
    else:
        # Each goes on a separate line with an integer identifier that matches
        # that in English field.
        result = '[1] ' + dictionary_entries[0].pinyin
        for idx in xrange(1, len(dictionary_entries)):
            id = idx+1
            result += '<br>['+str(id)+'] ' + dictionary_entries[idx].pinyin
    return result

class MainObject:

    def __init__(self, anki_main_window):
        self.mw = anki_main_window
        self.define_action = QtGui.QAction("Define", self.mw)
        self.define_action.triggered.connect(self.do_define_from_browser)
        self.dictionary = mmagic.zhonglib.standard_dictionary()

    def setup_browser_menu(self, browser):
        self.browser = browser
        self.browser.form.menuEdit.addAction(self.define_action)

    def do_define_from_browser(self):
        selected_notes = self.browser.selectedNotes()
        if not selected_notes:
            utils.showInfo("No notes selected.")
            return
        try:
            for note_id in selected_notes:
                note = mw.col.getNote(note_id)
                self.populate_note(note)
        except MagicException as e:
            utils.showInfo(e.message())

    def setup_editor_button(self, editor):
        self.editor = editor
        button = QPushButton(editor.widget)
        button.setFixedHeight(20)
        button.setFixedWidth(20)
        button.setText('Z')
        button.clicked.connect(self.define_from_editor)
        button.setStyle(editor.plastiqueStyle)
        editor.iconsBox.addWidget(button)

    def define_from_editor(self):
        try:
            self.populate_note(self.editor.note)
        except MagicException as e:
            utils.showInfo(e.message())

    def populate_note(self, note):

        # Extract Mandarin from card
        mandarin_word = get_mandarin_word(note)
        if len(mandarin_word) == 0:
            raise MagicException(MANDARIN_FIELD + ' field is empty')

        # Get dictionary entries
        dictionary_entries = self.dictionary.find(mandarin_word)
        if len(dictionary_entries) == 0:
            raise MagicException('No dictionary entry for "' + mandarin_word + '"')

        # Add Englih
        if has_english_field(note):
            set_english_field(note, format_english(dictionary_entries))

        # Add 拼音
        if has_pinyin_field(note):
            set_pinyin_field(note, format_pinyin(dictionary_entries))

        note.flush()
        mw.reset()
