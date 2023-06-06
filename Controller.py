# -*- coding: utf-8 -*-
"""
@author: Gabriel Maccari
"""
import pyproj
import numpy
import csv
import pandas
import collections
import geopandas
import os
import exif

from PyQt6 import QtGui
from shapely.geometry import Point

from ViewController import show_popup, show_file_dialog, show_selection_dialog, show_input_dialog, show_wait_cursor
from Model import crs_dict, GeographicTable


class MainController:
    def __init__(self, model_class=GeographicTable):
        self.model_class = model_class
        self.model = None

    def create_new_model_instance(self, path, excel_file, df):
        self.model = None
        self.model = self.model_class(path, excel_file, df)

    def get_df_columns(self) -> list[str]:
        columns = self.model.df.columns.to_list()
        return columns

    def get_df_dtypes(self) -> list[str]:
        dtypes = self.model.df.dtypes.to_list()
        return dtypes

    def get_model_attribute(self, attribute: str):
        return getattr(self.model, attribute)

    def set_model_attribute(self, attribute: str, value):
        setattr(self.model, attribute, value)

    def open_file(self, path: str) -> (bool, bool):
        excel_file, df = self.read_file(path)

        file_open = True if isinstance(df, pandas.DataFrame) else False

        if file_open:
            df = self.process_data(df)

            if excel_file is not None:
                multiple_sheets = True if len(excel_file.sheet_names) > 1 else False
            else:
                multiple_sheets = False

            self.create_new_model_instance(path, excel_file, df)

            return True, multiple_sheets

        return False, False

    def read_file(self, path: str) -> (pandas.ExcelFile, bool, pandas.DataFrame):
        excel_file, df = None, None
        # Arquivo csv
        if path.endswith(".csv"):
            sniffer = csv.Sniffer()
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
                sheet, ok = show_selection_dialog("Selecione a planilha que contém as coordenadas dos pontos:", sheets)
                if not ok:
                    return False, None, False, None
            else:
                sheet = 0
            df = excel_file.parse(sheet_name=sheet)

        return excel_file, df

    def process_data(self, df: pandas.DataFrame) -> pandas.DataFrame:
        # Converte os nomes das colunas para str para evitar erros estranhos
        df.columns = df.columns.astype(str)
        # Remove colunas e linhas em branco
        remove_cols = [col for col in df.columns if 'Unnamed' in col and len(df[col]) == 0]
        df = df.drop(remove_cols, axis='columns')
        df = df.replace(r'^\s*$', pandas.NA, regex=True)
        df = df.dropna(how='all', axis='index')
        return df

    def merge_sheets(self):
        # Filtra as colunas que aparecem em todas as abas
        sheet_names = self.model.excel_file.sheet_names
        columns_list = []
        for sheet_name in sheet_names:
            sheet = self.model.excel_file.parse(sheet_name=sheet_name)
            columns_list = columns_list + sheet.columns.to_list()
        count = collections.Counter(columns_list)
        merge_column_options = [k for k, v in count.items() if v > 1]

        # Usuário seleciona a coluna de mescla
        merge_column, ok = show_selection_dialog(
            ("Selecione uma coluna em comum entre as abas para realizar a mescla.\n"
             "Apenas pontos presentes na aba inicial (selecionada ao abrir o arquivo)\nserão incluídos."),
            merge_column_options
        )
        if not ok:
            return

        show_wait_cursor()

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
            show_wait_cursor(False)
            show_popup(f"As seguintes abas não possuem a coluna {merge_column} e, portanto, não serão adicionadas ao "
                       f"DataFrame:\n{', '.join(sheets_to_ignore)}")
            show_wait_cursor()

        # Lê as abas do arquivo e armazena em uma lista. Armazena também os dtypes das colunas de merge de cada aba
        sheets, merge_dts = [], []
        for i in range(0, number_of_sheets):
            if i not in sheets_to_merge:
                continue
            sheet = self.model.excel_file.parse(sheet_name=i)

            # Remove colunas e linhas totalmente vazias # TODO utilizar a função já definida pra isso
            remove_cols = [col for col in sheet.columns if 'Unnamed' in col and len(sheet[col]) == 0]
            sheet = sheet.drop(remove_cols, axis='columns')
            sheet.dropna(how='all', axis='index', inplace=True)
            sheets.append(sheet)
            merge_dts.append(sheet[merge_column].dtype)

        # Verifica se a coluna de mescla tem o mesmo dtype em todas as abas. Se não tiver, converte todas para string
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

        show_wait_cursor(False)

    def switch_dtype(self, column: str, target_dtype: str) -> bool:
        # Conversão para datetime
        if target_dtype == "datetime64[ns]":
            if self.model.df[column].dtype == "category":
                self.model.df[column] = self.model.df[column].astype("object")
            self.model.df[column] = pandas.to_datetime(self.model.df[column])

        # Conversão para timedelta
        elif target_dtype == "timedelta64[ns]":
            unit_options = ["days", "hours", "minutes", "seconds", "miliseconds", "microseconds", "nanoseconds"]
            time_unit, ok = show_selection_dialog("Selecione a unidade de medida de tempo do campo:", unit_options)
            if not ok:
                return False
            self.model.df[column] = pandas.to_timedelta(self.model.df[column], unit=time_unit)

        # Conversão para boolean
        elif target_dtype == "bool":
            # Obtém uma lista de valores únicos da coluna
            column_data = self.model.df[column].astype(str)
            bool_options = column_data.unique()
            selected_true_value = self.select_bool_option(bool_options, True)
            selected_false_value = self.select_bool_option(bool_options, False)
            if len(bool_options) != 2:
                raise Exception(f"A coluna em questão contém mais de dois valores únicos (para verdadeiro/falso) ou "
                                f"possui células vazias (nan).\n\n{bool_options}")

            # Caixa para selecionar o valor True
            true_key, ok1 = show_selection_dialog("Selecione o valor verdadeiro:",
                                                  bool_options, selected=selected_true_value)

            # Caixa para selecionar o valor False
            false_key, ok2 = show_selection_dialog("Selecione o valor falso:",
                                                   bool_options, selected=selected_false_value)

            # Se o usuário der ok nas caixas, faz a conversão
            if ok1 and ok2:
                self.model.df[column] = column_data.map({true_key: True, false_key: False})

        # Conversão para float
        elif target_dtype == "float64":
            self.model.df[column] = self.model.df[column].replace(",", ".", regex=True)
            self.model.df[column] = self.model.df[column].astype("float64")

        # Conversão para os demais tipos (string, int...)
        else:
            self.model.df[column] = self.model.df[column].astype(target_dtype)

        return True

    def select_bool_option(self, options: list[str], true_or_false: bool) -> int:
        common_values = (("true", "sim", "verdadeiro", "v", "yes", "y", "1") if true_or_false
                         else ("false", "não", "nao", "falso", "f", "no", "0"))

        for i, value in enumerate(options):
            if str(value).lower() in common_values:
                return i

        return 0

    def save_csv(self):
        path = show_file_dialog("Salvar tabela", "Comma Separated Values (*.csv)", "save", None)
        if path != "":
            if not path.endswith(".csv"):
                path = path + ".csv"
            self.model.df.to_csv(path, sep=";", decimal=",", encoding="utf-8-sig", index=False)
            show_popup(f"Tabela salva com sucesso!")

    def get_crs_list(self) -> list[str]:
        crs_list = sorted(list(crs_dict.keys()), key=lambda x: (crs_dict[x]['name'], crs_dict[x]['type']))

        return crs_list

    def get_crs_icons(self, crs_list: list[str]) -> list[QtGui.QIcon]:
        icon_list = []
        for crs in crs_list:
            if "GEOGRAPHIC" in str(crs_dict[crs]["type"]):
                icon_list.append(QtGui.QIcon("icons/latlon.png"))
            else:
                icon_list.append(QtGui.QIcon("icons/projected.png"))

        return icon_list

    def get_coordinate_columns(self, crs_key: str) -> (list[str], list[str]):
        df = self.model.df

        crs_auth = crs_dict[crs_key]["auth_name"]
        crs_code = crs_dict[crs_key]["code"]
        crs = pyproj.CRS.from_authority(crs_auth, crs_code)

        x_min, y_min, x_max, y_max = crs.area_of_use.bounds

        valid_x_columns = []
        valid_y_columns = []

        for column in df.columns:
            try:
                coords = df[column].astype(float)

                if coords.dtype not in ["float64", "int64"]:
                    continue

                if crs.is_geographic:
                    if all(y_min <= c <= y_max for c in coords):
                        valid_x_columns.append(column)
                    if all(x_min <= c <= x_max for c in coords):
                        valid_y_columns.append(column)
                elif crs.is_projected:
                    if all(165000 <= c <= 835000 for c in coords) or all(1099000 <= c <= 10000000 for c in coords):
                        valid_x_columns.append(column)
                        valid_y_columns.append(column)

            except (ValueError, TypeError) as error:
                if not str(error).startswith("could not convert") and not str(error).startswith("Cannot cast"):
                    print(f"ERRO: {error}")

        return valid_x_columns, valid_y_columns

    def select_coord_column(self, axis: str, options: list[str]) -> str | None:
        if axis == "y":
            common_names = ("latitude", "lat", "northing", "utm_n", "utmn", "n", "y", "utmn (m)")
        elif axis == "x":
            common_names = ("longitude", "lon", "easting", "utm_e", "utme", "e", "x", "utme (m)")
        else:
            raise Exception('Expected "y" or "x" for axis')

        for col in options:
            if str(col).lower() in common_names:
                return col

        return None

    def reproject(self, output_crs_key: str):
        y_column, x_column = self.model.y_column, self.model.x_column
        input_auth = crs_dict[self.model.crs]["auth_name"]
        input_code = crs_dict[self.model.crs]["code"]
        output_auth = crs_dict[output_crs_key]["auth_name"]
        output_code = crs_dict[output_crs_key]["code"]

        input_type = ("utm" if str(crs_dict[self.model.crs]["type"]) == "PJType.PROJECTED_CRS" else "latlon")
        output_type = ("utm" if str(crs_dict[output_crs_key]["type"]) == "PJType.PROJECTED_CRS" else "latlon")

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

        self.model.df.rename(columns={y_column: new_y_column, x_column: new_x_column}, inplace=True)

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

        self.model.gdf = geopandas.GeoDataFrame(self.model.df, geometry=geometry, crs=crs)

    def save_points(self) -> bool:
        file_name = show_file_dialog(
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

        if file_name.endswith(".gpkg"):
            layer_name, ok = show_input_dialog('Insira um nome para a camada:', 'Camada', 'pontos')
            layer_name = layer_name if ok else "unnamed_layer"
            gdf.to_file(file_name, layer=layer_name, driver='GPKG')

        elif file_name.endswith(".shp"):
            gdf.to_file(file_name, driver='ESRI Shapefile')

        elif file_name.endswith(".geojson"):
            gdf.to_file(file_name, driver='GeoJSON')

        else:
            return False

        return True

    def adapt_column_dtypes(self, file_name: str):
        gdf = self.model.gdf
        if file_name.endswith(".shp"):
            bad_types = ("datetime64[ns]", "<M8[ns]", "category", "timedelta64[ns]")
        else:
            bad_types = ("<M8[ns]", "category", "timedelta64[ns]")

        adapted_columns = []
        for column, dtype in zip(gdf.columns, gdf.dtypes):
            if dtype in bad_types:
                gdf[column] = gdf[column].astype(str)
                adapted_columns.append(column)

        if adapted_columns:
            show_popup(f"As seguintes colunas tinham tipos de dado não suportados pelo formato escolhido e, portanto, "
                       f"foram convertidas para string durante a exportação:\n\n{', '.join(adapted_columns)}")

    def organize_pictures_by_point(self, directory: str, label_field: str, max_distance: int):
        file_names = os.listdir(directory)

        supported_formats = (".jpg", "jpeg", ".png", ".tif", "tiff", "webp", ".gif", ".bmp", "avif")

        file_paths = [f"{directory}/{file}" for file in file_names
                      if os.path.isfile(f"{directory}/{file}")
                      and file.lower()[-4:] in supported_formats]

        if not file_paths:
            raise Exception(f"Diretório não contém imagens (formatos suportados: JPG, PNG, TIF, WEBP, GIF, BMP e AVIF).")

        points = self.get_model_attribute("gdf")

        pic_points = self.assign_pictures_to_points(file_paths, points, label_field, max_distance)
        self.move_pictures_to_folders(file_paths, pic_points, directory)

    def assign_pictures_to_points(self, file_paths: list[str], points: geopandas.GeoDataFrame, label_field: str,
                                  max_distance: int) -> list[str]:
        names, geometries = [], []
        for path in file_paths:
            names.append(path.split("/")[-1])
            lon_lat = self.get_img_coordinates(path)
            try:
                geometries.append(Point(lon_lat))
            except TypeError:
                geometries.append(None)

        img_dict = {"image": names, "geometry": geometries}
        pictures = geopandas.GeoDataFrame(img_dict, crs="EPSG:4326", geometry=img_dict["geometry"]).to_crs(points.crs)

        pictures = pictures.sjoin_nearest(points, how="left", max_distance=max_distance, distance_col="distance")

        return list(pictures[label_field])

    def get_img_coordinates(self, image_path: str):
        def tuple_to_dd(coords: tuple, ref: str):
            dd = coords[0] + coords[1] / 60 + coords[2] / 3600
            if ref == "S" or ref == 'W':
                dd = -dd
            return dd

        """if not os.path.isfile(image_path):
            return None"""

        with open(image_path, 'rb') as src:
            """try:"""
            img = exif.Image(src)
            """except plum.exceptions.UnpackError:  # Esse erro acontece quando o arquivo não é uma imagem
                return None"""

        if not img.has_exif:
            return None

        try:
            lat, lat_ref = img.gps_latitude, img.gps_latitude_ref
            lon, lon_ref = img.gps_longitude, img.gps_longitude_ref
            coordinates = (tuple_to_dd(lon, lon_ref), tuple_to_dd(lat, lat_ref))
        except AttributeError:
            return None

        return coordinates

    def move_pictures_to_folders(self, file_paths: list[str], picture_points: list[str], folder_path: str):
        for src_path, point in zip(file_paths, picture_points, strict=True):
            if not os.path.isfile(src_path):
                continue

            image_name = src_path.split("/")[-1]

            directory = f"{folder_path}/{point}"
            if not os.path.isdir(directory):
                os.makedirs(directory)

            dest_path = f"{directory}/{image_name}"

            os.rename(src_path, dest_path)
