# -*- coding: utf-8 -*-
"""
@author: Gabriel Maccari
"""

import os
import pandas
from PyQt6 import QtCore, QtGui, QtWidgets
from icecream import ic

from model import DataHandler, CRS_DICT, DATETIME_FORMATS, get_dtype_key
from view import MainWindow, ListRow, ListWindow, center_window_on_point
from dialogs import show_popup, show_file_dialog, show_selection_dialog, show_input_dialog, show_question_dialog
from extensions.stereogram import StereogramWindow
from extensions.rose_chart import RoseChartWindow


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
        self.view.graph_button.clicked.connect(self.graph_button_clicked)

        self.view.import_ok_btn.clicked.connect(self.import_ok_button_clicked)

        # self.view.target_crs_cbx.currentTextChanged.connect(self.save_coords_checkbox_checked)
        self.view.save_coords_chk.checkStateChanged.connect(self.save_coords_checkbox_checked)
        self.view.x_column_name_edt.textChanged.connect(self.check_if_coords_columns_exist)
        self.view.y_column_name_edt.textChanged.connect(self.check_if_coords_columns_exist)
        self.view.z_column_name_edt.textChanged.connect(self.check_if_coords_columns_exist)
        self.view.reproject_ok_btn.clicked.connect(self.reproject_ok_button_clicked)

    # AÇÕES DA JANELA PRINCIPAL
    def import_button_clicked(self):
        try:
            path = show_file_dialog(
                caption="Selecione uma tabela contendo os dados de entrada.",
                extension_filter=("Formatos suportados (*.xlsx *.xlsm *.csv *.ods);;"
                                  "Pasta de Trabalho do Excel (*.xlsx);;"
                                  "Pasta de Trabalho Habilitada para Macro do Excel (*.xlsm);;"
                                  "Comma Separated Values (*.csv);;"
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
            else:
                self.model.read_excel_file(path)
                sheets = self.model.excel_file.sheet_names

            self.setup_import_screen(csv=True if path.endswith(".csv") else False, sheets=sheets)
            self.view.switch_stack(1)
            toggle_wait_cursor(False)

        except Exception as error:
            self.handle_exception(error, "import_button_clicked()", "Ops! Ocorreu um erro ao abrir o arquivo.")
            # Reconecta os componentes caso tenha dado erro na função model.process_data()
            if isinstance(error, IndexError):
                self.connect_import_screen_components(True)

    def setup_import_screen(self, csv: bool = False, sheets: list | None = None):
        # Desconecta os componentes para poder atualizar sem dar trigger nas funções
        try:
            self.connect_import_screen_components(False)
        except TypeError:
            pass

        self.view.sheet_cbx.clear()
        self.view.sheet_cbx.setEnabled(not csv)

        # Caso seja um tipo de arquivo que suporta múltiplas planilhas/abas (xlsx, xlsm, ods) (i.e. não é um csv)
        if not csv:
            self.view.sheet_cbx.addItems(sheets)
            self.model.read_excel_sheet(0)

        self.view.crs_cbx.clear()
        self.view.crs_cbx.addItems(sorted(CRS_DICT.keys()))
        self.view.crs_cbx.setCurrentText("SIRGAS 2000 (EPSG:4674)")

        self.view.dms_chk.setChecked(False)

        self.fill_xy_combos()

        self.view.z_cbx.setEnabled(False)
        self.view.z_ok_icon.setEnabled(False)

        # Reconecta os componentes
        self.connect_import_screen_components(True)

        self.check_if_selected_xyz_is_valid()

    def connect_import_screen_components(self, connect: bool):
        if connect:
            self.view.sheet_cbx.currentTextChanged.connect(self.sheet_selected)
            self.view.crs_cbx.currentTextChanged.connect(self.crs_selected)
            self.view.dms_chk.clicked.connect(self.check_if_selected_xyz_is_valid)
            self.view.x_cbx.currentTextChanged.connect(self.check_if_selected_xyz_is_valid)
            self.view.y_cbx.currentTextChanged.connect(self.check_if_selected_xyz_is_valid)
            self.view.z_cbx.currentTextChanged.connect(self.check_if_selected_xyz_is_valid)
        else:
            self.view.sheet_cbx.disconnect()
            self.view.crs_cbx.disconnect()
            self.view.dms_chk.disconnect()
            self.view.x_cbx.disconnect()
            self.view.y_cbx.disconnect()
            self.view.z_cbx.disconnect()

    def fill_xy_combos(self):
        self.view.x_cbx.clear()
        self.view.y_cbx.clear()
        self.view.z_cbx.clear()

        self.view.x_cbx.addItems(self.model.gdf.columns)
        self.view.y_cbx.addItems(self.model.gdf.columns)
        self.view.z_cbx.addItems(self.model.gdf.columns)

        self.auto_select_xy_columns()

    def auto_select_xy_columns(self):
        crs_key = self.view.crs_cbx.currentText()
        crs_type = CRS_DICT[crs_key]["type"]
        x = self.model.search_coordinates_column_by_name("x", crs_type, self.model.gdf.columns)
        self.view.x_cbx.setCurrentText(x)
        y = self.model.search_coordinates_column_by_name("y", crs_type, self.model.gdf.columns)
        self.view.y_cbx.setCurrentText(y)

        if crs_type == "Geographic 3D CRS":
            z = self.model.search_coordinates_column_by_name("z", crs_type, self.model.gdf.columns)
            self.view.z_cbx.setCurrentText(z)

    def check_if_selected_xyz_is_valid(self):
        crs_key = self.view.crs_cbx.currentText()
        crs_type = CRS_DICT[crs_key]["type"]
        dms_format = self.view.dms_chk.isChecked()
        valid_x_cols, valid_y_cols, valid_z_cols = self.model.filter_coordinates_columns(crs_key, dms_format)

        selected_x = self.view.x_cbx.currentText()
        selected_y = self.view.y_cbx.currentText()
        selected_z = self.view.z_cbx.currentText()

        x_ok = True if selected_x in valid_x_cols else False
        y_ok = True if selected_y in valid_y_cols else False
        z_ok = True if selected_z in valid_z_cols else False

        self.view.x_ok_icon.setIcon(QtGui.QIcon("icons/ok.png" if x_ok else "icons/not_ok.png"))
        self.view.y_ok_icon.setIcon(QtGui.QIcon("icons/ok.png" if y_ok else "icons/not_ok.png"))
        self.view.z_ok_icon.setIcon(QtGui.QIcon("icons/ok.png" if z_ok else "icons/not_ok.png"))

        if crs_type == "Geographic 3D CRS":
            self.view.import_ok_btn.setEnabled(True if x_ok and y_ok and z_ok else False)
        else:
            self.view.import_ok_btn.setEnabled(True if x_ok and y_ok else False)

    def sheet_selected(self):
        try:
            toggle_wait_cursor(True)
            sheet = self.view.sheet_cbx.currentText()
            self.model.read_excel_sheet(sheet)
            self.fill_xy_combos()
            self.check_if_selected_xyz_is_valid()
            toggle_wait_cursor(False)
        except Exception as error:
            self.handle_exception(error, "sheet_selected()")

    def crs_selected(self):
        try:
            toggle_wait_cursor(True)
            crs_key = self.view.crs_cbx.currentText()
            crs_type = CRS_DICT[crs_key]["type"]
            self.view.z_cbx.setEnabled(True if crs_type == "Geographic 3D CRS" else False)
            self.view.z_ok_icon.setEnabled(True if crs_type == "Geographic 3D CRS" else False)
            self.auto_select_xy_columns()
            self.check_if_selected_xyz_is_valid()
            toggle_wait_cursor(False)
        except Exception as error:
            self.handle_exception(error, "crs_selected()")

    def import_ok_button_clicked(self):
        try:
            toggle_wait_cursor(True)

            crs_key = self.view.crs_cbx.currentText()
            crs_type = CRS_DICT[crs_key]["type"]
            x_column = self.view.x_cbx.currentText()
            y_column = self.view.y_cbx.currentText()
            z_column = (self.view.z_cbx.currentText() if crs_type == "Geographic 3D CRS" else None)
            dms = self.view.dms_chk.isChecked()

            self.model.set_geodataframe_geometry(crs_key, x_column, y_column, z_column, dms)
            self.update_column_list()
            self.view.switch_stack(0)

            self.view.merge_button.setEnabled(True if self.model.excel_file and len(self.model.excel_file.sheet_names) > 1 else False)
            self.view.reproject_button.setEnabled(True)
            self.view.export_button.setEnabled(True)
            self.view.graph_button.setEnabled(True)

            crs_label = f"{self.model.gdf.crs.name} ({self.model.gdf.crs.type_name})"
            label = f"Pontos: {len(self.model.gdf.index)}    SRC: {crs_label}"
            self.view.bottom_label.setText(label if len(label) < 85 else f"Pontos: {len(self.model.gdf.index)}")

            toggle_wait_cursor(False)
        except Exception as error:
            self.handle_exception(error, "import_ok_button_clicked()")

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
                    widget.show_uniques_action.triggered.connect(self.show_uniques_action_triggered)
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
            self.handle_exception(error, "update_column_list()", "Ops! Ocorreu um erro ao atualizar a lista de colunas.")

    def column_dtype_changed(self, row: int):
        try:
            toggle_wait_cursor(True)

            widget = self.column_list_widgets[row]
            column = widget.column_lbl.text()
            target_dtype = widget.dtype_cbx.currentText()

            true_key, false_key, ok_clicked = None, None, True

            if target_dtype == "Boolean":
                uniques = sorted([str(value) for value in self.model.gdf[column].unique()])
                if "nan" in uniques:
                    uniques.remove("nan")
                uniques.append("<Células vazias>")
                uniques.append("<Nenhum>")
                toggle_wait_cursor(False)
                true_key, ok_clicked = show_selection_dialog(
                    message="Insira o valor a ser considerado como Verdadeiro:", items=uniques,
                    title="Conversão para booleano"
                )
                if ok_clicked:
                    if true_key not in uniques:
                        raise KeyError("O valor informado não existe na coluna.")
                    false_key, ok_clicked = show_selection_dialog(
                        message="Insira o valor a ser considerado como Falso:", items=uniques,
                        title="Conversão para booleano"
                    )
                toggle_wait_cursor(True)
                if ok_clicked:
                    if false_key not in uniques:
                        raise KeyError("O valor informado não existe na coluna.")
                    self.model.change_column_dtype(column, target_dtype, true_key=true_key, false_key=false_key)

            elif target_dtype == "Datetime":
                toggle_wait_cursor(False)
                datetime_format, ok_clicked = show_selection_dialog(
                    "Selecione o formato de data e hora presente no campo:",
                    items=DATETIME_FORMATS.keys(), allow_edit=False, parent=self.view)
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
            self.handle_exception(error, "column_dtype_changed()", "Ops! Não foi possível converter o tipo de dado da coluna.")

    def merge_button_clicked(self):
        try:
            merge_column, ok_clicked = show_selection_dialog(message="Selecione a coluna identificadora para a mescla:",
                                                             items=self.model.gdf.columns, title="Mesclar planilhas",
                                                             parent=self.view)
            if ok_clicked:
                merged_sheets, skipped_sheets = self.model.merge_sheets(merge_column)
                show_popup(f"As seguintes planilhas foram mescladas com sucesso usando a coluna {merge_column}: "
                           f"{', '.join(merged_sheets)}.\nAs demais planilhas do arquivo foram ignoradas pois não "
                           f"contêm a coluna de mescla em questão.", parent=self.view)
                self.update_column_list()

        except Exception as error:
            self.handle_exception(error, "merge_button_clicked()", "Ops! Não foi possível mesclar as planilhas.")

    def reproject_button_clicked(self):
        try:
            toggle_wait_cursor(True)

            self.view.switch_stack(2)

            self.view.source_crs_lbl.setText(f"SRC atual: {self.model.crs_key})")

            self.view.target_crs_cbx.addItems(sorted(CRS_DICT.keys()))
            self.view.target_crs_cbx.setCurrentText("SIRGAS 2000 (EPSG:4674)")

            self.view.save_coords_chk.setChecked(False)

            toggle_wait_cursor(False)
        except Exception as error:
            self.handle_exception(error, "reproject_button_clicked()", "Ops! Não foi possível reprojetar os pontos.")

    def save_coords_checkbox_checked(self):
        try:
            state = self.view.save_coords_chk.isChecked()
            crs_type = CRS_DICT[self.view.target_crs_cbx.currentText()]["type"]
            is_crs_3d = crs_type == "Geographic 3D CRS"

            self.view.x_column_name_edt.setEnabled(state)
            self.view.y_column_name_edt.setEnabled(state)
            self.view.z_column_name_edt.setEnabled(state and is_crs_3d)

            self.view.x_column_name_icn.setEnabled(state)
            self.view.y_column_name_icn.setEnabled(state)
            self.view.z_column_name_icn.setEnabled(state and is_crs_3d)

            reset_icon = QtGui.QIcon("icons/circle.png")

            if state:
                self.check_if_coords_columns_exist()
            else:
                self.view.x_column_name_icn.setIcon(reset_icon)
                self.view.y_column_name_icn.setIcon(reset_icon)
                self.view.z_column_name_icn.setIcon(reset_icon)
                self.view.reproject_ok_btn.setEnabled(True)

            if not is_crs_3d:
                self.view.z_column_name_icn.setIcon(reset_icon)

        except Exception as error:
            self.handle_exception(error, "save_coords_checkbox_checked()", "Ops! Ocorreu um erro.")

    def check_if_coords_columns_exist(self):
        crs_type = CRS_DICT[self.view.target_crs_cbx.currentText()]["type"]

        edits = [self.view.x_column_name_edt, self.view.y_column_name_edt]
        buttons = [self.view.x_column_name_icn, self.view.y_column_name_icn]
        xyz_ok = [False, False]

        if crs_type == "Geographic 3D CRS":
            edits.append(self.view.z_column_name_edt)
            buttons.append(self.view.z_column_name_icn)
            xyz_ok.append(False)

        for i, b in enumerate(xyz_ok):
            col_name = edits[i].text()
            btn = buttons[i]
            if col_name in self.model.gdf.columns:
                xyz_ok[i] = True
                btn.setIcon(QtGui.QIcon("icons/alert.png"))
                btn.setToolTip("A coluna já existe na tabela. Os dados contidos nela serão\n"
                               "substituídos pelas coordenadas reprojetadas.")
            elif col_name == "":
                xyz_ok[i] = False
                btn.setIcon(QtGui.QIcon("icons/not_ok.png"))
                btn.setToolTip("Insira um nome para a coluna.")
            else:
                xyz_ok[i] = True
                btn.setIcon(QtGui.QIcon("icons/ok.png"))
                btn.setToolTip(f"A coluna \"{col_name}\" será criada com\nas coordenadas reprojetadas.")

        self.view.reproject_ok_btn.setEnabled(all(xyz_ok))

    def reproject_ok_button_clicked(self):
        try:
            toggle_wait_cursor(True)

            crs_key = self.view.target_crs_cbx.currentText()
            save_coords = self.view.save_coords_chk.isChecked()

            self.model.reproject_geodataframe(crs_key)

            if save_coords:
                x_col = self.view.x_column_name_edt.text()
                y_col = self.view.y_column_name_edt.text()

                self.model.gdf[x_col] = self.model.gdf.geometry.x
                self.model.gdf[y_col] = self.model.gdf.geometry.y

                if CRS_DICT[crs_key]["type"] == "Geographic 3D CRS":
                    z_col = self.view.z_column_name_edt.text()
                    self.model.gdf[z_col] = self.model.gdf.geometry.z

                # Reordena as colunas para que a geometria fique no final
                if "geometry" in self.model.gdf.columns and self.model.gdf["geometry"].dtype == "geometry":
                    cols = [col for col in self.model.gdf.columns if col != "geometry"]
                    cols.append("geometry")
                    self.model.gdf = self.model.gdf[cols]

            self.update_column_list()
            self.view.switch_stack()

            crs_label = f"{self.model.gdf.crs.name} ({self.model.gdf.crs.type_name})"
            label = f"Pontos: {len(self.model.gdf.index)}    SRC: {crs_label}"
            self.view.bottom_label.setText(label if len(label) < 87 else f"Pontos: {len(self.model.gdf.index)}")

            toggle_wait_cursor(False)
            show_popup("Pontos reprojetados com sucesso!", parent=self.view)

        except Exception as error:
            self.handle_exception(error, "reproject_ok_button_clicked()", "Ops! Ocorreu um erro ao reprojetar.")

    def export_button_clicked(self):
        try:
            file_name = show_file_dialog(
                caption="Salvar arquivo", mode="save", parent=self.view,
                extension_filter="Formatos suportados (*.gpkg *.geojson *.shp *.csv *.xlsx);;"
                                 "Geopackage (*.gpkg);;"
                                 "GeoJSON (*.geojson);;"
                                 "Shapefile (*.shp);;"
                                 "Comma Separated Values (*.csv);;"
                                 "Pasta de Trabalho do Excel (*.xlsx)"
            )

            if file_name == "":
                return

            _, file_extension = os.path.splitext(file_name)
            if not file_extension:
                file_name += ".gpkg"

            layer_name = "pontos"
            if file_name.endswith(".gpkg"):
                layer_name, ok_clicked = show_input_dialog("Insira um nome para a camada:", "Nome da camada",
                                                           layer_name, self.view)
                if not ok_clicked:
                    return

            toggle_wait_cursor(True)
            self.model.export_geodataframe(file_name, layer_name)
            toggle_wait_cursor(False)
            show_popup("Pontos exportados com sucesso!", parent=self.view)

        except Exception as error:
            self.handle_exception(error, "export_button_clicked()", "Ops! Não foi possível exportar.")

    def graph_button_clicked(self):
        try:
            action = self.view.graph_button.click_menu.exec(self.view.graph_button.mapToGlobal(self.view.graph_button.rect().bottomLeft()))

            if action is self.view.graph_stereogram_action:
                graph_window = StereogramWindow(self.view, pandas.DataFrame(self.model.gdf))
                graph_window.show()
                center_window_on_point(graph_window, graph_window.parent.geometry().center())

            elif action is self.view.graph_rosediagram_action:
                graph_window = RoseChartWindow(self.view, pandas.DataFrame(self.model.gdf))
                graph_window.show()
                center_window_on_point(graph_window, graph_window.parent.geometry().center())

        except Exception as error:
            self.handle_exception(error, "graph_button_clicked()", "Ops! Ocorreu um erro.")

    def rename_column_action_triggered(self):
        try:
            row = self.view.columns_list.currentRow()
            column = self.column_list_widgets[row].field

            new_name, ok_clicked = show_input_dialog("Insira um novo nome para a coluna:", "Renomear coluna", column, self.view)

            if not ok_clicked:
                return

            toggle_wait_cursor(True)

            if new_name in self.model.gdf.columns:
                raise ValueError("O nome inserido já está sendo utilizado por outra coluna do GeoDataFrame.")

            self.model.gdf.rename(columns={column: new_name}, inplace=True)
            self.column_list_widgets[row].field = new_name
            self.update_column_list(row)
            toggle_wait_cursor(False)
        except Exception as error:
            self.handle_exception(error, "rename_column_action_triggered()", "Ops! Não foi possível renomear a coluna.")

    def delete_column_action_triggered(self):
        try:
            row = self.view.columns_list.currentRow()
            column = self.column_list_widgets[row].field

            yes_or_no = show_question_dialog(f"Excluir coluna \"{column}\"?", self.view)

            if yes_or_no != QtWidgets.QMessageBox.StandardButton.Yes.value:
                return

            toggle_wait_cursor(True)
            self.model.gdf.drop(columns=[column], inplace=True)
            self.column_list_widgets.pop(row)
            self.update_column_list(row)
            toggle_wait_cursor(False)
        except Exception as error:
            self.handle_exception(error, "delete_column_action_triggered()", "Ops! Não foi possível deletar a coluna.")

    def show_uniques_action_triggered(self):
        try:
            toggle_wait_cursor(True)

            row = self.view.columns_list.currentRow()
            column = self.column_list_widgets[row].field

            uniques = self.model.gdf[column].astype("string").unique()
            has_na = any(pandas.isna(value) for value in uniques)
            uniques = [value for value in uniques if not pandas.isna(value)]

            toggle_wait_cursor(False)

            list_window = ListWindow(sorted(uniques), has_na, self.view)
            list_window.show()
            center_window_on_point(list_window, list_window.parent.geometry().center())
        except Exception as error:
            self.handle_exception(error, "show_uniques_action_triggered()", "Ops! Ocorreu um erro ao obter a lista de valores únicos.")

    def handle_exception(self, error, context, message: str = "Ocorreu um erro.", ):
        toggle_wait_cursor(False)
        ic(context, error)
        show_popup(f"{message}", "error", f"Descrição do erro: {error}\n\nContexto: {context}", self.view)


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
