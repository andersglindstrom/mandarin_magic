import mmagic.gui.tool_button as tool_button
from anki.hooks import addHook
import PyQt4.QtCore as QtCore

def mmagic_add_editor_button(self):
    button = tool_button.ToolButton(self.widget)
    self.iconsBox.addWidget(button)
    button.setFocusPolicy(QtCore.Qt.NoFocus)
    # This should copy code from Anki editor.py
    # Otherwise, plastiqueStyle will be used at all times
    # and so not match other styles.
    # Maybe can get style from other editor buttons instead?
    button.setStyle(self.plastiqueStyle)

addHook("setupEditorButtons", mmagic_add_editor_button)
