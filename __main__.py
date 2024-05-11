# -*- coding: utf-8 -*-
"""
@author: Gabriel Maccari
"""

import sys
from PyQt6.QtWidgets import QApplication
from icecream import ic

from controller import UIController

ic.configureOutput(prefix='LOG| ', includeContext=True)


class App(QApplication):
    def __init__(self, sys_argv):
        super(App, self).__init__(sys_argv)

        self.controller = UIController()


def main():
    app = App(sys.argv)

    with open('style/app_style_light.qss', 'r') as f:
        style = f.read()
    app.setStyleSheet(style)

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
