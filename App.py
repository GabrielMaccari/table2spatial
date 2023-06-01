# -*- coding: utf-8 -*-
"""
@author: Gabriel Maccari
"""
import sys

from PyQt6 import QtWidgets

from Model import GeographicTable
from ViewController import AppMainWindow
from Controller import MainController


class App(QtWidgets.QApplication):
    def __init__(self, sys_argv):
        super(App, self).__init__(sys_argv)

        self.controller = MainController(GeographicTable)
        self.view = AppMainWindow(self.controller)

        self.view.show()


def main():
    app = App(sys.argv)

    with open('style/app_style_light.qss', 'r') as f:
        style = f.read()
    app.setStyleSheet(style)

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
