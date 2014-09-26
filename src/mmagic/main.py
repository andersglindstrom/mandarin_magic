
from mmagic.gui.main_object import MainObject
from aqt import mw
from anki.hooks import addHook

main_object = MainObject(mw)

def setup_browser_menu(browser):
    main_object.setup_browser_menu(browser)

addHook("browser.setupMenus", setup_browser_menu)

def setup_editor_button(editor):
    main_object.setup_editor_buttons(editor)

addHook("setupEditorButtons", setup_editor_button)

def before_state_change(state, old_state):
    print 'before_state_change:', state

addHook("beforeStateChange", before_state_change)
