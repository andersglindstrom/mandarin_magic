# -*- coding: utf-8 -*-

from PyQt4 import QtGui
from aqt import mw, utils
from mmagic.core.exception import MagicException
import mmagic.zhonglib

ENGLISH_FIELD='English'
MANDARIN_FIELD=u'漢字'
PINYIN_FIELD=u'拼音'

def get_mandarin_word(note):
    if not MANDARIN_FIELD in note.keys():
        raise MagicException("Missing field: " + MANDARIN_FIELD)
    return note[MANDARIN_FIELD]

def get_english_definition(note):
    if not ENGLISH_FIELD in note.keys():
        raise MagicException("Missing field: " + ENGLISH_FIELD)
    return note[ENGLISH_FIELD]

def format_definition(dictionary_entries):
    result = dictionary_entries[0].meaning
    for idx in xrange(1, len(dictionary_entries)):
        result += '\n' + entry[idx].meaning
    return result

class MainObject:

    def __init__(self, anki_main_window):
        self.mw = anki_main_window
        self.define_action = QtGui.QAction("Define", self.mw)
        self.define_action.triggered.connect(self.do_define)
        self.dictionary = mmagic.zhonglib.standard_dictionary()

    def setup_browser_menu(self, browser):
        self.browser = browser
        self.browser.form.menuEdit.addAction(self.define_action)

    def do_define(self):
        selected_notes = self.browser.selectedNotes()
        if not selected_notes:
            utils.showInfo("No notes selected.")
            return
        try:
            for note_id in selected_notes:
                self.do_define_for_note(note_id)
        except MagicException as e:
            utils.showInfo(e.message())

    def do_define_for_note(self, note_id):
        note = mw.col.getNote(note_id)
        print "Doing define for note", note
        print note.keys()
        print note.model()
        # Extract Mandarin from card
        mandarin_word = get_mandarin_word(note)
        print 'Mandarin word is', mandarin_word
        # Get definition
        dictionary_entries = self.dictionary.find(mandarin_word)
        if len(dictionary_entries) == 0:
            raise MagicException('No dictionary entry for "' + mandarin_word + '"')

        # If not defined, add it to 'English' field
        english_definition = get_english_definition(note)
        #if english_definition == '':
            #note[ENGLISH_FIELD] = format_definition(dictionary_entries)
        note[ENGLISH_FIELD] = 'Test definition'
        print 'Field is now:', note[ENGLISH_FIELD]
        note.flush()
        mw.reset()
        # If not defined, add pinyin pronunciations

