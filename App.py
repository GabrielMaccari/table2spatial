import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QIcon

from Model import GeographicTable
from View import AppMainWindow
from Controller import MainController


class App(QApplication):
    def __init__(self, sys_argv):
        super(App, self).__init__(sys_argv)

        self.model = GeographicTable()
        self.controller = MainController(self.model)
        self.view = AppMainWindow(self.model, self.controller)

        self.view.show()


if __name__ == '__main__':
    app = App(sys.argv)

    with open('app_style.qss', 'r') as f:
        style = f.read()
    app.setStyleSheet(style)

    sys.exit(app.exec())