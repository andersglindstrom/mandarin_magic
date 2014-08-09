#!/usr/bin/env python

import sys
from PyQt4 import QtGui, QtCore

class ToolButton(QtGui.QPushButton):

    decompose = QtCore.pyqtSignal()
    define = QtCore.pyqtSignal()

    def __init__(self, parent):
        super(ToolButton, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.configureButton()
        self.createContextMenu()
        self.show()

    def configureButton(self):
        self.setText('Z')
        self.setFixedHeight(20)
        self.setFixedWidth(20)
#        self.setCheckable(True)
        self.clicked.connect(self.buttonClicked)

    def createContextMenu(self):
        self._contextMenu = QtGui.QMenu(self)

        action = self._contextMenu.addAction("Decompose")
        action.triggered.connect(self.emit_decompose)

        action = self._contextMenu.addAction("Define")
        action.triggered.connect(self.emit_define)

    def emit_decompose(self):
        self.decompose.emit()

    def emit_define(self):
        self.define.emit()

    def buttonClicked(self):
        self._contextMenu.exec_(QtGui.QCursor.pos())

class MenuDemo(QtGui.QWidget):

    def __init__(self):
        super(MenuDemo, self).__init__()
        self.initUI()

    def initUI(self):
        menu = ToolButton(self)
        menu.decompose.connect(self.decompose)
        self.show()

    def decompose(self):
        print('Decompose')

def main():
    app = QtGui.QApplication(sys.argv)
    ex = MenuDemo()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
