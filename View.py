from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWebEngineWidgets import QWebEngineView #pip install PyQt6-WebEngine
from folium.plugins import MeasureControl, MousePosition, Geocoder
from io import BytesIO
import folium

from Model import dtype_dict, crs_dict


class ListRow(QWidget):

    def __init__(self, column_name, column_dtype):

        super().__init__()

        self.field = column_name
        self.dtype = column_dtype

        self.column_lbl = QLabel(self)
        self.column_lbl.setText(self.field)
        self.column_lbl.setGeometry(5, 0, 260, 30)

        self.dtype_cbx = QComboBox(self)
        self.dtype_cbx.setGeometry(273, 4, 90, 22)

        self.dtype_cbx.addItems(dtype_dict.keys())
        key = self.get_dtype_key()
        self.dtype_cbx.setCurrentText(key)

    def get_icon(self):
        dt_values = dtype_dict.values()
        img = next(subdict["icon"] for subdict in dt_values
                   if subdict["pandas_type"] == self.dtype)
        return QIcon(img)

    def get_dtype_key(self):
        dt_items = dtype_dict.items()
        key = next(key for key, subdict in dt_items
                   if subdict["pandas_type"] == self.dtype)
        return key


class AppMainWindow(QMainWindow):

    def __init__(self, model, controller):

        super().__init__()

        self.model = model
        self.controller = controller

        self.file_open = False

        self.icon_dict = {

        }

        self.setWindowTitle('table2spatial')
        self.setWindowIcon(QIcon('icons/globe.png'))
        self.setMaximumSize(425, 560)

        layout = QGridLayout()
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop |
                            Qt.AlignmentFlag.AlignLeft)

        self.open_file_btn = QToolButton(self)
        self.open_file_btn.setToolTip("Importar tabela de pontos")
        self.open_file_btn.setIcon(QIcon("icons/excel.png"))
        self.open_file_btn.setMinimumSize(40, 40)
        self.open_file_btn.setMaximumSize(40, 40)
        self.open_file_btn.clicked.connect(self.open_file_btn_clicked)

        self.merge_btn = QToolButton(self)
        self.merge_btn.setToolTip("Mesclar abas do arquivo usando um campo "
                                  "em comum")
        self.merge_btn.setIcon(QIcon("icons/merge.png"))
        self.merge_btn.setMinimumSize(40, 40)
        self.merge_btn.setMaximumSize(40, 40)
        self.merge_btn.clicked.connect(self.merge_btn_clicked)
        self.merge_btn.setEnabled(False)

        self.save_table_btn = QToolButton(self)
        self.save_table_btn.setToolTip("Exportar como CSV")
        self.save_table_btn.setIcon(QIcon("icons/export.png"))
        self.save_table_btn.setMinimumSize(40, 40)
        self.save_table_btn.setMaximumSize(40, 40)
        self.save_table_btn.clicked.connect(self.save_table_btn_clicked)
        self.save_table_btn.setEnabled(False)

        self.crs_settings_btn = QToolButton(self)
        self.crs_settings_btn.setToolTip("Configurar SRC e campos de "
                                         "coordenadas")
        self.crs_settings_btn.setIcon(QIcon("icons/settings.png"))
        self.crs_settings_btn.setMinimumSize(40, 40)
        self.crs_settings_btn.setMaximumSize(40, 40)
        self.crs_settings_btn.clicked.connect(self.crs_settings_btn_clicked)
        self.crs_settings_btn.setEnabled(False)

        self.export_btn = QToolButton(self)
        self.export_btn.setToolTip("Exportar como arquivo vetorial de pontos")
        self.export_btn.setIcon(QIcon("icons/points.png"))
        self.export_btn.setMinimumSize(40, 40)
        self.export_btn.setMaximumSize(40, 40)
        self.export_btn.clicked.connect(self.export_btn_clicked)
        self.export_btn.setEnabled(False)

        self.map_preview_btn = QToolButton(self)
        self.map_preview_btn.setToolTip("Visualizar uma prévia dos dados em "
                                        "mapa\n(apenas para dataframes com até "
                                        "100 pontos)")
        self.map_preview_btn.setIcon(QIcon("icons/map.png"))
        self.map_preview_btn.setMinimumSize(40, 40)
        self.map_preview_btn.setMaximumSize(40, 40)
        self.map_preview_btn.clicked.connect(self.map_preview_btn_clicked)
        self.map_preview_btn.setEnabled(False)

        self.df_columns_lsw = QListWidget(self)
        self.df_columns_lsw.setMinimumSize(410, 480)
        self.df_columns_lsw.setMaximumSize(410, 480)
        self.df_columns_lsw.setIconSize(QSize(22, 22))
        self.df_columns_lsw.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        copyright_lbl = QLabel("©2023 Gabriel Maccari / "
                               "Icons by www.icons8.com")

        layout.addWidget(self.open_file_btn, 0, 0, 1, 1)
        layout.addWidget(self.merge_btn, 0, 1, 1, 1)
        layout.addWidget(self.save_table_btn, 0, 2, 1, 1)
        layout.addWidget(self.crs_settings_btn, 0, 3, 1, 1)
        layout.addWidget(self.export_btn, 0, 4, 1, 1)
        layout.addWidget(self.map_preview_btn, 0, 5, 1, 1)
        layout.addWidget(self.df_columns_lsw, 1, 0, 20, 8)
        layout.addWidget(copyright_lbl, 22, 0, 1, 8)

        widget = QWidget(self)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def open_file_btn_clicked(self):
        try:
            new_file_opened = self.controller.open_file()
            if new_file_opened:
                self.update_list()
                self.file_open = True
            self.merge_btn.setEnabled(self.model.multiple_sheets)
            self.save_table_btn.setEnabled(self.file_open)
            self.crs_settings_btn.setEnabled(self.file_open)
        except Exception as exception:
            message = (f"Não foi possível abrir o arquivo.\n\n"
                       f"Motivo: {exception}")
            show_popup(message, "error")

    def update_list(self):
        try:
            # Limpa o conteúdo atual da lista
            self.df_columns_lsw.clear()
            #
            columns = self.model.df.columns
            dtypes = self.model.df.dtypes
            #
            row = 0
            self.column_list_widgets = []
            self.dtypes_list = []
            #
            for column_name, column_type in zip(columns, dtypes):
                #
                widget = ListRow(column_name, str(column_type))
                #
                widget.dtype_cbx.currentTextChanged.connect(
                    lambda dtype_change, x=row:
                    self.column_dtype_changed(x)
                )
                #
                self.column_list_widgets.append(widget)
                self.dtypes_list.append(str(column_type))
                #
                item = QListWidgetItem()
                item.setIcon(widget.get_icon())
                item.setSizeHint(QSize(410, 30))
                self.df_columns_lsw.addItem(item)
                self.df_columns_lsw.setItemWidget(item, widget)
                row += 1
        except Exception as exception:
            message = (f"Não foi possível atualizar a lista com os dados do "
                       f"arquivo.\n\nMotivo: {exception}")
            show_popup(message, "error")

    def merge_btn_clicked(self):
        try:
            self.controller.merge_sheets()
            self.update_list()
        except Exception as exception:
            message = (f"Não foi possível mesclar as abas do arquivo."
                       f"\n\nMotivo: {exception}")
            show_popup(message, "error")

    def column_dtype_changed(self, row):
        switched = False
        target_dtype = "object"

        try:
            # Seleciona o widget da linha
            widget = self.column_list_widgets[row]
            # Obtém o nome da coluna
            field = widget.column_lbl.text()
            # Obtém o tipo de dado atual da coluna
            current_dtype = self.dtypes_list[row]
            current_dtype_key = next(key for key, subdict in dtype_dict.items()
                                     if subdict["pandas_type"] == current_dtype)
            # Obtém o tipo de dado para o qual o usuário deseja converter
            target_dtype_key = widget.dtype_cbx.currentText()
            target_dtype = dtype_dict[target_dtype_key]["pandas_type"]
            # Tenta realizar a conversão
            switched = self.controller.switch_dtype(field, target_dtype)

        # Exibe uma popup em caso de erro
        except Exception as exception:
            message = (f"Não foi possível converter.\n\nMotivo: {exception}")
            show_popup(message, "error")

        if switched:
            self.dtypes_list[row] = target_dtype
        self.update_list()

    def save_table_btn_clicked(self):
        try:
            self.controller.save_csv()
        except Exception as exception:
            message = (f"Não foi possível salvar o arquivo CSV."
                       f"\n\nMotivo: {exception}")
            show_popup(message, "error")

    def crs_settings_btn_clicked(self):
        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            crs_window = CRSSettingsWindow(self, self.model, self.controller)
            crs_window.show()
        except Exception as exception:
            message = (f"Não foi possível abrir a janela de configuração do SRC"
                       f"\n\nMotivo: {exception}")
            show_popup(message, "error")
        QApplication.restoreOverrideCursor()

    def export_btn_clicked(self):
        try:
            self.controller.build_gdf()
            saved = self.controller.save_points()
            if saved:
                show_popup("Exportado com sucesso!")
                if len(self.model.df) <= 100:
                    self.map_preview_btn.setEnabled(True)
                else:
                    self.map_preview_btn.setEnabled(False)
        except Exception as exception:
            message = (f"Não foi possível exportar o arquivo de pontos."
                       f"\n\nMotivo: {exception}")
            show_popup(message, "error")

    def map_preview_btn_clicked(self):
        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            map_window = MapWindow(self, self.model.gdf)
            map_window.show()
        except Exception as exception:
            message = (f"Não foi possível gerar o mapa."
                       f"\n\nMotivo: {exception}")
            show_popup(message, "error")
        QApplication.restoreOverrideCursor()


class CRSSettingsWindow(QMainWindow):

    def __init__(self, parent, model, controller):
        super(CRSSettingsWindow, self).__init__(parent)
        self.parent = parent
        self.model = model
        self.controller = controller

        self.setWindowTitle('Configurações de SRC')
        self.setWindowIcon(QIcon('icons/globe.png'))
        self.setMinimumWidth(400)

        layout = QGridLayout()
        layout.setVerticalSpacing(6)
        layout.setHorizontalSpacing(3)

        self.crs_lbl = QLabel("SRC dos dados de entrada")
        self.crs_lbl.setStyleSheet("font-size: 11pt;")

        self.crs_cbx = QComboBox()
        self.crs_cbx.currentTextChanged.connect(self.crs_changed)

        self.coord_fields_lbl = QLabel("Campos de coordenadas")
        self.coord_fields_lbl.setStyleSheet("font-size: 11pt;")

        self.y_icn = QLabel()
        self.y_icn.setPixmap(QPixmap("icons/lat.png").scaled(
            22, 22, transformMode=Qt.TransformationMode.SmoothTransformation)
        )
        self.y_lbl = QLabel("Latitude/Northing")
        self.y_cbx = QComboBox()
        self.y_cbx.setToolTip("A coluna da tabela que contém a coordenada Y "
                              "(Northing/Latitude). \nApenas colunas contendo "
                              "valores numéricos dentro do intervalo esperado "
                              "para o SRC aparecerão aqui.")
        self.y_cbx.currentTextChanged.connect(self.yx_column_changed)

        self.x_icn = QLabel()
        self.x_icn.setPixmap(QPixmap("icons/lon.png").scaled(
            22, 22, transformMode=Qt.TransformationMode.SmoothTransformation)
        )
        self.x_lbl = QLabel("Longitude/Easting")
        self.x_cbx = QComboBox()
        self.x_cbx.setToolTip("A coluna da tabela que contém a coordenada X "
                              "(Easting/Longitude). \nApenas colunas contendo "
                              "valores numéricos dentro do intervalo esperado "
                              "para o SRC aparecerão aqui.")
        self.x_cbx.currentTextChanged.connect(self.yx_column_changed)

        self.cancel_btn = QToolButton()
        self.cancel_btn.setIcon(QIcon("icons/cancel.png"))
        self.cancel_btn.setToolTip("Descartar alterações e fechar")
        self.cancel_btn.setStyleSheet("qproperty-iconSize: 22px 22px;")
        self.cancel_btn.setMinimumSize(30, 30)
        self.cancel_btn.setMaximumSize(30, 30)
        self.cancel_btn.clicked.connect(self.close)

        self.ok_btn = QToolButton()
        self.ok_btn.setIcon(QIcon("icons/ok.png"))
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

        widget = QWidget(self)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.fill_crs_list()

        self.resize(425, 175)
        self.setMaximumSize(650, 175)

    def fill_crs_list(self):
        crs_list = self.controller.get_crs_list()
        self.crs_cbx.clear()
        self.crs_cbx.addItems(crs_list)
        """
        self.crs_cbx.setIconSize(QSize(20, 20))
        icon_list = self.controller.get_crs_icons(crs_list)
        for i, crs in enumerate(icon_list):
            self.crs_cbx.setItemIcon(i, icon)
        """
        if self.model.crs is not None:
            self.crs_cbx.setCurrentText(self.model.crs)
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
        crs_key = self.crs_cbx.currentText()
        y_columns, x_columns = self.controller.get_coordinate_columns(crs_key)
        self.y_cbx.clear()
        self.y_cbx.addItems(y_columns)
        self.x_cbx.clear()
        self.x_cbx.addItems(x_columns)
        if (self.model.crs == crs_key
                and self.model.y_column in y_columns
                and self.model.x_column in x_columns
                and self.model.y_column is not None
                and self.model.x_column is not None):
            self.y_cbx.setCurrentText(self.model.y_column)
            self.x_cbx.setCurrentText(self.model.x_column)

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

            self.model.crs = crs_key
            self.model.y_column = y
            self.model.x_column = x

            self.parent.export_btn.setEnabled(True)

            self.close()
        except Exception as exception:
            message = (f"Não foi possível configurar o sistema de referência de"
                       f" coordenadas.\n\nMotivo: {exception}")
            show_popup(message, "error")


class MapWindow(QMainWindow):
    def __init__(self, parent, gdf):

        super(MapWindow, self).__init__(parent)

        self.gdf = gdf

        self.setWindowTitle("Mapa")
        self.setWindowIcon(QIcon('icons/globe.png'))

        m = self.build_webmap()

        data = BytesIO()
        m.save(data, close_file=False)

        map_wev = QWebEngineView(self)
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

        webmap = folium.Map(location=yx, zoom_start=12, minZoom=5,
                            control_scale=True, zoomControl=True,
                            tiles='openstreetmap', attributionControl=True)

        folium.raster_layers.WmsTileLayer(
            'https://www.google.cn/maps/vt?lyrs=s@189&gl=cn&x={x}&y={y}&z={z}',
            'Google Satellite',
            name='Google Satellite',
            overlay=False
        ).add_to(webmap)

        f = columns[0:-1] if len(columns) <= 11 else columns[0:11]

        folium.GeoJson(
            gdf.to_json(),
            name='Pontos',
            show=True,
            tooltip=folium.features.GeoJsonTooltip(
                fields=[columns[0]],
                labels=False
            ),
            popup=folium.features.GeoJsonPopup(
                fields=f,
                aliases=f
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


def show_popup(message, msg_type="notification"):
    popup_types = {
        "notification": {"title": "Notificação", "icon": "icons/globe.png"},
        "error":        {"title": "Erro",        "icon": "icons/error.png"}
    }
    title = popup_types[msg_type]["title"]
    icon = QIcon(popup_types[msg_type]["icon"])

    popup = QMessageBox()
    popup.setText(message)
    popup.setWindowTitle(title)
    popup.setWindowIcon(icon)
    popup.exec()


def show_file_dialog(caption, extension_filter, mode="open"):
    if mode == "open":
        file_name, file_type = QFileDialog.getOpenFileName(
            caption=caption, filter=extension_filter
        )
    else:
        file_name, file_type = QFileDialog.getSaveFileName(
            caption=caption, filter=extension_filter
        )
    return file_name, file_type


def show_selection_dialog(message, options, title="Selecionar opções"):
    choice, ok = QInputDialog.getItem(None, title, message, options, editable=False)
    return choice, ok


def show_input_dialog(message, title="", text=""):
    user_input, ok = QInputDialog.getText(None, title, message, text=text)
    return user_input, ok