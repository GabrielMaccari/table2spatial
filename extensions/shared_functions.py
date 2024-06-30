import os
from PyQt6 import QtWidgets, QtGui, QtCore
from icecream import ic


def handle_exception(error, context, message: str = "Ocorreu um erro.", parent: QtWidgets.QMainWindow = None):
    toggle_wait_cursor(False)
    ic(context, error)
    popup = QtWidgets.QMessageBox(parent)
    popup.setWindowIcon(QtGui.QIcon("icons/error.png"))
    popup.setWindowTitle("Erro")
    popup.setText(message)
    popup.setDetailedText(f"Descrição do erro: {error}\n\nContexto: {context}")
    popup.exec()


def toggle_wait_cursor(activate: bool = True):
    if activate:
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
    else:
        QtWidgets.QApplication.restoreOverrideCursor()


def select_figure_save_location(parent: QtWidgets.QMainWindow) -> (str, str):
    """
    :param parent: Janela pai.
    :return: Caminho do arquivo, Extensão do arquivo
    """
    file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
        parent, caption="Salvar gráfico",
        filter="Formatos suportados (*.png *.jpg *.svg)"
               "PNG (*.png);;"
               "JPG (*.jpg);;"
               "SVG (*.svg)"
    )

    if file_path == "":
        return None, None

    _, file_extension = os.path.splitext(file_path)
    if not file_extension:
        file_extension = ".png"
        file_path += file_extension

    return file_path, file_extension.replace(".", "")
