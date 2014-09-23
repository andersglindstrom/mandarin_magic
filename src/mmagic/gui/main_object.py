# -*- coding: utf-8 -*-

from PyQt4 import QtGui
from PyQt4.QtGui import QPushButton
from aqt import mw, utils
from mmagic.core.exception import MagicException
import mmagic.zhonglib as zhonglib

# All this stuff should be moved to core
ENGLISH_FIELDS=frozenset({'English'})
MANDARIN_FIELDS=frozenset({u'漢字', 'Hanzi', 'Chinese', 'Mandarin'})
PINYIN_FIELDS=frozenset({u'拼音', u'pīnyīn', u'Pīnyīn', 'Pinyin', 'Pronunciation'})
DECOMPOSITION_FIELDS=frozenset({'Decomposition'})

def calculate_field_name(note, possible_fields):
    # Have to make this is a mutable set. Hence the explicit construction.
    candidates = set(possible_fields & set(note.keys()))
    if len(candidates) > 1:
        note_type = note.model()['name']
        message ='Note type "' + note_type + '" has the following fields: '
        message += candidates.pop()
        while len(candidates) > 0:
            message += ", " + candidates.pop()
        message += '. It should have at most one of them.'
        raise MagicException(message)
    if len(candidates) == 0:
        note_type = note.model()['name']
        message = 'Note type "' + note_type + '" does not have any of the following fields: '
        field_set = set(possible_fields)
        message += field_set.pop()
        while len(field_set) > 0:
            message += ', ' + field_set.pop()
        message += '. It should have one of them.'
        raise MagicException(message)
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

def has_decomposition_field(note):
    return len(set(note.keys()) & DECOMPOSITION_FIELDS) > 0

def set_decomposition_field(note, value):
    note[calculate_field_name(note, DECOMPOSITION_FIELDS)] = value

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

def format_decomposition(decompositon):
    result = ''
    if len(decompositon) == 0:
        return result
    result += decompositon[0]
    for idx in xrange(1, len(decompositon)):
        result += ', ' + decompositon[idx]
    return result

class MainObject:

    def __init__(self, anki_main_window):
        self.mw = anki_main_window
        self.define_action = QtGui.QAction("Define", self.mw)
        self.define_action.triggered.connect(self.do_define_from_browser)
        self.dictionary = zhonglib.standard_dictionary()

    def setup_browser_menu(self, browser):
        self.browser = browser
        self.browser.form.menuEdit.addAction(self.define_action)

    def do_define_from_browser(self):
        selected_notes = self.browser.selectedNotes()
        if not selected_notes:
            utils.showInfo("No notes selected.")
            return
        errors = []
        for note_id in selected_notes:
            note = mw.col.getNote(note_id)
            try:
                self.populate_note(note)
            except MagicException as e:
                errors.append(e)
        if len(errors) > 0:
            message = "The following errors occurred:"
            count = 0

            # Want to avoid duplication of messages.
            seen_messages = set()
            for e in errors:
                if e.message() in seen_messages:
                    continue
                count += 1
                message += "<br><br>" + str(count) + ". " + e.message()
                seen_messages = e.message()

            utils.showInfo(message)

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
            assert self.editor.note != None
            self.populate_note(self.editor.note)
        except MagicException as e:
            utils.showInfo(e.message())

    def populate_note(self, note):
        try:
            # Extract 漢字 from card
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

            # Can decompose single characaters only just now
            if has_decomposition_field(note):
                decompositon = zhonglib.decompose(mandarin_word)
                set_decomposition_field(note, format_decomposition(decompositon))

        finally:
            note.flush()
            mw.reset()
