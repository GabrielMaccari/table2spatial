# -*- coding: utf-8 -*-
"""
@author: Gabriel Maccari
"""

from PyQt6 import QtWidgets
from PyQt6 import QtGui
from PyQt6 import QtCore

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
        self.export_button = ToolbarButton(self, "Exportar como camada vetorial de pontos", "layers.png")
        self.layout.addWidget(self.export_button, 0, 3, 1, 1)

        # PAGINADOR
        self.frame_stack = QtWidgets.QStackedWidget(self)
        self.frame_stack.setFixedSize(410, 480)
        self.columns_stack = QtWidgets.QWidget()
        self.import_stack = QtWidgets.QWidget()
        self.merge_stack = QtWidgets.QWidget()
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
        self.import_stack_layout.addWidget(self.sheet_lbl, 0, 0, 1, 10)
        self.sheet_cbx = QtWidgets.QComboBox(self.import_stack)
        self.import_stack_layout.addWidget(self.sheet_cbx, 1, 0, 1, 10)
        self.crs_lbl = QtWidgets.QLabel("SRC:", self.import_stack)
        self.import_stack_layout.addWidget(self.crs_lbl, 2, 0, 1, 10)
        self.crs_cbx = QtWidgets.QComboBox(self.import_stack)
        self.import_stack_layout.addWidget(self.crs_cbx, 3, 0, 1, 10)
        self.x_lbl = QtWidgets.QLabel("Campo das coordenadas X:", self.import_stack)
        self.import_stack_layout.addWidget(self.x_lbl, 4, 0, 1, 10)
        self.x_cbx = QtWidgets.QComboBox(self.import_stack)
        self.import_stack_layout.addWidget(self.x_cbx, 5, 0, 1, 9)
        self.x_ok_icon = QtWidgets.QPushButton(icon=QtGui.QIcon("icons/circle.png"))
        self.x_ok_icon.setFlat(True)
        self.import_stack_layout.addWidget(self.x_ok_icon, 5, 9, 1, 1)
        self.y_lbl = QtWidgets.QLabel("Campo das coordenadas Y:", self.import_stack)
        self.import_stack_layout.addWidget(self.y_lbl, 6, 0, 1, 10)
        self.y_cbx = QtWidgets.QComboBox(self.import_stack)
        self.import_stack_layout.addWidget(self.y_cbx, 7, 0, 1, 9)
        self.y_ok_icon = QtWidgets.QPushButton(icon=QtGui.QIcon("icons/circle.png"))
        self.y_ok_icon.setFlat(True)
        self.import_stack_layout.addWidget(self.y_ok_icon, 7, 9, 1, 1)
        self.import_ok_btn = QtWidgets.QPushButton("OK", self.import_stack)
        self.import_stack_layout.addWidget(self.import_ok_btn, 8, 0, 1, 1)
        self.import_cancel_btn = QtWidgets.QPushButton("Cancelar", self.import_stack)
        self.import_stack_layout.addWidget(self.import_cancel_btn, 8, 1, 1, 1)
        self.import_stack_layout.setRowStretch(9, 1)

        # PAGINADOR → PÁGINA DE MESCLAGEM
        self.frame_stack.addWidget(self.merge_stack)
        self.merge_stack_layout = QtWidgets.QGridLayout(self.merge_stack)
        self.merge_column_lbl = QtWidgets.QLabel("Coluna de mescla", self.merge_stack)
        self.merge_stack_layout.addWidget(self.merge_column_lbl, 0, 0, 1, 10)
        self.merge_column_cbx = QtWidgets.QComboBox()
        self.merge_stack_layout.addWidget(self.merge_column_cbx, 1, 0, 1, 10)
        self.merge_ok_btn = QtWidgets.QPushButton("OK", self.merge_stack)
        self.merge_stack_layout.addWidget(self.merge_ok_btn, 2, 0, 1, 1)
        self.merge_cancel_btn = QtWidgets.QPushButton("Cancelar", self.merge_stack)
        self.merge_stack_layout.addWidget(self.merge_cancel_btn, 2, 1, 1, 1)
        self.merge_stack_layout.setRowStretch(9, 1)

        # RÓTULO INFERIOR
        self.copyright_label = QtWidgets.QLabel("©2024 Gabriel Maccari / Icons by www.icons8.com")
        self.copyright_label.setStyleSheet("font-size: 8pt")
        self.layout.addWidget(self.copyright_label, 22, 0, 1, 8)

        # Conexões dos botões de cancelar de cada página
        self.import_cancel_btn.clicked.connect(self.switch_stack)
        self.merge_cancel_btn.clicked.connect(self.switch_stack)

    def switch_stack(self, stack_index: int = 0):
        self.frame_stack.setCurrentIndex(stack_index)


class ToolbarButton(QtWidgets.QToolButton):
    def __init__(self, parent, tooltip, icon, enabled=False):
        super().__init__(parent=parent)
        self.setIcon(QtGui.QIcon(f"icons/{icon}"))
        self.setToolTip(tooltip)
        self.setFixedSize(40, 40)
        self.setEnabled(enabled)


class ListRow(QtWidgets.QWidget):
    def __init__(self, column_name, column_dtype):
        super().__init__()

        self.field = column_name
        self.dtype = column_dtype

        self.column_lbl = QtWidgets.QLabel(self)
        self.column_lbl.setText(self.field)
        self.column_lbl.setGeometry(5, 0, 230, 30)

        self.dtype_cbx = QtWidgets.QComboBox(self)
        self.dtype_cbx.setGeometry(243, 4, 120, 22)

        if self.dtype == "geometry":
            self.dtype_cbx.addItems(["Point(X,Y)"])
        else:
            self.dtype_cbx.addItems(DTYPES_DICT.keys())
            self.dtype_cbx.setCurrentText(get_dtype_key(self.dtype))

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

# ||--*--||--*--||--*--||--*--||--*--||--*--||--*--||--*--||--*--||--*--||--*--||--*--||--*--||--*--||--*--||--*--||