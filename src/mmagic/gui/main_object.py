# -*- coding: utf-8 -*-

import operator

from PyQt4 import QtGui
from PyQt4.QtGui import QPushButton

import aqt.utils
import anki.notes
import anki.utils
import mmagic.core.exception as exception
import mmagic.zhonglib as zl

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
        notes = collection.findNotes('%s:"%s"'%(field,value))
        result += notes
    return result

def find_notes_for_word(collection, word):
    return find_notes(collection, MANDARIN_FIELDS, word)

def note_exists_for_mandarin(collection, word):
    return len(find_notes_for_word(collection, word)) > 0

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
    return zl.format_pinyin_sequence(zl.parse_cedict_pinyin(text))

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

# Returns the decomposition components as a list. A new list is returned. It
# can be modified by the client.
def get_decomposition_list(note):
    field = get_decomposition_field(note)
    field = anki.utils.stripHTML(field.strip().rstrip())
    if field == 'None':
        return []
    pattern, words = zl.extract_cjk(field)
    return list(words)

def get_measure_word_list(note):
    field = get_measure_word_field(note)
    field = anki.utils.stripHTML(field.strip().rstrip())
    if len(field) == 0:
        return []
    pattern, words = zl.extract_cjk(field)
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
        self.dictionary = zl.standard_dictionary()

    def add_browser_action(self, name, callback, browser):
        action = QtGui.QAction(name, self.mw)
        action.triggered.connect(callback)
        browser.form.menuEdit.addAction(action)

    def setup_browser_menu(self, browser):
        self.add_browser_action(
            "Populate",
            lambda: self.populate_from_browser(browser),
            browser)

        self.add_browser_action(
            "Export to Skritter",
            lambda: self.export_to_skritter(browser),
            browser)

        self.add_browser_action(
            "Mark cards with missing dependencies",
            lambda: self.mark_cards_with_missing_dependencies(browser),
            browser)

        self.add_browser_action(
            "Mark all dependencies",
            lambda: self.mark_all_dependencies(browser),
            browser)

        self.add_browser_action(
            "Add missing dependencies",
            lambda: self.add_missing_dependencies(browser),
            browser)

    def get_note(self, note_id):
        return self.mw.col.getNote(note_id)

    # Returns a pair: (result, errors)
    def get_transitive_dependencies(self, note_id, depth=0):
        all_notes = [note_id]
        all_errors = exception.MultiException()

        dependencies = get_decomposition_list(self.get_note(note_id))
        for dependency in dependencies:
            note_ids = find_notes_for_word(self.mw.col, dependency)
            if len(note_ids) > 1:
                all_errors.append(exception.MagicException('More than one note for "%s"'%dependency))
                continue
            if len(note_ids) == 0:
                all_errors.append(exception.MagicException('No note for "%s"'%dependency))
                continue
            dependency_id = note_ids[0]
            notes, errors = self.get_transitive_dependencies(dependency_id, depth+1)
            all_notes += notes
            all_errors.append(errors)
        return (all_notes, all_errors)

    def add_tag(self, browser, note_ids, tag):
        # Code taken from anki/aqt/browser.py(addTags method).
        # This is a bit nasty because I'm using the "browser.model" field,
        # which is really a private field.
        browser.model.beginReset()
        self.mw.col.tags.bulkAdd(note_ids, tag)
        browser.model.endReset()
        self.mw.requireReset()

    # Returns (result, errors pair) where result is a dictionary with
    # the word as key and the note_id as value
    def get_note_ids_for_words(self, words):
        result = {}
        errors = exception.MultiException()
        for word in words:
            note_ids = find_notes_for_word(self.mw.col, word)
            if len(note_ids) > 1:
                errors.append(exception.MagicException('More than one note for "%s"'%word))
                continue
            if len(note_ids) == 0:
                errors.append(exception.MagicException('No note for "%s"'%word))
                continue
            result[word] = note_ids[0]
        return (result, errors)

    def word_has_notes(self, word):
        return len(find_notes_for_word(self.mw.col, word)) > 0

    def note_has_missing_dependencies(self, note_id):
        result = False
        dependencies = []
        note = self.get_note(note_id)
        if has_decomposition_field(note):
            field = get_decomposition_field(note)
            pattern, words = zl.extract_cjk(field)
            dependencies += words
        if has_measure_word_field(note):
            field = get_measure_word_field(note)
            pattern, words = zl.extract_cjk(field)
            dependencies += words
        notes_exist = map(lambda word: self.word_has_notes(word), dependencies)
        all_exist = reduce(operator.and_, notes_exist, True)
        print 'notes_exist:',notes_exist
        print 'all_exist:',all_exist

        result = not all_exist
        print 'result:', result
        return result

    def mark_cards_with_missing_dependencies(self, browser):
        selected_notes = browser.selectedNotes()
        if not selected_notes:
            aqt.utils.showInfo("No notes selected.", browser)
            return
        errors = exception.MultiException()
        notes_to_mark = []
        for note_id in selected_notes:
            try:
                if self.note_has_missing_dependencies(note_id):
                    notes_to_mark.append(note_id)
            except exception.MagicException as e:
                errors.append(e)
        print 'marking notes:',notes_to_mark
        self.add_tag(browser, notes_to_mark, 'marked')
        show_error(errors)

    def add_missing_dependencies(self, browser):
        selected_notes = browser.selectedNotes()
        if not selected_notes:
            aqt.utils.showInfo("No notes selected.", browser)
            return
        errors = exception.MultiException()
        for note_id in selected_notes:
            try:
                note = self.get_note(note_id)
                self.add_missing_dependencies_to_note(note)
            except exception.MagicException as e:
                errors.append(e)
        # Refresh editor
        browser.editor.setNote(browser.editor.note)
        show_error(errors)

    def mark_all_dependencies(self, browser):
        selected_notes = browser.selectedNotes()
        if not selected_notes:
            aqt.utils.showInfo("No notes selected.", browser)
            return
        all_errors = exception.MultiException()
        all_notes = list(selected_notes)
        for note_id in selected_notes:
            notes, errors = self.get_transitive_dependencies(note_id)
            all_notes += notes
            all_errors.append(errors)
        self.add_tag(browser, all_notes, 'marked')
        show_error(all_errors)

    def export_to_skritter(self, browser):
        # Generate the dependency graph and then sort topologically.

        print 'export_to_skritter'

        # Generate the dependency graph.
        #
        # We have to add all the selected characters and all the characters
        # they depend on to the graph.

        selected_notes = browser.selectedNotes()
        if not selected_notes:
            aqt.utils.showInfo("No notes selected.", browser)
            return

        # Export words selected in browser.
        words = []
        for note_id in selected_notes:
            note = self.get_note(note_id)
            words.append(get_mandarin_text(note))

        # Only export characters (although Skitter seems to work for words
        # too).
        selected_characters = set(filter(lambda word: len(word) == 1, words))

        chars_and_ids, errors = self.get_note_ids_for_words(selected_characters)

        if len(errors) > 0:
            show_error(errors)
            return

        # Now, generate the dependency graph.
        dependency_graph = {}
        for char, note_id in chars_and_ids.iteritems():
            note = self.get_note(note_id)

            # Now get the dependencies for the note but only include
            # characters that are in the selected characters.
            dependencies = get_decomposition_list(note)
            dependencies = filter(lambda d: d in selected_characters, dependencies)

            dependency_graph[char] = dependencies

        # Sort topologically
        for_export = zl.topological_sort(dependency_graph)
        # Remove any characters that have already been exported
        #for_export = filter(lambda c: c not in already_exported, for_export)

        if len(for_export) == 0:
            aqt.utils.showInfo('There are no characters to export. They may have already been exported. Check tags.', browser)
            return

        # Now copy characters to clipboad so that they can be pasted in to
        # Skritter. Skritter has a 200 word limit per section, so we only
        # copy max 200 characters at a time.  After each section, we wait
        # for the user to prompt us for the next batch.

        section_size = 200
        def export(section):
            print 'len(section):',len(section)
            assert len(section) <= section_size
            text = unicode()
            for c in section:
                text += c + '\n'

            QtGui.QApplication.clipboard().setText(text)

            ids = map(lambda char: chars_and_ids[char], section)
            print 'adding export_to_skritter to', ids
            self.add_tag(browser, ids, 'exported_to_skritter')


        while len(for_export) > section_size:

            section = for_export[0:section_size]
            for_export = for_export[section_size:]

            export(section)

            result = aqt.utils.askUser('%s characters copied to clipboard.  There are more characters remaining. Press OK when you want more characters to be copied.'%section_size, browser)
            if not result:
                return

        assert len(for_export) <= section_size
        export(for_export)
        aqt.utils.showInfo("%s characters copied to clipboard for pasting into Skritter."%len(for_export), browser)

        print 'exiting exported_to_skritter'
        # Refresh editor
        browser.editor.setNote(browser.editor.note)


    def populate_from_browser(self, browser):
        selected_notes = browser.selectedNotes()
        if not selected_notes:
            aqt.utils.showInfo("No notes selected.", browser)
            return
        errors = exception.MultiException()
        for note_id in selected_notes:
            note = self.get_note(note_id)
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
        # Refresh the editor
        browser.editor.setNote(browser.editor.note)
        aqt.utils.showInfo('Done.', browser)

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
        # Note that shortcut is Alt-P
        self.setup_button(editor, '&P', lambda: self.populate_and_save_note(editor))
        self.setup_button(editor, '+', lambda: self.add_missing_components_from_editor(editor))

    def populate_and_save_note(self, editor):
        note = editor.note
        try:
            self.populate_note(note)
            note.flush()
        except exception.MagicException as e:
            show_error(e)
        finally:
            # Refresh editor
            editor.setNote(note)

    def add_missing_components_from_editor(self, editor):
        try:
            self.add_missing_dependencies_to_note(editor.note)
        except exception.MagicException as e:
            show_error(e)
        finally:
            # Refresh editor
            editor.setNote(editor.note)

    def add_learning_status_colour_to_word(self, word):
        # Find all notes that have the given word as the Mandarin field
        note_ids = find_notes_for_word(self.mw.col, word)
        if len(note_ids) == 0:
            word = add_missing_note_highlight(word)
        else:
            # Find out whether each note is learnt or not.
            notes_are_learnt = map(
                lambda note_id: note_is_learnt(self.get_note(note_id)),
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
        pattern, words = zl.extract_cjk(text)
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
                decomposition = zl.decompose_character(mandarin_text, stop_at_strokes=False)
            else:
                # When segmenting sentences, only use the traditional words.
                words = zl.segment(mandarin_text, zl.TRADITIONAL)
                if len(words) == 1:
                    decomposition = zl.decompose_word(mandarin_text)
                else:
                    is_sentence = True
                    can_lookup_dictionary = False
                    decomposition = words
        except zl.ZhonglibException as e:
            decomposition = None
            errors.append(exception.MagicException(unicode(e)))

        if is_sentence:
            if has_empty_english_field(note):
                set_english_field(note, 'Cannot use dictionary to look up sentences')
            # Should also set pinyin here from decomposition
        else:
            # The Mandarin text is either a word or a character. We can look
            # it up in the dictionary.

            # Get dictionary entries. Some character components are only defined
            # in the dictionary as simplifed, so we have to look in both.
            dictionary_entries = self.dictionary.find(
                mandarin_text, zl.TRADITIONAL | zl.SIMPLIFIED, include_english=False)

            if len(dictionary_entries) == 0:
                message = 'No dictionary entry for "' + mandarin_text + '"'
                errors.append(exception.MagicException(message))
                if has_empty_english_field(note):
                    set_english_field(note, "No dictionary entry")

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

    def add_missing_dependencies_to_note(self, note):
        # Add a note for every composition component that doesn't yet
        # have one.
        dependencies = []
        if has_decomposition_field(note):
            dependencies += get_decomposition_list(note)
        if has_measure_word_field(note):
            dependencies += get_measure_word_list(note)

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

        errors.raise_if_not_empty()
