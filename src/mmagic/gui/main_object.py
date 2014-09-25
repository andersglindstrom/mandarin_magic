# -*- coding: utf-8 -*-

from PyQt4 import QtGui
from PyQt4.QtGui import QPushButton
from aqt import mw, utils
from anki.notes import Note
import mmagic.core.exception as exception
import mmagic.zhonglib as zhonglib

# All this stuff should be moved to core
MANDARIN_FIELDS=frozenset({'Front', u'漢字', 'Hanzi', 'Chinese', 'Mandarin'})
ENGLISH_FIELDS=frozenset({'Back', 'English'})
PINYIN_FIELDS=frozenset({u'拼音', u'pīnyīn', u'Pīnyīn', 'Pinyin', 'Pronunciation'})
DECOMPOSITION_FIELDS=frozenset({'Decomposition'})

#------------------------------------------------------------------------------
#

# From a set of possible field names, this function returns the actual field
# used in a particular note.
#
# MagicException is thrown if there is no matching field or there is more than
# one match.
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
        raise exception.MagicException(message)
    if len(candidates) == 0:
        note_type = note.model()['name']
        message = 'Note type "' + note_type + '" does not have any of the following fields: '
        field_set = set(possible_fields)
        message += field_set.pop()
        while len(field_set) > 0:
            message += ', ' + field_set.pop()
        message += '. It should have one of them.'
        raise exception.MagicException(message)
    return candidates.pop()

#------------------------------------------------------------------------------
# Field access

def get_field(note, fields, failIfEmpty=False):
    result = note[calculate_field_name(note, fields)]
    if failIfEmpty and len(result) == 0:
        field_name = calculate_field_name(note, fields)
        raise exception.MagicException(field_name + ' field is empty')
    return result

def has_field(note, fields):
    return len(set(note.keys()) & fields) > 0

def has_empty_field(note, fields):
    return has_field(note, fields) and len(get_field(note, fields)) == 0

def set_field(note, fields, value):
    note[calculate_field_name(note, fields)] = value

def get_mandarin_word(note, failIfEmpty=False):
    return get_field(note, MANDARIN_FIELDS, failIfEmpty)

def set_mandarin_field(note, value):
    set_field(note, MANDARIN_FIELDS, value)

def get_english_definition(note, failIfEmpty=False):
    return get_field(note, ENGLISH_FIELDS, failIfEmpty)

def has_english_field(note):
    return has_field(note, ENGLISH_FIELDS)

def has_empty_english_field(note):
    return has_empty_field(note, ENGLISH_FIELDS)

def set_english_field(note, value):
    set_field(note, ENGLISH_FIELDS, value)

def has_pinyin_field(note):
    return has_field(note, PINYIN_FIELDS)

def has_empty_pinyin_field(note):
    return has_empty_field(note, PINYIN_FIELDS)

def set_pinyin_field(note, value):
    set_field(note, PINYIN_FIELDS, value)

def has_decomposition_field(note):
    return has_field(note, DECOMPOSITION_FIELDS)

def has_empty_decomposition_field(note):
    return has_empty_field(note, DECOMPOSITION_FIELDS)

def set_decomposition_field(note, value):
    set_field(note, DECOMPOSITION_FIELDS, value)

def get_decomposition_field(note, failIfEmpty=False):
    return get_field(note, DECOMPOSITION_FIELDS, failIfEmpty)

#------------------------------------------------------------------------------
# Note search

def find_notes(collection, field_set, value):
    result = []
    for field in field_set:
        notes = collection.findNotes(field + ":" + value)
        result += notes
    return result

def note_exists_for_mandarin(collection, word):
    print 'Looking for ' + word
    notes = find_notes(collection, MANDARIN_FIELDS, word)
    print notes
    return len(notes) > 0

#------------------------------------------------------------------------------
# Formatting routines

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

def add_highlight(text):
    return '<font color=red>' + text + '</font>'

def remove_highlight(text):
    return text.replace('<font color=red>', '').replace('</font>', '')

def format_decomposition(collection, decompositon):
    if len(decompositon) == 0:
        return 'None'
    result = ''
    for idx in xrange(0, len(decompositon)):
        component = decompositon[idx]
        if not note_exists_for_mandarin(collection, component):
            component = add_highlight(component)
        if idx == 0:
            result += component
        else:
            result += ', ' + component
    return result

def unformat_decomposition(decompositon):
    return [remove_highlight(x.strip().rstrip()) for x in decompositon.split(',')]

# exception must be an instance of MagicException or its subclasses
def show_error(exception):
    # Use a set to avoid duplicates. Use a list to support indexing.
    all_messages = list(set(exception.get_message_list()))
    print 'all_messages:', all_messages
    # No Messages
    if len(all_messages) == 0:
        return
    # Single error only
    if len(all_messages) == 1:
        utils.showInfo(all_messages[0])
        return
    # Multiple errors
    display_message = "The following problems were encountered:<br>"
    # Prepend an ordinal to each message.
    for idx in xrange(len(all_messages)):
        display_message += "<br>" + str(idx+1) + ". " + all_messages[idx]
    utils.showInfo(display_message)

class MainObject:

    def __init__(self, anki_main_window):
        self.mw = anki_main_window

        self.do_define_action = QtGui.QAction("Define", self.mw)
        self.do_define_action.triggered.connect(self.do_define_from_browser)

        self.dictionary = zhonglib.standard_dictionary()

    def setup_browser_menu(self, browser):
        self.browser = browser
        self.browser.form.menuEdit.addAction(self.do_define_action)

    def do_define_from_browser(self):
        selected_notes = self.browser.selectedNotes()
        if not selected_notes:
            utils.showInfo("No notes selected.")
            return
        errors = exception.MultiException()
        for note_id in selected_notes:
            note = self.mw.col.getNote(note_id)
            try:
                self.populate_note(note)
            except exception.MagicException as e:
                errors.append(e)
        show_error(errors)

    def setup_button(self, editor, text, method_to_call):
        self.editor = editor
        button = QPushButton(editor.widget)
        button.setFixedHeight(20)
        button.setFixedWidth(20)
        button.setText(text)
        button.clicked.connect(method_to_call)
        button.setStyle(editor.plastiqueStyle)
        editor.iconsBox.addWidget(button)

    def setup_editor_buttons(self, editor):
        self.setup_button(editor, 'Z', self.from_editor_populate_note)
        self.setup_button(editor, '+', self.from_editor_add_missing_cards)

    def from_editor_populate_note(self):
        try:
            assert self.editor.note != None
            self.populate_note(self.editor.note)
        except exception.MagicException as e:
            show_error(e)

    def populate_note(self, note):
        try:
            # Extract 漢字 from card
            mandarin_word = get_mandarin_word(note, failIfEmpty=True)

            # Get dictionary entries
            dictionary_entries = self.dictionary.find(mandarin_word)
            if len(dictionary_entries) == 0:
                raise exception.MagicException('No dictionary entry for "' + mandarin_word + '"')

            # Add Englih
            if has_empty_english_field(note):
                set_english_field(note, format_english(dictionary_entries))

            # Add 拼音
            if has_empty_pinyin_field(note):
                set_pinyin_field(note, format_pinyin(dictionary_entries))

            # Can decompose single characaters only just now
            if has_empty_decomposition_field(note):
                decompositon = zhonglib.decompose(mandarin_word)
                set_decomposition_field(\
                    note,\
                    format_decomposition(self.mw.col, decompositon\
                ))

        finally:
            note.flush()
            mw.reset(guiOnly = True)
    
    def add_mandarin_note(self, text):
        assert self.editor.note != None
        model = self.editor.note.model()
        note = Note(self.mw.col, model)
        set_mandarin_field(note, text)
        mw.col.addNote(note)
        self.populate_note(note)

    def from_editor_add_missing_cards(self):
        assert self.editor.note != None
        note = self.editor.note
        if not has_decomposition_field(note):
            raise exception.MagicException("Note does not have a decomposition field.")

        # Add a note for every composition component that doesn't yet
        # have one.
        mandarin_word = get_mandarin_word(note, failIfEmpty=True)
        decompositon = zhonglib.decompose(mandarin_word)
        errors = exception.MultiException()
        for component in decompositon:
            if not note_exists_for_mandarin(self.mw.col, component):
                try:
                    self.add_mandarin_note(component)
                except exception.MagicException as e:
                    errors.append(e)

        # Have to reformat decompositon field.
        set_decomposition_field(\
            note,\
            format_decomposition(self.mw.col, decompositon\
        ))
        note.flush()
        mw.reset(guiOnly = True)

        show_error(errors)
