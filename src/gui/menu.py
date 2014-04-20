#!/usr/bin/python

import sys
from PyQt4 import QtGui, QtCore

class Menu(QtGui.QWidget):

    def __init__(self):
        super(Menu, self).__init__()
        self.initUI()

    def initUI(self):
        self.createButton()
        self.createContextMenu()
        self.show()

    def createButton(self):
        self._button = QtGui.QPushButton('Z', self)
        self._button.setFixedHeight(20)
        self._button.setFixedWidth(20)
        self._button.setCheckable(True)
        self._button.clicked.connect(self.buttonClicked)

    def createContextMenu(self):
        self._contextMenu = QtGui.QMenu(self)
        action = self._contextMenu.addAction("Decompose")
        action.triggered.connect(self.decompose)

    def decompose(self):
        print('decompose')

    def buttonClicked(self):
        self._contextMenu.exec_(QtGui.QCursor.pos())

def main():
    app = QtGui.QApplication(sys.argv)
    ex = Menu()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
