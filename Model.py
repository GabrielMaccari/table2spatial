# -*- coding: utf-8 -*-
"""
@author: Gabriel Maccari
"""

import csv
import pandas
import geopandas
import pyproj
import warnings

from icecream import ic

CRS_DICT = {}
for crs_info in pyproj.database.query_crs_info(pj_types=["GEOGRAPHIC_2D_CRS", "PROJECTED_CRS"]):
    key = f"{crs_info.name} ({crs_info.auth_name}:{crs_info.code})"
    CRS_DICT[key] = {
        "name": crs_info.name,
        "auth_name": crs_info.auth_name,
        "code": crs_info.code,
        "type": crs_info.type,
        "area_of_use": crs_info.area_of_use
    }
del crs_info, key

DTYPES_DICT = {
    "String": {
        "pandas_dtypes": ("object", "category"),
        "icon": "icons/string.png"
    },
    "Integer": {
        "pandas_dtypes": ('int64', 'uint64', 'int32', 'uint32', 'int16', 'uint16', 'int8', 'uint8'),
        "icon": "icons/integer.png"
    },
    "Float": {
        "pandas_dtypes": ("float64", "float32", "float16"),
        "icon": "icons/float.png"
    },
    "Boolean": {
        "pandas_dtypes": ("bool"),
        "icon": "icons/boolean.png"
    },
    "Datetime": {
        "pandas_dtypes": ("datetime64[ns]", "<M8[ns]", ">M8[ns]"),
        "icon": "icons/datetime.png"
    }
}

DATETIME_FORMATS = {
    "DD/MM/YYYY": "%d/%m/%Y",
    "YYYY/MM/DD": "%Y/%m/%d",
    "MM/DD/YYYY": "%m/%d/%Y",
    "DD-MM-YYYY": "%d-%m-%Y",
    "YYYY-MM-DD": "%Y-%m-%d",
    "MM-DD-YYYY": "%m-%d-%Y",
    "YYYY/MM/DD HH:MM:SS": "%Y/%m/%d %H:%M:%S",
    "MM/DD/YYYY HH:MM:SS": "%m/%d/%Y %H:%M:%S",
    "DD/MM/YYYY HH:MM:SS": "%d/%m/%Y %H:%M:%S",
    "DD-MM-YYYY HH:MM:SS": "%d-%m-%Y %H:%M:%S",
    "YYYY-MM-DD HH:MM:SS": "%Y-%m-%d %H:%M:%S",
    "MM-DD-YYYY HH:MM:SS": "%m-%d-%Y %H:%M:%S",
}


class DataHandler:
    def __init__(self):
        self.excel_file = None
        self.gdf = None
        self.x_column = None
        self.y_column = None
        self.crs_key = None

    def read_excel_file(self, path: str) -> None:
        """
        Função que lê uma pasta de trabalho do Excel/OpenDocument e a armazena como um objeto pandas.ExcelFile no
        atributo "excel_file" da classe.
        :param path: Caminho do arquivo a ser lido.
        :return: Nada.
        """
        self.excel_file = pandas.ExcelFile(path)

    def read_excel_sheet(self, sheet: str | int) -> None:
        """
        Função que lê uma planilha contida no arquivo do atributo "excel_file" e armazena os dados como um
        geopandas.GeoDataFrame no atributo "gdf" da classe. Automaticamente chama a função process_data para tratar os
        dados.
        :param sheet: O nome (str) ou índice (int) da planilha a ser lida.
        :return: Nada.
        """
        df = self.process_data(self.excel_file.parse(sheet_name=sheet))
        self.gdf = geopandas.GeoDataFrame(df)

    def read_csv_file(self, path: str, decimal: str = ',') -> None:
        """
        Função que lê um arquivo CSV, identifica o delimitador de células e armazena os dados como um
        geopandas.GeoDataFrame no atributo "gdf" da classe. Automaticamente chama a função process_data para tratar os
        dados.
        :param path:  Caminho do arquivo a ser lido.
        :param decimal: O separador decimal usado no arquivo. O padrão é ',' (vírgula).
        :return: Nada.
        """
        sniffer = csv.Sniffer()
        data = open(path, "r").read(4096)
        sep = str(sniffer.sniff(data).delimiter)
        df = self.process_data(pandas.read_csv(path, delimiter=sep, decimal=decimal))
        self.gdf = geopandas.GeoDataFrame(df)

    @staticmethod
    def process_data(df: pandas.DataFrame) -> pandas.DataFrame:
        """
        Função que recebe um pandas.DataFrame e 1) Converte todos os rótulos de colunas para strings, 2) Descarta
        colunas sem rótulo/cabeçalho e 3) Descarta linhas completamente vazias. Também levanta um erro caso não haja
        nenhuma linha preenchida na planilha (com exceção dos cabeçalhos).
        :param df: O DataFrame a ser tratado.
        :return: O DataFrame após o tratamento.
        """
        # Converte os nomes das colunas para string
        df.columns = df.columns.astype(str)
        # Descarta colunas sem nome
        df = df.drop([col for col in df.columns if 'Unnamed' in col], axis='columns')
        # Descarta linhas vazias
        df = df.dropna(how='all', axis='index')
        # Verifica se existem linhas preenchidas no arquivo
        if len(df.index) <= 0:
            raise Exception('A tabela selecionada está vazia ou contém apenas cabeçalhos.')
        return df

    def filter_coordinates_columns(self, crs_key: str) -> (list[str], list[str]):
        """
        Encontra as colunas válidas para coordenadas no GeoDataFrame contido no atributo "gdf" da classe e retorna uma
        lista de colunas válidas para x (longitude/easting) e y (latitude/northing). São consideradas colunas válidas
        aquelas que podem ser convertidas para float e cujos valores estão dentro dos limites esperados para as
        coordenadas do SRC.
        :param crs_key: A chave para o dicionário de SRCs (CRS_DICT), no formato "name (auth:code)". Ex: "SIRGAS 2000 (EPSG:4674)".
        :return: Listas contendo os rótulos das colunas válidas para x e y, respectivamente.
        """
        crs = pyproj.CRS.from_authority(CRS_DICT[crs_key]["auth_name"], CRS_DICT[crs_key]["code"])

        if str(CRS_DICT[crs_key]["type"]) == "PJType.GEOGRAPHIC_2D_CRS":
            x_min, y_min, x_max, y_max = crs.area_of_use.bounds
        else:
            transformer = pyproj.Transformer.from_crs(crs.geodetic_crs, crs, always_xy=True)
            x_min, y_min, x_max, y_max = transformer.transform_bounds(*crs.area_of_use.bounds)

        y_columns, x_columns = [], []

        for col in self.gdf.columns:
            try:
                self.gdf[col] = self.gdf[col].replace(",", ".", regex=True).astype(float)
                if self.gdf[col].dropna().between(y_min, y_max).all():
                    y_columns.append(col)
                if self.gdf[col].dropna().between(x_min, x_max).all():
                    x_columns.append(col)
            except (ValueError, TypeError):
                continue

        return x_columns, y_columns

    @staticmethod
    def search_coordinates_column_by_name(axis: str, crs_type: str, column_options: list[str]) -> str | None:
        """
        Função que seleciona uma coluna que provavelmente contém coordenadas com base no nome.
        :param axis: O eixo das coordenadas ("y": latitude/northing, "x": longitude/easting).
        :param crs_type: O tipo de SRC ("PJType.GEOGRAPHIC_2D_CRS": geográfico, "PJType.PROJECTED_CRS": projetado).
        :param column_options: Uma lista contendo os rótulos das colunas a serem consideradas.
        :return: O rótulo da coluna que provavelmente contém as coordenadas (str) ou None, se nenhuma coluna provável for encontrada.
        """
        options = {
            ("y", "PJType.GEOGRAPHIC_2D_CRS"): ("latitude", "lat", "y"),
            ("y", "PJType.PROJECTED_CRS"): ("northing", "utm_n", "utmn", "n", "utmn (m)", "utm_n (m)", "y"),
            ("x", "PJType.GEOGRAPHIC_2D_CRS"): ("longitude", "lon", "x"),
            ("x", "PJType.PROJECTED_CRS"): ("easting", "utm_e", "utme", "e", "utme (m)", "utm_e (m)", "x")
        }

        common_names = options[(axis, crs_type)]

        return next((col for col in column_options if str(col).lower() in common_names), None)

    def set_geodataframe_geometry(self, crs_key: str, x_column: str, y_column: str) -> None:
        """
        Define a geometria e o crs do GeoDataFrame contido no adributo "gdf" da classe. Também define os atributos
        "crs_key", "x_column" e "y_column" da classe com base nos parâmetros dados.
        :param crs_key: A chave para o dicionário de SRCs (CRS_DICT), no formato "name (auth:code)". Ex: "SIRGAS 2000 (EPSG:4674)".
        :param x_column: O rótulo da coluna que contém as coordenadas do eixo X.
        :param y_column: O rótulo da coluna que contém as coordenadas do eixo Y.
        """
        crs = pyproj.CRS.from_authority(CRS_DICT[crs_key]["auth_name"], CRS_DICT[crs_key]["code"])
        geometry = geopandas.points_from_xy(self.gdf[x_column], self.gdf[y_column], crs=crs)

        self.gdf = geopandas.GeoDataFrame(self.gdf, geometry=geometry, crs=crs)

        self.x_column, self.y_column = x_column, y_column
        self.crs_key = crs_key

    def merge_sheets(self, merge_column: str) -> (list[str], list[str]):
        """
        Mescla múltiplas abas de uma pasta de trabalho do Excel/OpenDocument armazenado no atributo "excel_file" da
        classe, com base em uma coluna de ID. Armazena os novos dados no atributo "gdf", usando os atributos
        "x_column", "y_column" e "crs" para construir a geometria e definir o SRC. Planilhas que não contenham a coluna
        merge_column são ignoradas.
        :param merge_column: A coluna identificadora.
        :return: Listas contendo os rótulos das colunas que foram e não foram incluídas na mesclagem, respectivamente.
        """
        sheets_to_merge, sheets_to_skip = [], []
        sheet_dfs, merge_column_dtypes = [], []

        # Itera pelo ExcelFile, convertendo as planilhas para DFs, e verifica se cada uma contém a coluna de mescla
        for s in self.excel_file.sheet_names:
            sheet_df = self.excel_file.parse(sheet_name=s)

            if merge_column in sheet_df.columns:
                sheets_to_merge.append(s)
                sheet_dfs.append(self.process_data(sheet_df))
                merge_column_dtypes.append(sheet_df[merge_column].dtype)
            else:
                sheets_to_skip.append(s)

        # Verifica se a coluna de mescla tem o mesmo dtype em todas as abas. Se não tiver, converte todas para string
        if len(set(merge_column_dtypes)) > 1:
            for s in sheet_dfs:
                s[merge_column] = s[merge_column].astype(str)

        # Mescla as abas com base na coluna de mescla selecionada pelo usuário
        df = sheet_dfs[0]
        for i in range(1, len(sheet_dfs)):
            df = pandas.merge(df, sheet_dfs[i], how='outer', on=merge_column)

        # Restaura a ordem correta das colunas
        cols = df.columns.to_list()
        cols.remove(merge_column)
        columns = [merge_column] + cols
        df = df[columns]

        self.gdf = geopandas.GeoDataFrame(df, geometry=self.gdf.geometry, crs=self.gdf.crs)

        return sheets_to_merge, sheets_to_skip

    def change_column_dtype(self, column: str, target_dtype_key: str, **kwargs) -> None:
        """
        Muda o tipo de dado de uma coluna.
        :param column: O nome da coluna.
        :param target_dtype_key: O tipo de dado de destino (String, Integer, Float, Boolean ou Datetime).
        :kwarg true_key: O valor encontrado na coluna a ser considerado como True (necessário apenas ao converter para Boolean). Ex: "Verdadeiro".
        :kwarg false_key: O valor encontrado na coluna a ser considerado como False (necessário apenas ao converter para Boolean). Ex: "Falso".
        :kwarg datetime_format: O formato de data e hora (necessário apenas ao converter para Datetime)
        :return: Nada
        """
        if target_dtype_key == "Boolean":
            true, false = kwargs.get("true_key", "Sim"), kwargs.get("false_key", "Não")
            if not self.gdf[column].astype(str).isin((true, false)).all():
                raise ValueError(f"A coluna deve conter apenas os valores indicados para verdadeiro e falso ({true} e {false}).")
            self.gdf[column] = self.gdf[column].astype(str).map({true: True, false: False}).astype(bool)
        elif target_dtype_key == "Datetime":
            datetime_format = kwargs.get("datetime_format", "DD-MM-YYYY")
            self.gdf[column] = pandas.to_datetime(self.gdf[column], format=DATETIME_FORMATS[datetime_format], errors="raise")
        else:
            target_dtype = DTYPES_DICT[target_dtype_key]["pandas_dtypes"][0]
            self.gdf[column] = self.gdf[column].astype(target_dtype, errors="raise")

    def reproject_geodataframe(self, target_crs_key: str) -> None:
        """
        Reprojeta o GeoDataFrame para um SRC de destino.
        :param target_crs_key: A chave para o dicionário de SRCs (CRS_DICT) do SRC de destino, no formato "name (auth:code)". Ex: "SIRGAS 2000 (EPSG:4674)".
        :return: Nada
        """
        target_crs = pyproj.CRS.from_authority(CRS_DICT[target_crs_key]["auth_name"], CRS_DICT[target_crs_key]["code"])
        self.gdf = self.gdf.to_crs(crs=target_crs)

    def save_to_geospatial_file(self, path: str, layer_name: str = None):
        """
        Exporta o GeoDataFrame aramazenado no atributo "gdf" da classe para um arquivo Shapefile, GeoJson ou Geopackage.
        :param path: Caminho do arquivo de saída.
        :param layer_name: Nome da camada (para arquivos geopackage).
        :return: Nada
        """
        unsupported_dtypes = ("category", "timedelta64[ns]")

        for column in self.gdf.columns:
            if self.gdf[column].dtype in unsupported_dtypes:
                self.gdf[column] = self.gdf[column].astype(str)

        self.gdf.to_file(path, layer_name=layer_name)


def get_dtype_key(value):
    for dt_key, inner_dict in DTYPES_DICT.items():
        if value in inner_dict["pandas_dtypes"]:
            return dt_key
    return None

# TESTES ||--*--||--*--||--*--||--*--||--*--||--*--||--*--||--*--||--*--||--*--||--*--||--*--||--*--||--*--||--*--||--*-
if __name__ == "__main__":
    ic.configureOutput(prefix="LOG | ", includeContext=False)
    warnings.simplefilter("ignore", category=UserWarning)

    handler = DataHandler()

    input_file = "exemplo_preenchido_2.xlsx"

    handler.read_excel_file(input_file)
    handler.read_excel_sheet(0)
    conversion = handler.change_column_dtype("Easting", "uint8")
    ic(handler.gdf["Easting"])
