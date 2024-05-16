# -*- coding: utf-8 -*-
"""
@author: Gabriel Maccari
"""

from PyQt6 import QtWidgets, QtGui


def show_popup(message: str, msg_type: str = "notification", details: str | None = None):
    """
    Exibe uma mensagem em popup.
    :param message: Conteúdo da popup.
    :param msg_type: "notification" ou "error". Define o ícone a ser exibido.
    :param details: String contendo informações adicionais.
    :return: Nada.
    """
    title = "Erro" if msg_type == "error" else "Notificação"
    icon = QtGui.QIcon("icons/error.png" if msg_type == "error" else "icons/info.png")

    popup = QtWidgets.QMessageBox()

    popup.setText(message)
    popup.setWindowTitle(title)
    popup.setWindowIcon(icon)

    if details is not None:
        popup.setDetailedText(details)

    popup.exec()


def show_file_dialog(caption: str, extension_filter: str|None = None, mode: str = "open",
                     parent: QtWidgets.QMainWindow = None) -> str | list[str]:
    """
    Exibe um diálogo de abertura/salvamento de arquivo.
    :param caption: Título do diálogo.
    :param extension_filter: Filtro de extensões de arquivo.
    :param mode: "open", "save" ou "directory".
    :param parent: Janela pai.
    :return: Caminho completo do arquivo (str).
    """
    if mode == "open":
        file_name, file_type = QtWidgets.QFileDialog.getOpenFileName(parent, caption=caption, filter=extension_filter)
    elif mode == "save":
        file_name, file_type = QtWidgets.QFileDialog.getSaveFileName(parent, caption=caption, filter=extension_filter)
    else:
        directory = QtWidgets.QFileDialog.getExistingDirectory(parent, caption=caption)
        return directory

    return file_name


def show_selection_dialog(message: str, items: list, selected=0, allow_edit=False,
                          title="Selecionar opções", parent: QtWidgets.QMainWindow = None) -> (str, bool):
    """
    Exibe um diálogo de seleção de opções.
    :param message: Mensagem ao usuário.
    :param items: Opções para seleção na combobox.
    :param selected: Índice da opção selecionada por padrão.
    :param allow_edit: Se verdadeiro, o usuário consegue editar os valores na combo box.
    :param title: Título da janela.
    :param parent: Janela pai.
    :return: A opção selecionada e se o botão de OK foi clicado (str, bool).
    """
    dialog = QtWidgets.QInputDialog()

    choice, ok = dialog.getItem(parent, title, message, items, selected, allow_edit)

    return choice, ok


def show_input_dialog(message: str, title: str = "Inserir", default_text: str = "",
                      parent: QtWidgets.QMainWindow = None) -> (str, bool):
    """
    Exibe um diálogo para inserção de uma string.
    :param message: Mensagem ao usuário.
    :param title: Título da janela.
    :param default_text: Texto padrão na caixa.
    :param parent: Janela pai.
    :return: O texto inserido e se o botão de OK foi clicado (str, bool)
    """
    user_input, ok = QtWidgets.QInputDialog.getText(parent, title, message, text=default_text)

    return user_input, ok


def show_question_dialog(message: str):
    """
    Exibe uma mensagem de confirmação.
    :param message: Conteúdo da popup.
    :return: Nada.
    """
    dialog = QtWidgets.QMessageBox()
    dialog.setWindowIcon(QtGui.QIcon("icons/unknown.png"))
    dialog.setWindowTitle("Confirmação")
    dialog.setText(message)
    dialog.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)

    yes_button = dialog.button(QtWidgets.QMessageBox.StandardButton.Yes)
    yes_button.setText('Sim')
    no_button = dialog.button(QtWidgets.QMessageBox.StandardButton.No)
    no_button.setText('Não')

    return dialog.exec()
