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

def get_mandarin_text(note, fail_if_empty=False):
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
    return get_field(note, MEASURE_WORD_FIELDS)

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

def format_entry_english(entry):
    result = entry.english[0]
    for idx in xrange(1, len(entry.english)):
        result += "; "
        result += entry.english[idx]
    return result

def format_english(dictionary_entries):
    if len(dictionary_entries) == 1:
        result = format_entry_english(dictionary_entries[0])
    else:
        # Each entry is put on a separate line with an integer identifier.
        result = '[1] ' + format_entry_english(dictionary_entries[0])
        for idx in xrange(1, len(dictionary_entries)):
            id = idx+1
            result += '<br>['+str(id)+'] ' + format_entry_english(dictionary_entries[idx])
    return result

def format_pinyin(text):
    return zhonglib.format_pinyin_sequence(zhonglib.parse_cedict_pinyin(text))

def format_pinyin_list(dictionary_entries):
    if len(dictionary_entries) == 1:
        result = format_pinyin(dictionary_entries[0].pinyin)
    else:
        # Each goes on a separate line with an integer identifier that matches
        # that in English field.
        result = '[1] ' + format_pinyin(dictionary_entries[0].pinyin)
        for idx in xrange(1, len(dictionary_entries)):
            id = idx+1
            result += '<br>['+str(id)+'] ' + format_pinyin(dictionary_entries[idx].pinyin)
    return result

def format_entry_measure_words(is_first, ordinal, dictionary_entry):
    measure_words = dictionary_entry.traditional_measure_words
    if len(measure_words) == 0:
        return ''
    result = ''
    if not is_first:
        result += '<br>'
    result += '[' + str(ordinal) + '] ' + format_list(measure_words)
    return result

def format_measure_words(dictionary_entries):
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
    field = anki.utils.stripHTML(field.strip().rstrip())
    if field == 'None':
        return []
    pattern, words = zhonglib.extract_cjk(field)
    return list(words)

def get_measure_word_list(note):
    field = get_measure_word_field(note)
    field = anki.utils.stripHTML(field.strip().rstrip())
    if len(field) == 0:
        return []
    pattern, words = zhonglib.extract_cjk(field)
    return list(words)

# exception must be an instance of MagicException or its subclasses
def show_error(exception):
    # Use a set to avoid duplicates. Use a list to support indexing.
    all_messages = list(set(exception.get_message_list()))
    # No Messages
    if len(all_messages) == 0:
        return
    # Single error only
    if len(all_messages) == 1:
        aqt.utils.showInfo(all_messages[0])
        return
    # Multiple errors
    display_message = u"The following problems were encountered:<br>"
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

        # Disable this for now. I think it's more trouble than it's worth.
        # It's safer to populate each note one-by-one.

        #self.browser.form.menuEdit.addAction(self.do_define_action)

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
                # Even if there's an error, flush the note.  Usually, the
                # error only pertains to one problematic field.  The other
                # fields are okay.
                note.flush()
        show_error(errors)
        self.mw.reset(guiOnly=True)
        aqt.utils.showInfo('Done.')

    def setup_button(self, editor, text, callback):
        button = QPushButton(editor.widget)
        button.setFixedHeight(20)
        button.setFixedWidth(20)
        button.setText(text)
        button.clicked.connect(callback)
        button.setStyle(editor.plastiqueStyle)
        editor.iconsBox.addWidget(button)

    def setup_editor_buttons(self, editor):
        self.editor = editor
        self.setup_button(editor, 'P', lambda: self.populate_and_save_note(editor.note))
        self.setup_button(editor, '+', lambda: self.add_missing_components(editor.note))

    def populate_and_save_note(self, note):
        try:
            self.populate_note(note)
            note.flush()
        except exception.MagicException as e:
            show_error(e)
        finally:
            self.mw.reset(guiOnly = True)

    def add_learning_status_colour_to_word(self, word):
        # Find all notes that have the given word as the Mandarin field
        note_ids = find_notes(self.mw.col, MANDARIN_FIELDS, word)
        if len(note_ids) == 0:
            word = add_missing_note_highlight(word)
        else:
            # Find out whether each note is learnt or not.
            notes_are_learnt = map(
                lambda note_id: note_is_learnt(self.mw.col.getNote(note_id)),
                note_ids
            )
            # Are they all learnt?
            all_learnt = reduce(operator.and_, notes_are_learnt, True)
            if all_learnt:
                word = add_learnt_note_highlight(word)
            else:
                word = add_unlearnt_note_highlight(word)
        return word

    def add_learning_status_colour(self, text):
        pattern, words = zhonglib.extract_cjk(text)
        highlit_words = tuple(
            map(lambda w: self.add_learning_status_colour_to_word(w), words)
        )
        return pattern%highlit_words

    def refresh_learning_status_colour(self, note):
        if has_decomposition_field(note):
            field = get_decomposition_field(note)
            set_decomposition_field(note, self.add_learning_status_colour(field))
        if has_measure_word_field(note):
            field = get_measure_word_field(note)
            set_measure_word_field(note, self.add_learning_status_colour(field))

    # This function does not flush the note. 'flush' has to be called (either
    # directly or indirectly) from the caller. See 'add_mandarin_note' for
    # the only instance where it is called indirectly.
    def populate_note(self, note):
        # Extract 漢字 from card
        mandarin_text = get_mandarin_text(note, fail_if_empty=True)

        # In the following, we want to populate as many fields as possible
        # even if errors occur on previous field.  The following object
        # is used to accumulate errors.  At the end, the object is raised
        # as an exception if it actually has errors.
        errors = exception.MultiException()

        try:
            # In the following, we do two things. One, we work out whether
            # the text can possibly be in the dictionary or not.  If it's a
            # sentence, it cannot.  Second, we split the text into components.
            # This can happen no matter what the text is.  If it's a character,
            # it is split into sub-characters.  If it's a word, it's split into
            # characters.  If it's a sentence, it is is split into words.
            is_sentence = False
            if len(mandarin_text) == 1:
                decomposition = zhonglib.decompose_character(mandarin_text)
            else:
                # When segmenting sentences, only use the traditional words.
                words = zhonglib.segment(mandarin_text, zhonglib.TRADITIONAL)
                if len(words) == 1:
                    decomposition = zhonglib.decompose_word(mandarin_text)
                else:
                    is_sentence = True
                    can_lookup_dictionary = False
                    decomposition = words
        except zhonglib.ZhonglibException as e:
            decomposition = None
            errors.append(exception.MagicException(unicode(e)))

        if is_sentence:
            if has_empty_english_field(note):
                set_english_field(note, 'Cannot use dictionary to look up sentences.')
            # Should also set pinyin here from decomposition
        else:
            # The Mandarin text is either a word or a character. We can look
            # it up in the dictionary.

            # Get dictionary entries. Some character components are only defined
            # in the dictionary as simplifed, so we have to look in both.
            dictionary_entries = self.dictionary.find(
                mandarin_text, zhonglib.TRADITIONAL | zhonglib.SIMPLIFIED, include_english=False)

            if len(dictionary_entries) == 0:
                message = 'No dictionary entry for "' + mandarin_text + '"'
                errors.append(exception.MagicException(message))

            if len(dictionary_entries) > 0:
                # Add Englih
                if has_empty_english_field(note):
                    set_english_field(note, format_english(dictionary_entries))

                # Add 拼音
                if has_empty_pinyin_field(note):
                    set_pinyin_field(note, format_pinyin_list(dictionary_entries))

                # Add 量詞
                if has_empty_measure_word_field(note):
                    set_measure_word_field(note, format_measure_words(dictionary_entries))


        if decomposition != None and has_empty_decomposition_field(note):
            try:
                set_decomposition_field(\
                    note,\
                    format_decomposition(decomposition\
                ))
            except exception.MagicException as e:
                errors.append(e)

        # Whether the fields previously existed or they have just been added,
        # we want to set the colour of words according to their current learning
        # status.
        self.refresh_learning_status_colour(note)
        errors.raise_if_not_empty()
    
    def add_mandarin_note(self, model, text):
        errors = exception.MultiException()
        note = anki.notes.Note(self.mw.col, model)
        set_mandarin_field(note, text)
        try:
            self.populate_note(note)
        except exception.MagicException as e:
            errors.append(e)
        # The following will flush the note which is why we don't have to
        # do it ourselves. In fact, we have to avoid it doing it ourselves
        # because col.addNote() may fail if no cards are produced.  If this
        # is the case, then the note must not be flushed because the database
        # ends up with a note with no cards, which will not show up on the
        # browser.  In that case, you don't even know that there's a dodgy
        # note unless you dive directly into the database.
        cards_added = self.mw.col.addNote(note)
        if cards_added == 0:
            errors.append(exception.MagicException(
                'No cards were added for "' + text + '". ' +
                "Try adding manually for further clues."
            ))
        errors.raise_if_not_empty()

    def add_missing_components(self, note):

        print 'add_missing_components: note=%s', note

        # Add a note for every composition component that doesn't yet
        # have one.
        dependencies = []
        if has_decomposition_field(note):
            dependencies += get_decomposition_list(note)
        if has_measure_word_field(note):
            dependencies += get_measure_word_list(note)

        print 'add_missing_components: dependencies:',dependencies
        errors = exception.MultiException()
        for dependency in dependencies:
            if not note_exists_for_mandarin(self.mw.col, dependency):
                try:
                    self.add_mandarin_note(note.model(), dependency)
                except exception.MagicException as e:
                    errors.append(e)

        # Missing components (may) have been added. Have to update the colour
        # of words in the text to reflect this.
        self.refresh_learning_status_colour(note)
        note.flush()
        self.mw.reset(guiOnly = True)

        show_error(errors)
