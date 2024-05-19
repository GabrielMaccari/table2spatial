# -*- coding: utf-8 -*-
"""
@author: Gabriel Maccari
"""

import sys
from PyQt6.QtWidgets import QApplication
from icecream import ic
from platform import platform
from PyQt6 import sip  # necessário para criar o exe com pyinstaller

from controller import UIController

ic.configureOutput(prefix='LOG| ', includeContext=True)
OS = platform()


class App(QApplication):
    def __init__(self, sys_argv):
        super(App, self).__init__(sys_argv)
        self.controller = UIController()


if __name__ == '__main__':
    app = App(sys.argv)
    app.setStyle("windowsvista" if OS.startswith("Win") else "Breeze")
    with open('style/win11_light.qss', 'r') as f:
        style = f.read()
    app.setStyleSheet(style)
    sys.exit(app.exec())
