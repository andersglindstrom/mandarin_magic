
from mmagic.gui.main_object import MainObject
from aqt import mw
from anki.hooks import addHook

main_object = MainObject(mw)

def setup_browser_menu(browser):
    main_object.setup_browser_menu(browser)

addHook("browser.setupMenus", setup_browser_menu)
