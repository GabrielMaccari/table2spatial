# -*- coding: utf-8 -*-
"""
@author: Gabriel Maccari
"""
from PyQt6 import QtCore
from icecream import ic

from model import DataHandler, CRS_DICT, DATETIME_FORMATS, get_dtype_key
from view import MainWindow, ListRow
from dialogs import *


class UIController:
    def __init__(self):
        self.model = DataHandler()
        self.view = MainWindow()

        self.column_list_widgets = []
        self.dtypes_list = []

        self.view.show()

        self.view.import_button.clicked.connect(self.import_button_clicked)
        self.view.merge_button.clicked.connect(self.merge_button_clicked)
        self.view.reproject_button.clicked.connect(self.reproject_button_clicked)
        self.view.export_button.clicked.connect(self.export_button_clicked)
        #self.view.map_button.clicked.connect(self.map_button_clicked)

        self.view.import_ok_btn.clicked.connect(self.import_ok_button_clicked)

    # AÇÕES DA JANELA PRINCIPAL
    def import_button_clicked(self):
        try:
            path = show_file_dialog(
                caption="Selecione uma tabela contendo os dados de entrada.",
                extension_filter=("Formatos suportados (*.xlsx *.xlsm *.csv *.ods);;"
                                  "Pasta de Trabalho do Excel (*.xlsx);;"
                                  "Pasta de Trabalho Habilitada para Macro do Excel (*.xlsm);;"
                                  "Comma Separated Values (*.csv);; "
                                  "OpenDocument Spreadsheet (*.ods)"),
                mode="open", parent=self.view
            )

            if path == "":
                return

            toggle_wait_cursor(True)

            sheets = None

            if path.endswith(".csv"):
                self.model.read_csv_file(path)
                self.model.excel_file = None
                self.view.sheet_cbx.setEnabled(False)
            else:
                self.model.read_excel_file(path)
                sheets = self.model.excel_file.sheet_names

            self.setup_import_screen(sheet_selection=False if path.endswith(".csv") else True,
                                     sheets=sheets)
            self.view.switch_stack(1)
            toggle_wait_cursor(False)

        except Exception as error:
            toggle_wait_cursor(False)
            ic(error)
            show_popup(f"Ops! Ocorreu um erro ao abrir o arquivo.", "error",
                       f"Descrição do erro: {error}\n\nContexto: import_button_clicked()")

    def setup_import_screen(self, sheet_selection: bool = True, sheets: list | None = None):
        # Desconecta os componentes para poder atualizar sem dar trigger nas funções
        self.view.sheet_cbx.disconnect()
        self.view.crs_cbx.disconnect()
        self.view.x_cbx.disconnect()
        self.view.y_cbx.disconnect()

        self.view.sheet_cbx.setEnabled(sheet_selection)

        # Caso seja um tipo de arquivo que suporta múltiplas planilhas/abas (xlsx, xlsm, ods) (i.e. não é um csv)
        if sheet_selection:
            self.view.sheet_cbx.clear()
            self.view.sheet_cbx.addItems(sheets)
            self.model.read_excel_sheet(0)

        try:  # Eu não lembro por que esse try está aqui ou se ele é necessário, mas está funcionando
            self.view.crs_cbx.clear()
            self.view.crs_cbx.addItems(sorted(CRS_DICT))
            self.view.crs_cbx.setCurrentText("SIRGAS 2000 (EPSG:4674)")
        except Exception as error:
            ic(error)

        self.fill_xy_combos()

        self.view.sheet_cbx.currentTextChanged.connect(self.sheet_selected)
        self.view.crs_cbx.currentTextChanged.connect(self.crs_selected)
        self.view.x_cbx.currentTextChanged.connect(self.check_if_selected_xy_is_valid)
        self.view.y_cbx.currentTextChanged.connect(self.check_if_selected_xy_is_valid)

        self.check_if_selected_xy_is_valid()

    def fill_xy_combos(self):
        self.view.x_cbx.clear()
        self.view.y_cbx.clear()
        self.view.x_cbx.addItems(self.model.gdf.columns)
        self.view.y_cbx.addItems(self.model.gdf.columns)
        self.auto_select_xy_columns()

    def auto_select_xy_columns(self):
        crs_key = self.view.crs_cbx.currentText()
        crs_type = str(CRS_DICT[crs_key]["type"])
        x = self.model.search_coordinates_column_by_name("x", crs_type, self.model.gdf.columns)
        self.view.x_cbx.setCurrentText(x)
        y = self.model.search_coordinates_column_by_name("y", crs_type, self.model.gdf.columns)
        self.view.y_cbx.setCurrentText(y)

    def check_if_selected_xy_is_valid(self):
        crs_key = self.view.crs_cbx.currentText()
        valid_x_cols, valid_y_cols = self.model.filter_coordinates_columns(crs_key)

        selected_x = self.view.x_cbx.currentText()
        selected_y = self.view.y_cbx.currentText()

        x_ok = True if selected_x in valid_x_cols else False
        y_ok = True if selected_y in valid_y_cols else False

        self.view.x_ok_icon.setIcon(QtGui.QIcon("icons/ok.png" if x_ok else "icons/not_ok.png"))
        self.view.y_ok_icon.setIcon(QtGui.QIcon("icons/ok.png" if y_ok else "icons/not_ok.png"))

        self.view.import_ok_btn.setEnabled(True if x_ok and y_ok else False)

    def sheet_selected(self):
        try:
            toggle_wait_cursor(True)
            sheet = self.view.sheet_cbx.currentText()
            self.model.read_excel_sheet(sheet)
            self.fill_xy_combos()
            self.check_if_selected_xy_is_valid()
        except Exception as error:
            toggle_wait_cursor(False)
            ic(error)
            show_popup(f"Ops! Ocorreu um erro no funcionamento do aplicativo.", "error",
                       f"Descrição do erro: {error}\n\nContexto: sheet_selected()")

    def crs_selected(self):
        try:
            toggle_wait_cursor(True)
            self.auto_select_xy_columns()
            self.check_if_selected_xy_is_valid()
            toggle_wait_cursor(False)
        except Exception as error:
            toggle_wait_cursor(False)
            ic(error)
            show_popup(f"Ops! Ocorreu um erro no funcionamento do aplicativo.", "error",
                       f"Descrição do erro: {error}\n\nContexto: crs_selected()")

    def import_ok_button_clicked(self):
        try:
            toggle_wait_cursor(True)

            crs_key = self.view.crs_cbx.currentText()
            x_column = self.view.x_cbx.currentText()
            y_column = self.view.y_cbx.currentText()
            self.model.set_geodataframe_geometry(crs_key, x_column, y_column)
            self.update_column_list()
            self.view.switch_stack(0)

            self.view.merge_button.setEnabled(
                True if self.model.excel_file and len(self.model.excel_file.sheet_names) > 1 else False)
            self.view.reproject_button.setEnabled(True)
            #self.view.map_button.setEnabled(True)
            self.view.export_button.setEnabled(True)

            toggle_wait_cursor(False)
        except Exception as error:
            toggle_wait_cursor(False)
            ic(error)
            show_popup(f"Ops! Ocorreu um erro no funcionamento do aplicativo.", "error",
                       f"Descrição do erro: {error}\n\nContexto: import_ok_button_clicked()")

    def update_column_list(self, current_row: int = -1):
        try:
            toggle_wait_cursor(True)

            self.view.columns_list.clear()
            columns = self.model.gdf.columns.to_list()
            dtypes = self.model.gdf.dtypes.to_list()

            row = 0
            self.column_list_widgets = []
            self.dtypes_list = []

            for column_name, column_type in zip(columns, dtypes):
                widget = ListRow(column_name, str(column_type))
                widget.dtype_cbx.currentTextChanged.connect(lambda dtype_change, x=row: self.column_dtype_changed(x))

                try:
                    widget.rename_action.triggered.connect(self.rename_column_action_triggered)
                    widget.delete_action.triggered.connect(self.delete_column_action_triggered)
                except AttributeError:
                    pass

                if str(column_type) == "geometry":
                    widget.setEnabled(False)

                self.column_list_widgets.append(widget)
                self.dtypes_list.append(get_dtype_key(str(column_type)))

                item = QtWidgets.QListWidgetItem()
                item.setIcon(widget.get_icon())
                item.setSizeHint(QtCore.QSize(410, 30))

                self.view.columns_list.addItem(item)
                self.view.columns_list.setItemWidget(item, widget)
                row += 1

            self.view.columns_list.setCurrentRow(current_row)
            toggle_wait_cursor(False)
        except Exception as error:
            toggle_wait_cursor(False)
            ic(error)
            show_popup(f"Ops! Ocorreu um erro ao atualizar a lista de colunas.", "error",
                       f"Descrição do erro: {error}\n\nContexto: update_column_list()")

    def column_dtype_changed(self, row: int):
        try:
            toggle_wait_cursor(True)

            widget = self.column_list_widgets[row]
            column = widget.column_lbl.text()
            target_dtype = widget.dtype_cbx.currentText()

            true_key, false_key, ok_clicked = None, None, True

            if target_dtype == "Boolean":
                toggle_wait_cursor(False)
                true_key, ok_clicked = show_input_dialog("Insira o valor a ser considerado como Verdadeiro:",
                                                         default_text="Sim", parent=self.view)
                if ok_clicked:
                    false_key, ok_clicked = show_input_dialog("Insira o valor a ser considerado como Falso:",
                                                              default_text="Não", parent=self.view)
                toggle_wait_cursor(True)
                if ok_clicked:
                    self.model.change_column_dtype(column, target_dtype, true_key=true_key, false_key=false_key)

            elif target_dtype == "Datetime":
                toggle_wait_cursor(False)
                datetime_format, ok_clicked = show_selection_dialog(
                    "Selecione o formato de data e hora presente no campo:",
                    items=DATETIME_FORMATS.keys(), parent=self.view)
                if ok_clicked:
                    self.model.change_column_dtype(column, target_dtype, datetime_format=datetime_format)
                toggle_wait_cursor(True)

            else:
                self.model.change_column_dtype(column, target_dtype)

            self.dtypes_list[row] = target_dtype
            self.update_column_list(row)
            toggle_wait_cursor(False)
        except Exception as error:
            self.update_column_list(row)
            toggle_wait_cursor(False)
            ic(error)
            show_popup(f"Ops! Não foi possível converter o tipo de dado da coluna.", "error",
                       f"Descrição do erro: {error}\n\nContexto: column_dtype_changed()")

    def merge_button_clicked(self):
        try:
            self.view.switch_stack(2)
            self.view.merge_column_cbx.clear()
            self.view.merge_column_cbx.addItems(self.model.gdf.columns)

            self.view.merge_ok_btn.clicked.connect(self.merge_ok_btn_clicked)

        except Exception as error:
            ic(error)
            show_popup(f"Ops! Ocorreu um erro no funcionamento do aplicativo.", "error",
                       f"Descrição do erro: {error}\n\nContexto: merge_button_clicked()")

    def merge_ok_btn_clicked(self):
        try:
            self.view.merge_ok_btn.disconnect()  # Por algum motivo estava dando trigger mais de uma vez nessa função
            merge_column = self.view.merge_column_cbx.currentText()
            merged_sheets, skipped_sheets = self.model.merge_sheets(merge_column)
            show_popup(f"As seguintes planilhas foram mescladas com sucesso usando a coluna {merge_column}: "
                       f"{", ".join(merged_sheets)}.\nAs demais planilhas do arquivo foram ignoradas pois não contêm a "
                       f"coluna de mescla em questão.")
            self.update_column_list()
            self.view.switch_stack(0)
        except Exception as error:
            ic(error)
            show_popup(f"Ops! Não foi possível mesclar as planilhas.", "error",
                       f"Descrição do erro: {error}\n\nContexto: merge_ok_button_clicked()")

    def reproject_button_clicked(self):
        try:
            current_crs = self.model.gdf.crs.name
            target_crs, ok_clicked = show_selection_dialog(message=f"SRC atual: {current_crs}\n\nSelecione o SRC de destino:", items=sorted(CRS_DICT),
                                                    title="Reprojetar pontos", parent=self.view)
            if not ok_clicked:
                return

            self.model.reproject_geodataframe(target_crs)
            show_popup("Pontos reprojetados com sucesso!\n\n"
                       "Obs: As coordenadas contidas na tabela não foram alteradas.")
        except Exception as error:
            ic(error)
            show_popup(f"Ops! Não foi possível reprojetar os pontos.", "error",
                       f"Descrição do erro: {error}\n\nContexto: reproject_button_clicked()")

    def export_button_clicked(self):
        try:
            file_name = show_file_dialog(
                caption="Salvar arquivo vetorial", mode="save", parent=self.view,
                extension_filter="Formatos suportados (*.gpkg *.geojson *.shp);;"
                                 "Geopackage (*.gpkg);;"
                                 "GeoJSON (*.geojson);;"
                                 "Shapefile (*.shp)"
            )

            if file_name == "":
                return

            layer_name = "pontos"
            if file_name.endswith(".gpkg"):
                layer_name, ok_clicked = show_input_dialog("Insira um nome para a camada:", "Nome da camada",
                                                           layer_name, self.view)
                if not ok_clicked:
                    return

            self.model.save_to_geospatial_file(file_name, layer_name)
            show_popup("Pontos exportados com sucesso!")

        except Exception as error:
            ic(error)
            show_popup(f"Ops! Não foi possível exportar.", "error",
                       f"Descrição do erro: {error}\n\nContexto: import_button_clicked()")

    def rename_column_action_triggered(self):
        try:
            row = self.view.columns_list.currentRow()
            column = self.column_list_widgets[row].field

            new_name, ok_clicked = show_input_dialog("Insira um novo nome para a coluna:", "Renomear coluna", column, self.view)

            if not ok_clicked:
                return

            if new_name in self.model.gdf.columns:
                raise Exception("O nome inserido já é utilizado por outra coluna do GeoDataFrame.")

            self.model.gdf.rename(columns={column: new_name}, inplace=True)
            self.column_list_widgets[row].field = new_name
            self.update_column_list(row)

        except Exception as error:
            ic(error)
            show_popup(f"Ops! Não foi possível renomear a coluna.", "error",
                       f"Descrição do erro: {error}\n\nContexto: rename_column_action_triggered()")

    def delete_column_action_triggered(self):
        try:
            row = self.view.columns_list.currentRow()
            column = self.column_list_widgets[row].field

            yes_or_no = show_question_dialog(f"Excluir coluna \"{column}\"?")

            if yes_or_no != QtWidgets.QMessageBox.StandardButton.Yes.value:
                return

            self.model.gdf.drop(columns=[column], inplace=True)
            self.column_list_widgets.pop(row)
            self.update_column_list(row)

        except Exception as error:
            ic(error)
            show_popup(f"Ops! Não foi possível renomear a coluna.", "error",
                       f"Descrição do erro: {error}\n\nContexto: rename_column_action_triggered()")


def toggle_wait_cursor(activate: bool = True):
    """
    Substitui o cursor padrão pelo cursor de ocupado.
    :param activate: True para mostrar o cursor de espera e False para restaurar o cursor normal.
    :return: Nada.
    """
    if activate:
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
    else:
        QtWidgets.QApplication.restoreOverrideCursor()

