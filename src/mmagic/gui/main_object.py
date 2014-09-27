# -*- coding: utf-8 -*-

import operator

from PyQt4 import QtGui
from PyQt4.QtGui import QPushButton

import aqt.utils
import anki.notes
import anki.utils
import mmagic.core.exception as exception
import mmagic.zhonglib as zhonglib

# All this stuff should be moved to core
MANDARIN_FIELDS=frozenset({'Front', u'漢字', 'Hanzi', 'Chinese', 'Mandarin', 'Radical'})
ENGLISH_FIELDS=frozenset({'Back', 'English', 'Meaning'})
PINYIN_FIELDS=frozenset({u'拼音', u'pīnyīn', u'Pīnyīn', 'Pinyin', 'Pronunciation'})
DECOMPOSITION_FIELDS=frozenset({'Decomposition'})
MEASURE_WORD_FIELDS=frozenset({'Measure Word', 'Classifier', u'量詞'})

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
    print 'calculate_field_name (%s): keys: %s candidates: %s'%(possible_fields,note.keys(),candidates)
    if len(candidates) > 1:
        note_type = note.model()['name']
        message ='Note type "' + note_type + '" has the following fields: '
        message += '"%s"'%candidates.pop()
        while len(candidates) > 0:
            message += ', "%s"'%candidates.pop()
        message += '. It should have at most one of them.'
        raise exception.MagicException(message)
    if len(candidates) == 0:
        note_type = note.model()['name']
        message = 'Note type "' + note_type + '" does not have any of the following fields: '
        field_set = set(possible_fields)
        message += '"%s"'%field_set.pop()
        while len(field_set) > 0:
            message += ', "%s"'%field_set.pop()
        message += '. It should have one of them.'
        raise exception.MagicException(message)
    return candidates.pop()

#------------------------------------------------------------------------------
# Field access

def get_field(note, fields, fail_if_empty=False, strip_html=True):
    result = note[calculate_field_name(note, fields)]
    if fail_if_empty and len(result) == 0:
        field_name = calculate_field_name(note, fields)
        raise exception.MagicException(field_name + ' field is empty')
    if strip_html:
        result = anki.utils.stripHTML(result)
    return result

def has_field(note, fields):
    return len(set(note.keys()) & fields) > 0

def has_empty_field(note, fields):
    return has_field(note, fields)\
            and len(get_field(note, fields, strip_html=True)) == 0

def set_field(note, fields, value):
    note[calculate_field_name(note, fields)] = value

def get_mandarin_word(note, fail_if_empty=False):
    return get_field(note, MANDARIN_FIELDS, fail_if_empty)

def set_mandarin_field(note, value):
    set_field(note, MANDARIN_FIELDS, value)

def get_english_definition(note, fail_if_empty=False):
    return get_field(note, ENGLISH_FIELDS, fail_if_empty)

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

def has_measure_word_field(note):
    return has_field(note, MEASURE_WORD_FIELDS)

def has_empty_measure_word_field(note):
    return has_empty_field(note, MEASURE_WORD_FIELDS)

def get_measure_word_field(note):
    return get_field(note, MEASURE_WORD_FIELDS, note)

def set_measure_word_field(note, value):
    set_field(note, MEASURE_WORD_FIELDS, value)

def has_decomposition_field(note):
    return has_field(note, DECOMPOSITION_FIELDS)

def has_empty_decomposition_field(note):
    return has_empty_field(note, DECOMPOSITION_FIELDS)

def set_decomposition_field(note, value):
    set_field(note, DECOMPOSITION_FIELDS, value)

def get_decomposition_field(note, fail_if_empty=False):
    return get_field(note, DECOMPOSITION_FIELDS, fail_if_empty)

#------------------------------------------------------------------------------
# Note search

def find_notes(collection, field_set, value):
    result = []
    for field in field_set:
        notes = collection.findNotes(field + ":" + value)
        result += notes
    return result

def note_exists_for_mandarin(collection, word):
    notes = find_notes(collection, MANDARIN_FIELDS, word)
    return len(notes) > 0

#------------------------------------------------------------------------------
# Formatting routines

def format_list(the_list):
    if len(the_list) == 0:
        return ''
    result = ''
    assert len(the_list) > 0
    result += the_list[0]
    for idx in xrange(1, len(the_list)):
        result += ', ' + the_list[idx]
    return result

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

def format_entry_measure_words(is_first, ordinal, dictionary_entry):
    measure_words = dictionary_entry.traditional_measure_words
    print 'format_entry_measure_words: measure_words="'+str(measure_words)+'"'
    print 'is_first:', is_first
    if len(measure_words) == 0:
        return ''
    result = ''
    if not is_first:
        result += '<br>'
    result += '[' + str(ordinal) + '] ' + format_list(measure_words)
    return result

def format_measure_words(dictionary_entries):
    print 'format_measure_words for "%s"'%dictionary_entries[0].traditional
    if len(dictionary_entries) == 1:
        result = format_list(dictionary_entries[0].traditional_measure_words)
    else:
        # Each goes on a separate line with an integer identifier that matches
        # that in English field.
        result = ''
        is_first = True
        for idx in xrange(0, len(dictionary_entries)):
            formatted_measure_words = format_entry_measure_words(\
                is_first,\
                idx+1,\
                dictionary_entries[idx]
            )
            result += formatted_measure_words
            is_first = len(formatted_measure_words) == 0
    return result

def add_highlight(text, colour):
    return '<font color='+colour+'>'+text +'</font>'

def add_missing_note_highlight(text):
    return add_highlight(text, 'red')

def add_unlearnt_note_highlight(text):
    return add_highlight(text, 'orange')

def add_learnt_note_highlight(text):
    return add_highlight(text, 'green')

def note_is_learnt(note):
    card_types = [card.type for card in note.cards()]
    # A card type of '2' means that the cards is in review state.
    # Other possible values are 0 (new) and 1 (learning).
    # See anki.note and ank.sched for details.
    return reduce(operator.and_, map((lambda t: t == 2), card_types), True)

def format_decomposition(decomposition):
    if len(decomposition) == 0:
        return 'None'
    return format_list(decomposition)

# Returns the decomposition components as a list
def get_decomposition_list(note):
    field = get_decomposition_field(note)
    return [anki.utils.stripHTML(x.strip().rstrip()) for x in field.split(',')]

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
        aqt.utils.showInfo(all_messages[0])
        return
    # Multiple errors
    display_message = "The following problems were encountered:<br>"
    # Prepend an ordinal to each message.
    for idx in xrange(len(all_messages)):
        display_message += "<br>" + str(idx+1) + ". " + all_messages[idx]
    aqt.utils.showInfo(display_message)

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
            aqt.utils.showInfo("No notes selected.")
            return
        errors = exception.MultiException()
        for note_id in selected_notes:
            note = self.mw.col.getNote(note_id)
            try:
                self.populate_note(note)
            except exception.MagicException as e:
                errors.append(e)
            finally:
                note.flush()
        show_error(errors)
        self.mw.reset(guiOnly=True)
        aqt.utils.showInfo('Done.')

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
        finally:
            self.editor.note.flush()
            self.mw.reset(guiOnly = True)

    def add_note_mode_highlight(self, word):
        # Find all notes that have the given word as the Mandarin field
        note_ids = find_notes(self.mw.col, MANDARIN_FIELDS, word)
        if len(note_ids) > 1:
            raise exception.MagicException('More than one note for "'+word+'"')
        if len(note_ids) == 0:
            word = add_missing_note_highlight(word)
        elif note_is_learnt(self.mw.col.getNote(note_ids[0])):
            word = add_learnt_note_highlight(word)
        else:
            word = add_unlearnt_note_highlight(word)
        return word

    def highlight_character_mode(self, text):
        pattern, words = zhonglib.extract_cjk(text)
        highlit_words = tuple(map(lambda w: self.add_note_mode_highlight(w), words))
        return pattern%highlit_words

    def refresh_mode_hightlights(self, note):
        if has_decomposition_field(note):
            field = get_decomposition_field(note)
            set_decomposition_field(note, self.highlight_character_mode(field))
        if has_measure_word_field(note):
            field = get_measure_word_field(note)
            set_measure_word_field(note, self.highlight_character_mode(field))

    def populate_note(self, note):
        # Extract 漢字 from card
        mandarin_word = get_mandarin_word(note, fail_if_empty=True)

        # In the following, we want to populate as many fields as possible
        # even if errors occur on previous field.  The following object
        # is used to accumulate errors.  At the end, the object is raised
        # as an exception if it actually has errors.
        errors = exception.MultiException()

        # Get dictionary entries
        dictionary_entries = self.dictionary.find(mandarin_word)
        if len(dictionary_entries) == 0:
            message = 'No dictionary entry for "' + mandarin_word + '"'
            errors.append(exception.MagicException(message))

        if len(dictionary_entries) > 0:
            # Add Englih
            if has_empty_english_field(note):
                set_english_field(note, format_english(dictionary_entries))

            # Add 拼音
            if has_empty_pinyin_field(note):
                set_pinyin_field(note, format_pinyin(dictionary_entries))

            # Add 量詞
            if has_empty_measure_word_field(note):
                set_measure_word_field(note, format_measure_words(dictionary_entries))

        if has_empty_decomposition_field(note):
            try:
                decomposition = zhonglib.decompose(mandarin_word)
                set_decomposition_field(\
                    note,\
                    format_decomposition(decomposition\
                ))
            except exception.MagicException as e:
                errors.append(e)
            except zhonglib.ZhonglibException as e:
                errors.append(exception.MagicException(str(e)))

        self.refresh_mode_hightlights(note)
        errors.raise_if_not_empty()
    
    def add_mandarin_note(self, text):
        assert self.editor.note != None
        errors = exception.MultiException()
        model = self.editor.note.model()
        note = anki.notes.Note(self.mw.col, model)
        set_mandarin_field(note, text)
        try:
            self.populate_note(note)
        except exception.MagicException as e:
            errors.append(e)
        # The following will flush the note
        cards_added = self.mw.col.addNote(note)
        if cards_added == 0:
            errors.append(exception.MagicException(
                'No cards were added for "' + text + '". ' +
                "Try adding manually for further clues."
            ))
        errors.raise_if_not_empty()

    def from_editor_add_missing_cards(self):
        assert self.editor.note != None
        note = self.editor.note
        if not has_decomposition_field(note):
            raise exception.MagicException("Note does not have a decomposition field.")

        # Add a note for every composition component that doesn't yet
        # have one.
        mandarin_word = get_mandarin_word(note, fail_if_empty=True)
        decomposition = get_decomposition_list(note)
        errors = exception.MultiException()
        for component in decomposition:
            if not note_exists_for_mandarin(self.mw.col, component):
                try:
                    self.add_mandarin_note(component)
                except exception.MagicException as e:
                    errors.append(e)

        # Missing components (may) have been added.  Refresh decomposition
        # field to reflect this.
        self.refresh_mode_hightlights(note)
        note.flush()
        self.mw.reset(guiOnly = True)

        show_error(errors)
