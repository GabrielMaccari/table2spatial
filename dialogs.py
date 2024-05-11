# -*- coding: utf-8 -*-
"""
@author: Gabriel Maccari
"""

from PyQt6 import QtWidgets, QtGui


def show_popup(message: str, msg_type: str = "notification"):
    """
    Exibe uma mensagem em popup.
    :param message: Conteúdo da popup.
    :param msg_type: "notification" ou "error". Define o ícone a ser exibido.
    :return: Nada.
    """
    popup_types = {
        "notification": {"title": "Notificação", "icon": "icons/globe.png"},
        "error":        {"title": "Erro",        "icon": "icons/error.png"}
    }
    title = popup_types[msg_type]["title"]
    icon = QtGui.QIcon(popup_types[msg_type]["icon"])

    popup = QtWidgets.QMessageBox()
    popup.setText(message)
    popup.setWindowTitle(title)
    popup.setWindowIcon(icon)

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


def show_selection_dialog(message: str, items: list, selected=0,
                          title="Selecionar opções", parent: QtWidgets.QMainWindow = None) -> (str, bool):
    """
    Exibe um diálogo de seleção de opções.
    :param message: Mensagem ao usuário.
    :param items: Opções para seleção na combobox.
    :param selected: Índice da opção selecionada por padrão.
    :param title: Título da janela.
    :param parent: Janela pai.
    :return: A opção selecionada e se o botão de OK foi clicado (str, bool).
    """
    dialog = QtWidgets.QInputDialog()
    combo_box = dialog.findChild(QtWidgets.QComboBox)
    if combo_box is not None:
        combo_box.setEditable(True)
        combo_box.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.NoInsert)
        combo_box.completer().setCompletionMode(QtWidgets.QCompleter.CompletionMode.PopupCompletion)

    choice, ok = dialog.getItem(parent, title, message, items, selected)

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
