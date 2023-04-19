import pyproj
import numpy
import pandas
import geopandas
from csv import Sniffer
from collections import Counter
from os import getcwd
from PyQt6.QtGui import QIcon

from View import (show_popup, show_file_dialog, show_selection_dialog,
                  show_input_dialog)
from Model import crs_dict


class MainController:
    def __init__(self, model):
        self.model = model

    def open_file(self):

        def get_file_path():

            file_name, file_type = show_file_dialog(
                caption="Selecione uma tabela contendo os dados de entrada.",
                extension_filter=("Formatos suportados (*.xlsx *.xlsm *.csv *.ods);;"
                                  "Pasta de Trabalho do Excel (*.xlsx);;"
                                  "Pasta de Trabalho Habilitada para Macro do Excel (*.xlsm);;"
                                  "Comma Separated Values (*.csv);; "
                                  "OpenDocument Spreadsheet (*.ods)"),
                mode="open"
            )
            return file_name

        def read_file(path):

            multiple_sheets = False
            excel_file = None
            # Arquivo csv
            if path.endswith(".csv"):
                sniffer = Sniffer()
                data = open(path, "r").read(4096)
                sep = str(sniffer.sniff(data).delimiter)
                df = pandas.read_csv(path, delimiter=sep)
            # Arquivo xlsx, xlsm ou ods
            else:
                engine = ("odf" if path.endswith(".ods") else "openpyxl")
                excel_file = pandas.ExcelFile(path, engine=engine)
                sheets = excel_file.sheet_names
                # Se houver mais de 1 aba, o usuário seleciona uma delas
                if len(sheets) > 1:
                    multiple_sheets = True
                    sheet, ok = show_selection_dialog(
                        "Selecione a aba do arquivo que contém as coordenadas dos pontos:", sheets
                    )
                    if not ok:
                        return False, None, False, None
                else:
                    sheet = 0
                df = excel_file.parse(sheet_name=sheet)
            # Checa se o dataframe foi criado ou não
            file_open = True if isinstance(df, pandas.DataFrame) else False
            return file_open, excel_file, multiple_sheets, df

        def process_data(df):

            # Converte os nomes das colunas para str para evitar erros estranhos
            df.columns = df.columns.astype(str)
            # Remove colunas e linhas em branco
            remove_cols = [col for col in df.columns
                           if 'Unnamed' in col and len(df[col]) == 0]
            df = df.drop(remove_cols, axis='columns')
            df = df.replace(r'^\s*$', pandas.NA, regex=True)
            df = df.dropna(how='all', axis='index')
            return df

        def set_model_attributes(path, excel_file, multiple_sheets, df):

            self.model.path = path
            self.model.excel_file = excel_file
            self.model.multiple_sheets = multiple_sheets
            self.model.df = df
            self.model.crs = None
            self.model.coordinate_columns = [None, None]
            self.model.gdf = None

        path = get_file_path()

        if path == "":
            return False

        file_open, excel_file, multiple_sheets, df = read_file(path)

        if file_open:
            df = process_data(df)
            set_model_attributes(path, excel_file, multiple_sheets, df)
            return True
        return False

    def merge_sheets(self):

        # Filtra as colunas que aparecem em todas as abas
        sheet_names = self.model.excel_file.sheet_names
        columns_list = []
        for sheet_name in sheet_names:
            df = self.model.excel_file.parse(sheet_name=sheet_name)
            columns_list = columns_list + df.columns.to_list()
        count = Counter(columns_list)
        merge_column_options = [k for k, v in count.items() if v > 1]

        # Usuário seleciona a coluna de mescla
        merge_column, ok = show_selection_dialog(
            ("Selecione uma coluna em comum entre as abas para realizar a mescla.\n"
             "Apenas pontos presentes na aba principal (selecionada ao abrir o arquivo)\nserão incluídos (inner join)."),
            merge_column_options
        )
        if not ok:
            return

        number_of_sheets = len(self.model.excel_file.sheet_names)

        # Verifica quais abas do arquivo possuem a coluna de mescla
        sheets_to_merge, sheets_to_ignore = [], []
        for i in range(0, number_of_sheets):
            if merge_column in self.model.excel_file.parse(i).columns.to_list():
                sheets_to_merge.append(i)
            else:
                sheets_to_ignore.append(self.model.excel_file.sheet_names[i])

        # Avisa o usuário caso alguma aba não possua a coluna de mescla
        if sheets_to_ignore:
            show_popup(f"As seguintes abas não possuem a coluna {merge_column} "
                       f"e, portanto, não serão adicionadas ao DataFrame:\n"
                       f"{', '.join(sheets_to_ignore)}")

        # Lê todas as abas do arquivo e armazena em uma lista. Armazena também
        # os dtypes das colunas de merge de cada aba
        sheets, merge_dts = [], []
        for i in range(0, number_of_sheets):
            if i in sheets_to_merge:
                sheet = self.model.excel_file.parse(sheet_name=i)
                # Remove colunas e linhas totalmente vazias
                remove_cols = [col for col in df.columns
                               if 'Unnamed' in col and len(df[col]) == 0]
                df = df.drop(remove_cols, axis='columns')
                sheet.dropna(how='all', axis='index', inplace=True)
                sheets.append(sheet)
                merge_dts.append(sheet[merge_column].dtype)

        # Verifica se a coluna de mescla tem o mesmo dtype em todas as abas.
        # Se não tiver, converte todas para string
        if not merge_dts.count(merge_dts[0]) == len(merge_dts):
            for s in sheets:
                s[merge_column] = s[merge_column].astype(str)

        # Mescla as abas com base na coluna de mescla selecionada pelo usuário
        df = sheets[0]
        for i in range(1, len(sheets)):
            df = pandas.merge(df, sheets[i], how='outer', on=merge_column)

        # Converte os nomes das colunas para string para evitar erros esquisitos
        df.columns = df.columns.astype(str)

        # Restaura a ordem correta das colunas e armazena no atributo apropriado
        cols = df.columns.to_list()
        cols.remove(merge_column)
        columns = [merge_column] + cols
        self.model.df = df[columns]

    def switch_dtype(self, column, target_dtype):

        # Conversão para datetime
        if target_dtype == "datetime64[ns]":
            if self.model.df[column].dtype == "category":
                self.model.df[column] = self.model.df[column].astype("object")
            self.model.df[column] = pandas.to_datetime(self.model.df[column])

        # Conversão para timedelta
        elif target_dtype == "timedelta64[ns]":
            # Opções de unidade
            unit_options = ["days", "hours", "minutes", "seconds",
                            "miliseconds", "microseconds", "nanoseconds"]
            # Exibe uma caixa de diálogo para selecionar a unidade de tempo
            time_unit, ok = show_selection_dialog(
                "Selecione a unidade de medida de tempo do campo:",
                unit_options
            )
            # Se o usuário der ok na caixa, faz a conversão
            if ok:
                self.model.df[column] = pandas.to_timedelta(
                    self.model.df[column], unit=time_unit
                )

        # Conversão para boolean
        elif target_dtype == "bool":
            # Obtém uma lista de valores únicos da coluna
            column_data = self.model.df[column].astype(str)
            bool_options = column_data.unique()
            selected_true_value = self.select_bool_option(bool_options, True)
            selected_false_value = self.select_bool_option(bool_options, False)
            if len(bool_options) != 2:
                raise Exception(f"A coluna em questão contém mais de dois "
                                f"valores únicos (para verdadeiro/falso) ou "
                                f"possui células vazias (nan)."
                                f"\n\n{bool_options}")
            # Caixa para selecionar o valor True
            true_key, ok1 = show_selection_dialog(
                "Selecione o valor verdadeiro:",
                bool_options, selected=selected_true_value
            )
            # Caixa para selecionar o valor False
            false_key, ok2 = show_selection_dialog(
                "Selecione o valor falso:",
                bool_options, selected=selected_false_value
            )
            # Se o usuário der ok nas caixas, faz a conversão
            if ok1 and ok2:
                self.model.df[column] = column_data.map({true_key: True,
                                                         false_key: False})
        # Conversão para os demais tipos (string, float, int...)
        else:
            self.model.df[column] = self.model.df[column].astype(target_dtype)
        return True

    def select_bool_option(self, options, true_or_false: bool):
        if true_or_false is True:
            common_values = ["true", "sim", "verdadeiro", "v", "yes", "y", "1"]
        else:
            common_values = ["false", "não", "nao", "falso", "f", "no", "0"]

        for i, value in enumerate(options):
            if str(value).lower() in common_values:
                return i

        return 0

    def save_csv(self):
        self.model.df.to_csv("dataframe.csv", sep=";", decimal=",",
                             encoding="utf-8-sig", index=False)
        show_popup(f"DataFrame salvo em {getcwd()}\\dataframe.csv.")

    def get_crs_list(self):
        crs_list = sorted(
            list(crs_dict.keys()),
            key=lambda x: (crs_dict[x]['name'], crs_dict[x]['type'])
        )
        return crs_list

    def get_crs_icons(self, crs_list):
        icon_list = []
        for crs in crs_list:
            if "GEOGRAPHIC" in str(crs_dict[crs]["type"]):
                icon_list.append(QIcon("icons/latlon.png"))
            else:
                icon_list.append(QIcon("icons/projected.png"))
        return icon_list

    def get_coordinate_columns(self, crs_key):

        df = self.model.df

        crs_auth = crs_dict[crs_key]["auth_name"]
        crs_code = crs_dict[crs_key]["code"]
        crs = pyproj.CRS.from_authority(crs_auth, crs_code)

        x_min, y_min, x_max, y_max = crs.area_of_use.bounds

        valid_x_columns = []
        valid_y_columns = []

        # Check each column for validity.
        for column in df.columns:
            try:
                # Try to convert column to a float or integer.
                coords = df[column].astype(float)

                # Create a Point object to check validity.
                if coords.dtype in ["float64", "int64"]:

                    if crs.is_geographic:
                        if all(y_min <= c <= y_max for c in coords):
                            valid_x_columns.append(column)
                        if all(x_min <= c <= x_max for c in coords):
                            valid_y_columns.append(column)
                    elif crs.is_projected:
                        if all(165000 <= c <= 835000 for c in coords) or \
                                all(1099000 <= c <= 10000000 for c in coords):
                            valid_x_columns.append(column)
                            valid_y_columns.append(column)
                else:
                    continue
            except (ValueError, TypeError) as error:
                if (not str(error).startswith("could not convert")
                        and not str(error).startswith("Cannot cast")):
                    print(f"{error}")

        return valid_x_columns, valid_y_columns

    def select_coord_column(self, axis, options):
        if axis == "y":
            common_names = ["latitude", "lat", "northing", "utm_n", "utmn", "n",
                            "y", "utmn (m)"]
        elif axis == "x":
            common_names = ["longitude", "lon", "easting", "utm_e", "utme", "e",
                            "x", "utme (m)"]
        else:
            raise Exception('Expected "y" or "x" for axis')

        for col in options:
            if str(col).lower() in common_names:
                return col

        return None

    def reproject(self, output_crs_key):
        y_column, x_column = self.model.y_column, self.model.x_column
        input_auth = crs_dict[self.model.crs]["auth_name"]
        input_code = crs_dict[self.model.crs]["code"]
        output_auth = crs_dict[output_crs_key]["auth_name"]
        output_code = crs_dict[output_crs_key]["code"]

        input_type = (
            "utm"
            if str(crs_dict[self.model.crs]["type"]) == "PJType.PROJECTED_CRS"
            else "latlon"
        )
        output_type = (
            "utm"
            if str(crs_dict[output_crs_key]["type"]) == "PJType.PROJECTED_CRS"
            else "latlon"
        )

        input_crs = pyproj.CRS.from_authority(input_auth, input_code)
        output_crs = pyproj.CRS.from_authority(output_auth, output_code)

        transformer = pyproj.Transformer.from_crs(input_crs, output_crs)

        input_y, input_x = self.model.df[y_column], self.model.df[x_column]
        output_y, output_x = [], []

        for old_y, old_x in zip(input_y, input_x):
            try:
                if input_type == "latlon" and output_type == "utm":
                    new_x, new_y = transformer.transform(old_y, old_x)
                elif input_type == "latlon" and output_type == "latlon":
                    new_y, new_x = transformer.transform(old_y, old_x)
                elif input_type == "utm" and output_type == "latlon":
                    new_y, new_x = transformer.transform(old_x, old_y)
                elif input_type == "utm" and output_type == "utm":
                    new_x, new_y = transformer.transform(old_x, old_y)
                else:
                    raise Exception("Can't handle input/output type combination")

                if new_x == numpy.inf or new_y == numpy.inf:
                    raise TypeError("Invalid coordinate")

                output_y.append(new_y)
                output_x.append(new_x)

            except TypeError:
                output_y.append(pandas.NA)
                output_x.append(pandas.NA)

        self.model.df[y_column] = output_y
        self.model.df[x_column] = output_x

        new_y_column = "Latitude" if output_type == "latlon" else "Northing"
        new_x_column = "Longitude" if output_type == "latlon" else "Easting"

        self.model.df.rename(columns={y_column: new_y_column,
                                      x_column: new_x_column}, inplace=True)

        self.model.crs = output_crs_key
        self.model.y_column = new_y_column
        self.model.x_column = new_x_column

    def build_gdf(self):

        crs_key = self.model.crs

        crs_auth = crs_dict[crs_key]["auth_name"]
        crs_code = str(crs_dict[crs_key]["code"])
        crs = pyproj.CRS.from_authority(crs_auth, crs_code)

        y = self.model.df[self.model.y_column]
        x = self.model.df[self.model.x_column]
        geometry = geopandas.points_from_xy(x, y, crs=crs)

        self.model.gdf = geopandas.GeoDataFrame(self.model.df,
                                                geometry=geometry,
                                                crs=crs)

    def save_points(self):

        # Show the file dialog to choose the file name and type
        file_name, file_type = show_file_dialog(
            caption='Salvar GeoDataFrame',
            extension_filter=('GeoPackage (*.gpkg);;'
                              'ESRI Shapefile (*.shp);;'
                              'GeoJSON (*.geojson)'),
            mode="save"
        )
        if file_name == "":
            return False

        self.adapt_column_dtypes(file_name)
        gdf = self.model.gdf

        # Save the GeoDataFrame to the selected file
        if file_name.endswith(".gpkg"):
            # Ask the user for the layer name
            layer_name, ok = show_input_dialog('Insira um nome para a camada:',
                                               'Camada',
                                               'pontos')
            layer_name = layer_name if ok else "unnamed_layer"
            # Save the GeoDataFrame to the selected file with the specified layer name
            gdf.to_file(file_name, layer=layer_name, driver='GPKG')

        elif file_name.endswith(".shp"):
            gdf.to_file(file_name, driver='ESRI Shapefile')

        elif file_name.endswith(".geojson"):
            gdf.to_file(file_name, driver='GeoJSON')

        return True

    def adapt_column_dtypes(self, file_name):
        gdf = self.model.gdf
        if file_name.endswith(".shp"):
            bad_types = ["datetime64[ns]", "<M8[ns]", "category", "timedelta64[ns]"]
        else:
            bad_types = ["<M8[ns]", "category", "timedelta64[ns]"]

        adapted_columns = []
        for column, dtype in zip(gdf.columns, gdf.dtypes):
            if dtype in bad_types:
                gdf[column] = gdf[column].astype(str)
                adapted_columns.append(column)

        if adapted_columns:
            show_popup(f"As seguintes colunas tinham tipos de dado não "
                       f"suportados pelo formato escolhido e, portanto, "
                       f"foram convertidas para string durante a "
                       f"exportação:\n\n{', '.join(adapted_columns)}")
