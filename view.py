# -*- coding: utf-8 -*-
"""
@author: Gabriel Maccari
"""

from PyQt6 import QtWidgets, QtGui, QtCore

from model import DTYPES_DICT, get_dtype_key


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('table2spatial')
        self.setWindowIcon(QtGui.QIcon('icons/globe.png'))
        self.setMaximumSize(425, 550)

        # LAYOUT PRINCIPAL
        self.layout = QtWidgets.QGridLayout()
        self.layout.setSpacing(5)
        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.widget = QtWidgets.QWidget(self)
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        # BOTÕES DA BARRA SUPERIOR
        self.import_button = ToolbarButton(self, "Importar tabela de pontos", "excel.png", enabled=True)
        self.layout.addWidget(self.import_button, 0, 0, 1, 1)
        self.merge_button = ToolbarButton(self, "Mesclar abas do arquivo usando um campo em comum", "merge.png")
        self.layout.addWidget(self.merge_button, 0, 1, 1, 1)
        self.reproject_button = ToolbarButton(self, "Reprojetar os pontos para outro SRC", "reproject.png")
        self.layout.addWidget(self.reproject_button, 0, 2, 1, 1)
        self.export_button = ToolbarButton(self, "Exportar como camada vetorial de pontos ou tabela", "layers.png")
        self.layout.addWidget(self.export_button, 0, 3, 1, 1)
        self.graph_button = ToolbarButton(self, "Criar gráfico de dados geológicos", "graph.png", click_menu=True)
        self.layout.addWidget(self.graph_button, 0, 4, 1, 1)

        self.graph_stereogram_action = self.graph_button.click_menu.addAction("Estereograma")
        #self.graph_rosediagram_action = self.graph_button.click_menu.addAction("Diagrama de roseta")

        # PAGINADOR
        self.frame_stack = QtWidgets.QStackedWidget(self)
        self.frame_stack.setFixedSize(410, 480)
        self.columns_stack = QtWidgets.QWidget()
        self.import_stack = QtWidgets.QWidget()
        self.layout.addWidget(self.frame_stack, 1, 0, 20, 8)

        # PAGINADOR → PÁGINA DE COLUNAS
        self.frame_stack.addWidget(self.columns_stack)
        self.columns_list = QtWidgets.QListWidget(self.columns_stack)
        self.columns_list.setFixedSize(410, 480)
        self.columns_list.setIconSize(QtCore.QSize(22, 22))
        self.columns_list.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # PAGINADOR → PÁGINA DE IMPORTAÇÃO
        self.frame_stack.addWidget(self.import_stack)
        self.import_stack_layout = QtWidgets.QGridLayout(self.import_stack)
        self.sheet_lbl = QtWidgets.QLabel("Planilha:", self.import_stack)
        self.sheet_cbx = QtWidgets.QComboBox(self.import_stack)
        self.crs_lbl = QtWidgets.QLabel("SRC:", self.import_stack)
        self.crs_cbx = QtWidgets.QComboBox(self.import_stack)
        self.coords_lbl = QtWidgets.QLabel("Coordenadas:", self.import_stack)
        self.dms_chk = QtWidgets.QCheckBox("Formato GMS (GG°MM'SS.sss\")", self.import_stack)
        self.x_lbl = QtWidgets.QLabel("X:", self.import_stack)
        self.x_cbx = QtWidgets.QComboBox(self.import_stack)
        self.x_ok_icon = QtWidgets.QPushButton(icon=QtGui.QIcon("icons/circle.png"))
        self.x_ok_icon.setFlat(True)
        self.y_lbl = QtWidgets.QLabel("Y:", self.import_stack)
        self.y_cbx = QtWidgets.QComboBox(self.import_stack)
        self.y_ok_icon = QtWidgets.QPushButton(icon=QtGui.QIcon("icons/circle.png"))
        self.y_ok_icon.setFlat(True)
        self.import_ok_btn = QtWidgets.QPushButton("OK", self.import_stack)
        self.import_cancel_btn = QtWidgets.QPushButton("Cancelar", self.import_stack)
        row = 0
        self.import_stack_layout.addWidget(self.sheet_lbl, row, 0, 1, 20)
        row += 1
        self.import_stack_layout.addWidget(self.sheet_cbx, row, 0, 1, 20)
        row += 1
        self.import_stack_layout.addWidget(self.crs_lbl, row, 0, 1, 20)
        row += 1
        self.import_stack_layout.addWidget(self.crs_cbx, row, 0, 1, 20)
        row += 1
        self.import_stack_layout.addWidget(self.coords_lbl, row, 0, 1, 20)
        row += 1
        self.import_stack_layout.addWidget(self.dms_chk, row, 0, 1, 20)
        row += 1
        self.import_stack_layout.addWidget(self.x_lbl, row, 0, 1, 1)
        self.import_stack_layout.addWidget(self.x_cbx, row, 1, 1, 18)
        self.import_stack_layout.addWidget(self.x_ok_icon, row, 19, 1, 1)
        row += 1
        self.import_stack_layout.addWidget(self.y_lbl, row, 0, 1, 1)
        self.import_stack_layout.addWidget(self.y_cbx, row, 1, 1, 18)
        self.import_stack_layout.addWidget(self.y_ok_icon, row, 19, 1, 1)
        row += 1
        self.import_stack_layout.addWidget(self.import_ok_btn, row, 0, 1, 4)
        self.import_stack_layout.addWidget(self.import_cancel_btn, row, 4, 1, 4)
        row += 1
        self.import_stack_layout.setRowStretch(row, 1)

        # RÓTULO INFERIOR
        self.copyright_label = QtWidgets.QLabel("©2024 Gabriel Maccari / Icons by www.icons8.com")
        self.copyright_label.setStyleSheet("font-size: 8pt")
        self.layout.addWidget(self.copyright_label, 22, 0, 1, 8)

        # Conexões dos botões de cancelar de cada página
        self.import_cancel_btn.clicked.connect(self.switch_stack)

    def switch_stack(self, stack_index: int = 0):
        self.frame_stack.setCurrentIndex(stack_index)


class ToolbarButton(QtWidgets.QToolButton):
    def __init__(self, parent, tooltip, icon, enabled=False, click_menu=False):
        super().__init__(parent=parent)
        self.setIcon(QtGui.QIcon(f"icons/{icon}"))
        self.setToolTip(tooltip)
        self.setFixedSize(40, 40)
        self.setEnabled(enabled)
        self.click_menu = None

        if click_menu:
            self.click_menu = QtWidgets.QMenu(self)


class ListRow(QtWidgets.QWidget):
    def __init__(self, column_name, column_dtype):
        super().__init__()

        self.field = column_name
        self.dtype = column_dtype

        self.column_lbl = QtWidgets.QLabel(self)
        self.column_lbl.setText(self.field)
        self.column_lbl.setGeometry(5, 0, 225, 30)

        self.dtype_cbx = QtWidgets.QComboBox(self)
        self.dtype_cbx.setGeometry(240, 4, 120, 22)

        if self.dtype == "geometry":
            self.dtype_cbx.addItems(["Point(X,Y)"])
        else:
            self.dtype_cbx.addItems(DTYPES_DICT.keys())
            self.dtype_cbx.setCurrentText(get_dtype_key(self.dtype))

            self.context_menu = QtWidgets.QMenu(self)
            self.rename_action = self.context_menu.addAction(QtGui.QIcon("icons/rename.png"), "Renomear")
            self.delete_action = self.context_menu.addAction(QtGui.QIcon("icons/delete.png"), "Excluir")
            self.show_uniques_action = self.context_menu.addAction(QtGui.QIcon("icons/list.png"), "Listar valores únicos")

    def get_icon(self):
        try:
            if self.dtype == "geometry":
                img = "icons/geometry"
            else:
                dt_key = get_dtype_key(self.dtype)
                img = DTYPES_DICT[dt_key]["icon"]
        except KeyError:
            img = "icons/unknown"
        return QtGui.QIcon(img)

    def contextMenuEvent(self, event):
        self.context_menu.exec(event.globalPos())


class ListWindow(QtWidgets.QMainWindow):
    def __init__(self, values_list: list[any], has_nan: bool, parent):
        super(ListWindow, self).__init__(parent)
        self.parent = parent

        self.setWindowTitle('Valores únicos')
        self.setWindowIcon(QtGui.QIcon('icons/list.png'))

        self.layout = QtWidgets.QVBoxLayout()

        self.widget = QtWidgets.QWidget()
        self.widget.setLayout(self.layout)

        self.setCentralWidget(self.widget)

        self.list_wgt = QtWidgets.QListWidget(self)
        self.list_wgt.addItems(values_list)
        self.layout.addWidget(self.list_wgt)

        if has_nan:
            self.nan_lbl = QtWidgets.QLabel("Obs: A coluna possui células vazias/nulas.")
            self.layout.addWidget(self.nan_lbl)

        self.close_button = QtWidgets.QPushButton("Fechar")
        self.close_button.clicked.connect(self.close)
        self.layout.addWidget(self.close_button)


def center_window_on_point(window, center_point):
    geometry = window.geometry()
    geometry.moveCenter(center_point)
    window.move(geometry.topLeft())

# ||--*--||--*--||--*--||--*--||--*--||--*--||--*--||--*--||--*--||--*--||--*--||--*--||--*--||--*--||--*--||--*--||
