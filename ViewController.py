# -*- coding: utf-8 -*-
"""
@author: Gabriel Maccari
"""
import folium

from PyQt6 import QtWidgets
from PyQt6 import QtGui
from PyQt6 import QtCore
from PyQt6 import QtWebEngineWidgets  # pip install PyQt6-WebEngine
from io import BytesIO
from folium.plugins import MeasureControl, MousePosition, Geocoder

from Model import DTYPE_DICT, crs_dict


class AppMainWindow(QtWidgets.QMainWindow):

    def __init__(self, controller):

        super().__init__()

        self.controller = controller

        self.file_open = False

        self.setWindowTitle('table2spatial')
        self.setWindowIcon(QtGui.QIcon('icons/globe.png'))
        self.setMaximumSize(425, 550)

        layout = QtWidgets.QGridLayout()
        layout.setSpacing(5)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft)

        self.open_file_btn = QtWidgets.QToolButton(self)
        self.open_file_btn.setToolTip("Importar tabela de pontos")
        self.open_file_btn.setIcon(QtGui.QIcon("icons/excel.png"))
        self.open_file_btn.setMinimumSize(40, 40)
        self.open_file_btn.setMaximumSize(40, 40)
        self.open_file_btn.clicked.connect(self.open_file_btn_clicked)

        self.merge_btn = QtWidgets.QToolButton(self)
        self.merge_btn.setToolTip("Mesclar abas do arquivo usando um campo em comum")
        self.merge_btn.setIcon(QtGui.QIcon("icons/merge.png"))
        self.merge_btn.setMinimumSize(40, 40)
        self.merge_btn.setMaximumSize(40, 40)
        self.merge_btn.clicked.connect(self.merge_btn_clicked)
        self.merge_btn.setEnabled(False)

        self.crs_settings_btn = QtWidgets.QToolButton(self)
        self.crs_settings_btn.setToolTip("Configurar SRC e campos de coordenadas")
        self.crs_settings_btn.setIcon(QtGui.QIcon("icons/settings.png"))
        self.crs_settings_btn.setMinimumSize(40, 40)
        self.crs_settings_btn.setMaximumSize(40, 40)
        self.crs_settings_btn.clicked.connect(self.crs_settings_btn_clicked)
        self.crs_settings_btn.setEnabled(False)

        self.reproject_btn = QtWidgets.QToolButton(self)
        self.reproject_btn.setToolTip("Reprojetar coordenadas para outro SRC")
        self.reproject_btn.setIcon(QtGui.QIcon("icons/reproject.png"))
        self.reproject_btn.setMaximumSize(40, 40)
        self.reproject_btn.setMaximumSize(40, 40)
        self.reproject_btn.clicked.connect(self.reproject_btn_clicked)
        self.reproject_btn.setEnabled(False)

        self.save_table_btn = QtWidgets.QToolButton(self)
        self.save_table_btn.setToolTip("Exportar como CSV")
        self.save_table_btn.setIcon(QtGui.QIcon("icons/table.png"))
        self.save_table_btn.setMinimumSize(40, 40)
        self.save_table_btn.setMaximumSize(40, 40)
        self.save_table_btn.clicked.connect(self.save_table_btn_clicked)
        self.save_table_btn.setEnabled(False)

        self.save_layer_btn = QtWidgets.QToolButton(self)
        self.save_layer_btn.setToolTip("Exportar como camada vetorial de pontos")
        self.save_layer_btn.setIcon(QtGui.QIcon("icons/layers.png"))
        self.save_layer_btn.setMinimumSize(40, 40)
        self.save_layer_btn.setMaximumSize(40, 40)
        self.save_layer_btn.clicked.connect(self.save_layer_btn_clicked)
        self.save_layer_btn.setEnabled(False)

        self.map_preview_btn = QtWidgets.QToolButton(self)
        self.map_preview_btn.setToolTip("Visualizar uma prévia dos dados em mapa")
        self.map_preview_btn.setIcon(QtGui.QIcon("icons/map.png"))
        self.map_preview_btn.setMinimumSize(40, 40)
        self.map_preview_btn.setMaximumSize(40, 40)
        self.map_preview_btn.clicked.connect(self.map_preview_btn_clicked)
        self.map_preview_btn.setEnabled(False)

        self.df_columns_lsw = QtWidgets.QListWidget(self)
        self.df_columns_lsw.setMinimumSize(410, 480)
        self.df_columns_lsw.setMaximumSize(410, 480)
        self.df_columns_lsw.setIconSize(QtCore.QSize(22, 22))
        self.df_columns_lsw.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        copyright_lbl = QtWidgets.QLabel("©2023 Gabriel Maccari / Icons by www.icons8.com")
        copyright_lbl.setStyleSheet("font-size: 8pt")

        layout.addWidget(self.open_file_btn, 0, 0, 1, 1)
        layout.addWidget(self.merge_btn, 0, 1, 1, 1)
        layout.addWidget(self.crs_settings_btn, 0, 2, 1, 1)
        layout.addWidget(self.reproject_btn, 0, 3, 1, 1)
        layout.addWidget(self.save_table_btn, 0, 4, 1, 1)
        layout.addWidget(self.save_layer_btn, 0, 5, 1, 1)
        layout.addWidget(self.map_preview_btn, 0, 6, 1, 1)
        layout.addWidget(self.df_columns_lsw, 1, 0, 20, 8)
        layout.addWidget(copyright_lbl, 22, 0, 1, 8)

        widget = QtWidgets.QWidget(self)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def open_file_btn_clicked(self):
        try:
            path = show_file_dialog(
                caption="Selecione uma tabela contendo os dados de entrada.",
                extension_filter=("Formatos suportados (*.xlsx *.xlsm *.csv *.ods);;"
                                  "Pasta de Trabalho do Excel (*.xlsx);;"
                                  "Pasta de Trabalho Habilitada para Macro do Excel (*.xlsm);;"
                                  "Comma Separated Values (*.csv);; "
                                  "OpenDocument Spreadsheet (*.ods)"),
                mode="open", parent=self
            )

            if path == "":
                return

            new_file_opened, multiple_sheets = self.controller.open_file(path)

            if not new_file_opened:
                return

            self.update_list()
            self.merge_btn.setEnabled(multiple_sheets)
            self.save_table_btn.setEnabled(True)
            self.crs_settings_btn.setEnabled(True)
            self.reproject_btn.setEnabled(False)
            self.save_layer_btn.setEnabled(False)
            self.map_preview_btn.setEnabled(False)

        except Exception as exception:
            show_popup(f"Não foi possível abrir o arquivo.\n\nMotivo: {exception}", "error")

    def update_list(self):
        try:
            self.df_columns_lsw.clear()

            columns = self.controller.get_df_columns()
            dtypes = self.controller.get_df_dtypes()

            row = 0
            self.column_list_widgets = []
            self.dtypes_list = []

            for column_name, column_type in zip(columns, dtypes):
                widget = ListRow(column_name, str(column_type))
                widget.dtype_cbx.currentTextChanged.connect(lambda dtype_change, x=row: self.column_dtype_changed(x))

                self.column_list_widgets.append(widget)
                self.dtypes_list.append(str(column_type))

                item = QtWidgets.QListWidgetItem()
                item.setIcon(widget.get_icon())
                item.setSizeHint(QtCore.QSize(410, 30))
                self.df_columns_lsw.addItem(item)
                self.df_columns_lsw.setItemWidget(item, widget)
                row += 1

        except Exception as exception:
            show_popup(f"Não foi possível atualizar a lista com os dados do arquivo.\n\nMotivo: {exception}", "error")

    def merge_btn_clicked(self):
        try:
            self.controller.merge_sheets()
            self.update_list()

        except Exception as exception:
            show_popup(f"Não foi possível mesclar as abas do arquivo.\n\nMotivo: {exception}", "error")

    def column_dtype_changed(self, row):
        switched = False
        target_dtype = "object"

        try:
            # Seleciona o widget da linha
            widget = self.column_list_widgets[row]
            # Obtém o nome da coluna
            field = widget.column_lbl.text()
            # Obtém o tipo de dado para o qual o usuário deseja converter
            target_dtype_key = widget.dtype_cbx.currentText()
            target_dtype = DTYPE_DICT[target_dtype_key]["pandas_type"]
            # Tenta realizar a conversão
            switched = self.controller.switch_dtype(field, target_dtype)

        # Exibe uma popup em caso de erro
        except Exception as exception:
            show_popup(f"Não foi possível converter.\n\nMotivo: {exception}", "error")

        if switched:
            self.dtypes_list[row] = target_dtype

        self.update_list()

    def crs_settings_btn_clicked(self):
        show_wait_cursor()

        try:
            crs_window = CRSSettingsWindow(self, self.controller)
            crs_window.show()

        except Exception as exception:
            show_popup(f"Não foi possível abrir a janela de configuração do SRC\n\nMotivo: {exception}", "error")

        show_wait_cursor(False)

    def reproject_btn_clicked(self):
        show_wait_cursor()

        try:
            reproject_window = ReprojectWindow(self, self.controller)
            reproject_window.show()

        except Exception as exception:
            show_popup(f"Não foi possível abrir a janela de reprojeção\n\nMotivo: {exception}", "error")

        show_wait_cursor(False)

    def save_table_btn_clicked(self):
        try:
            self.controller.save_csv()

        except Exception as exception:
            show_popup(f"Não foi possível salvar o arquivo CSV.\n\nMotivo: {exception}", "error")

    def save_layer_btn_clicked(self):
        try:
            self.controller.build_gdf()
            saved = self.controller.save_points()

            if saved:
                show_popup("Exportado com sucesso!")
                self.map_preview_btn.setEnabled(True)

        except Exception as exception:
            show_popup(f"Não foi possível exportar o arquivo de pontos.\n\nMotivo: {exception}", "error")

    def map_preview_btn_clicked(self):
        show_wait_cursor()

        try:
            gdf = self.controller.get_model_attribute("gdf")
            map_window = MapWindow(self, gdf)
            map_window.show()

        except Exception as exception:
            show_popup(f"Não foi possível gerar o mapa.\n\nMotivo: {exception}", "error")

        show_wait_cursor(False)


class ListRow(QtWidgets.QWidget):

    def __init__(self, column_name, column_dtype):

        super().__init__()

        self.field = column_name
        self.dtype = column_dtype

        self.column_lbl = QtWidgets.QLabel(self)
        self.column_lbl.setText(self.field)
        self.column_lbl.setGeometry(5, 0, 260, 30)

        self.dtype_cbx = QtWidgets.QComboBox(self)
        self.dtype_cbx.setGeometry(273, 4, 90, 22)
        self.dtype_cbx.addItems(DTYPE_DICT.keys())
        key = self.get_dtype_key()
        self.dtype_cbx.setCurrentText(key)

    def get_icon(self):
        dt_values = DTYPE_DICT.values()
        img = next(subdict["icon"] for subdict in dt_values if subdict["pandas_type"] == self.dtype)
        return QtGui.QIcon(img)

    def get_dtype_key(self):
        dt_items = DTYPE_DICT.items()
        key = next(key for key, subdict in dt_items if subdict["pandas_type"] == self.dtype)
        return key


class CRSSettingsWindow(QtWidgets.QMainWindow):

    def __init__(self, parent, controller):
        super(CRSSettingsWindow, self).__init__(parent)

        self.parent = parent
        self.controller = controller

        self.setWindowTitle('Configurações de SRC')
        self.setWindowIcon(QtGui.QIcon('icons/globe.png'))
        self.setMinimumWidth(400)

        layout = QtWidgets.QGridLayout()
        layout.setVerticalSpacing(6)
        layout.setHorizontalSpacing(3)

        self.crs_lbl = QtWidgets.QLabel("SRC dos dados de entrada")
        self.crs_lbl.setStyleSheet("font-size: 11pt;")

        self.crs_cbx = QtWidgets.QComboBox()
        self.crs_cbx.currentTextChanged.connect(self.crs_changed)

        self.coord_fields_lbl = QtWidgets.QLabel("Campos de coordenadas")
        self.coord_fields_lbl.setStyleSheet("font-size: 11pt;")

        self.y_icn = QtWidgets.QLabel()
        self.y_icn.setPixmap(QtGui.QPixmap("icons/lat.png").scaled(
            22, 22, transformMode=QtCore.Qt.TransformationMode.SmoothTransformation)
        )
        self.y_lbl = QtWidgets.QLabel("Latitude/Northing")
        self.y_cbx = QtWidgets.QComboBox()
        self.y_cbx.setToolTip("A coluna da tabela que contém a coordenada Y (Northing/Latitude). \nApenas colunas "
                              "contendo valores numéricos dentro do intervalo esperado para o SRC aparecerão aqui.")
        self.y_cbx.currentTextChanged.connect(self.yx_column_changed)

        self.x_icn = QtWidgets.QLabel()
        self.x_icn.setPixmap(QtGui.QPixmap("icons/lon.png").scaled(
            22, 22, transformMode=QtCore.Qt.TransformationMode.SmoothTransformation)
        )
        self.x_lbl = QtWidgets.QLabel("Longitude/Easting")
        self.x_cbx = QtWidgets.QComboBox()
        self.x_cbx.setToolTip("A coluna da tabela que contém a coordenada X (Easting/Longitude). \nApenas colunas "
                              "contendo valores numéricos dentro do intervalo esperado para o SRC aparecerão aqui.")
        self.x_cbx.currentTextChanged.connect(self.yx_column_changed)

        self.cancel_btn = QtWidgets.QToolButton()
        self.cancel_btn.setIcon(QtGui.QIcon("icons/cancel.png"))
        self.cancel_btn.setToolTip("Descartar alterações e fechar")
        self.cancel_btn.setStyleSheet("qproperty-iconSize: 22px 22px;")
        self.cancel_btn.setMinimumSize(30, 30)
        self.cancel_btn.setMaximumSize(30, 30)
        self.cancel_btn.clicked.connect(self.close)

        self.ok_btn = QtWidgets.QToolButton()
        self.ok_btn.setIcon(QtGui.QIcon("icons/ok.png"))
        self.ok_btn.setToolTip("Salvar e fechar")
        self.ok_btn.setStyleSheet("qproperty-iconSize: 22px 22px;")
        self.ok_btn.setMinimumSize(30, 30)
        self.ok_btn.setMaximumSize(30, 30)
        self.ok_btn.clicked.connect(self.ok_btn_clicked)

        layout.addWidget(self.crs_lbl, 0, 0, 1, 11)
        layout.addWidget(self.crs_cbx, 1, 0, 1, 11)
        layout.addWidget(self.coord_fields_lbl, 2, 0, 1, 11)
        layout.addWidget(self.y_icn, 3, 0, 1, 1)
        layout.addWidget(self.y_lbl, 3, 1, 1, 4)
        layout.addWidget(self.y_cbx, 3, 4, 1, 7)
        layout.addWidget(self.x_icn, 4, 0, 1, 1)
        layout.addWidget(self.x_lbl, 4, 1, 1, 4)
        layout.addWidget(self.x_cbx, 4, 4, 1, 7)
        layout.addWidget(self.cancel_btn, 5, 9, 1, 1)
        layout.addWidget(self.ok_btn, 5, 10, 1, 1)

        widget = QtWidgets.QWidget(self)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.fill_crs_list()

        self.resize(425, 175)
        self.setMaximumSize(650, 175)

    def fill_crs_list(self):
        crs_list = self.controller.get_crs_list()
        self.crs_cbx.clear()
        self.crs_cbx.addItems(crs_list)

        crs = self.controller.get_model_attribute("crs")
        if crs is not None:
            self.crs_cbx.setCurrentText(crs)
        else:
            self.crs_cbx.setCurrentText("SIRGAS 2000 (EPSG:4674)")

    def crs_changed(self):
        crs = crs_dict[self.crs_cbx.currentText()]
        tooltip = (f"{crs['name']}\n"
                   f"{crs['type']}\n"
                   f"{crs['area_of_use']}")
        self.crs_cbx.setToolTip(tooltip)
        self.fill_column_boxes()

    def fill_column_boxes(self):
        try:
            crs_key = self.crs_cbx.currentText()
            y_columns, x_columns = self.controller.get_coordinate_columns(crs_key)
            self.y_cbx.clear()
            self.y_cbx.addItems(y_columns)
            self.x_cbx.clear()
            self.x_cbx.addItems(x_columns)

            crs = self.controller.get_model_attribute("crs")
            y_column = self.controller.get_model_attribute("y_column")
            x_column = self.controller.get_model_attribute("x_column")

            if (crs == crs_key and y_column in y_columns and x_column in x_columns
                    and y_column is not None and x_column is not None):
                self.y_cbx.setCurrentText(y_column)
                self.x_cbx.setCurrentText(x_column)
            else:
                y_col = self.controller.select_coord_column("y", y_columns)
                x_col = self.controller.select_coord_column("x", x_columns)
                if y_col:
                    self.y_cbx.setCurrentText(y_col)
                if x_col:
                    self.x_cbx.setCurrentText(x_col)
        except Exception as exception:
            show_popup(f"Não foi possível encontrar a lista de colunas de coordenadas.\n\nMotivo: {exception}", "error")

    def yx_column_changed(self):
        if self.y_cbx.currentText() == "" or self.x_cbx.currentText() == "":
            self.ok_btn.setEnabled(False)
        else:
            self.ok_btn.setEnabled(True)

    def ok_btn_clicked(self):
        try:
            crs_key = self.crs_cbx.currentText()
            y = self.y_cbx.currentText()
            x = self.x_cbx.currentText()

            self.controller.set_model_attribute("crs", crs_key)
            self.controller.set_model_attribute("y_column", y)
            self.controller.set_model_attribute("x_column", x)

            self.parent.reproject_btn.setEnabled(True)
            self.parent.save_layer_btn.setEnabled(True)

            self.close()
        except Exception as exception:
            show_popup(f"Não foi possível configurar o SRC.\n\nMotivo: {exception}", "error")


class ReprojectWindow(QtWidgets.QMainWindow):
    def __init__(self, parent: AppMainWindow, controller):
        super(ReprojectWindow, self).__init__(parent)

        self.parent = parent
        self.controller = controller

        self.setWindowTitle('Reprojetar coordenadas')
        self.setWindowIcon(QtGui.QIcon('icons/globe.png'))
        self.setMinimumWidth(400)

        layout = QtWidgets.QGridLayout()
        layout.setVerticalSpacing(6)
        layout.setHorizontalSpacing(3)

        self.input_crs_lbl = QtWidgets.QLabel("SRC de entrada:")

        self.input_crs_edt = QtWidgets.QLineEdit(self.controller.get_model_attribute("crs"))
        self.input_crs_edt.setEnabled(False)
        self.input_crs_edt.setMinimumHeight(25)
        self.input_crs_edt.setMaximumHeight(25)

        self.output_crs_lbl = QtWidgets.QLabel("SRC de saída:")

        self.output_crs_cbx = QtWidgets.QComboBox()
        self.output_crs_cbx.setMinimumHeight(23)
        self.output_crs_cbx.setMaximumHeight(23)
        self.output_crs_cbx.currentTextChanged.connect(self.output_crs_changed)

        self.cancel_btn = QtWidgets.QToolButton()
        self.cancel_btn.setIcon(QtGui.QIcon("icons/cancel.png"))
        self.cancel_btn.setToolTip("Descartar alterações e fechar")
        self.cancel_btn.setStyleSheet("qproperty-iconSize: 22px 22px;")
        self.cancel_btn.setMinimumSize(30, 30)
        self.cancel_btn.setMaximumSize(30, 30)
        self.cancel_btn.clicked.connect(self.close)

        self.ok_btn = QtWidgets.QToolButton()
        self.ok_btn.setIcon(QtGui.QIcon("icons/ok.png"))
        self.ok_btn.setToolTip("Salvar e fechar")
        self.ok_btn.setStyleSheet("qproperty-iconSize: 22px 22px;")
        self.ok_btn.setMinimumSize(30, 30)
        self.ok_btn.setMaximumSize(30, 30)
        self.ok_btn.clicked.connect(self.ok_btn_clicked)

        layout.addWidget(self.input_crs_lbl, 0, 0, 1, 10)
        layout.addWidget(self.input_crs_edt, 1, 0, 1, 10)
        layout.addWidget(self.output_crs_lbl, 2, 0, 1, 10)
        layout.addWidget(self.output_crs_cbx, 3, 0, 1, 10)
        layout.addWidget(self.cancel_btn, 4, 8, 1, 1)
        layout.addWidget(self.ok_btn, 4, 9, 1, 1)

        widget = QtWidgets.QWidget(self)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.fill_crs_list()

    def fill_crs_list(self):
        crs_list = self.controller.get_crs_list()
        self.output_crs_cbx.clear()
        self.output_crs_cbx.addItems(crs_list)
        self.output_crs_cbx.setCurrentText("SIRGAS 2000 (EPSG:4674)")

    def output_crs_changed(self):
        input_crs = self.input_crs_edt.text()
        output_crs = self.output_crs_cbx.currentText()
        self.ok_btn.setEnabled(False if output_crs == input_crs else True)

    def ok_btn_clicked(self):
        try:
            output_crs = self.output_crs_cbx.currentText()
            self.controller.reproject(output_crs)
            show_popup("Coordenadas reprojetadas com sucesso!")
            self.parent.update_list()
            self.close()

        except Exception as exception:
            show_popup(f"Não foi possível reprojetar.\n\nMotivo: {exception}", "error")


class MapWindow(QtWidgets.QMainWindow):
    def __init__(self, parent, gdf):
        super(MapWindow, self).__init__(parent)

        self.gdf = gdf

        self.setWindowTitle("Mapa")
        self.setWindowIcon(QtGui.QIcon('icons/globe.png'))

        m = self.build_webmap()

        data = BytesIO()
        m.save(data, close_file=False)

        map_wev = QtWebEngineWidgets.QWebEngineView(self)
        map_wev.setHtml(data.getvalue().decode())
        map_wev.setGeometry(0, 0, 700, 500)

        self.setMinimumWidth(700)
        self.setMaximumWidth(700)
        self.setMinimumHeight(500)
        self.setMaximumHeight(500)

    def build_webmap(self):
        gdf = self.gdf.to_crs(4326)

        columns = gdf.columns.to_list()
        dtypes = gdf.dtypes.to_list()

        for column, dtype in zip(columns, dtypes):
            ok_types = ["object", "float64", "int64", "bool", "geometry"]
            if dtype not in ok_types:
                gdf[column] = gdf[column].astype(str, errors='ignore')

        yx = [gdf.geometry.y[0], gdf.geometry.x[0]]

        webmap = folium.Map(location=yx, zoom_start=12, minZoom=5, control_scale=True, zoomControl=True,
                            tiles='openstreetmap', attributionControl=True)

        folium.raster_layers.WmsTileLayer(
            'https://www.google.cn/maps/vt?lyrs=s@189&gl=cn&x={x}&y={y}&z={z}',
            'Google Satellite',
            name='Google Satellite',
            overlay=False
        ).add_to(webmap)

        folium.GeoJson(
            gdf.to_json(),
            name='Pontos',
            show=True,
            tooltip=folium.features.GeoJsonTooltip(
                fields=[columns[0]],
                labels=False
            )
        ).add_to(webmap)

        folium.map.LayerControl().add_to(webmap)

        MeasureControl(
            position='topright',
            primary_length_unit='meters',
            secondary_length_unit='kilometers',
            primary_area_unit='sqmeters',
            secondary_area_unit='hectares'
        ).add_to(webmap)

        Geocoder(position='topright', collapsed=True).add_to(webmap)

        MousePosition(position='bottomright', separator=' / ').add_to(webmap)

        return webmap


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


def show_file_dialog(caption: str, extension_filter: str, mode: str = "open", parent: QtWidgets.QMainWindow = None) -> str:
    """
    Exibe um diálogo de abertura/salvamento de arquivo.
    :param caption: Título do diálogo.
    :param extension_filter: Filtro de extensões de arquivo.
    :param mode: "open" ou "save".
    :param parent: Janela pai.
    :return: Caminho completo do arquivo (str).
    """
    if mode == "open":
        file_name, file_type = QtWidgets.QFileDialog.getOpenFileName(parent, caption=caption, filter=extension_filter)
    else:
        file_name, file_type = QtWidgets.QFileDialog.getSaveFileName(parent, caption=caption, filter=extension_filter)

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
    choice, ok = QtWidgets.QInputDialog.getItem(parent, title, message, items, selected, editable=False)

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


def show_wait_cursor(activate: bool = True):
    """
    Substitui o cursor padrão pelo cursor de ocupado.
    :param activate: True para mostrar o cursor de espera e False para restaurar o cursor normal.
    :return: Nada.
    """
    if activate:
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
    else:
        QtWidgets.QApplication.restoreOverrideCursor()
