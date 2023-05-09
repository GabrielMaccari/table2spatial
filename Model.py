# -*- coding: utf-8 -*-
"""
@author: Gabriel Maccari
"""
import pandas
import geopandas
import pyproj

DTYPE_DICT = {
    "String": {
        "pandas_type": "object",
        "icon": "icons/string.png",
    },
    "Float": {
        "pandas_type": "float64",
        "icon": "icons/float.png",
    },
    "Integer": {
        "pandas_type": "int64",
        "icon": "icons/integer.png",
    },
    "Boolean": {
        "pandas_type": "bool",
        "icon": "icons/boolean.png",
    },
    "Datetime": {
        "pandas_type": "datetime64[ns]",
        "icon": "icons/datetime.png",
    },
    "Timedelta": {
        "pandas_type": "timedelta64[ns]",
        "icon": "icons/timedelta.png",
    },
    "Category": {
        "pandas_type": "category",
        "icon": "icons/category.png",
    }
}

crs_dict = {}
for crs in pyproj.database.query_crs_info(pj_types=["GEOGRAPHIC_2D_CRS", "PROJECTED_CRS"]):
    key = f"{crs.name} ({crs.auth_name}:{crs.code})"
    crs_dict[key] = {
        "name": crs.name,
        "auth_name": crs.auth_name,
        "code": crs.code,
        "type": crs.type,
        "area_of_use": crs.area_of_use
    }


class GeographicTable:
    def __init__(self, path: str = None, excel_file: pandas.ExcelFile = None, df: pandas.DataFrame = None,
                 crs: str = None, y_column: str = None, x_column: str = None, gdf: geopandas.GeoDataFrame = None):
        self.path = path
        self.excel_file = excel_file
        self.df = df

        self.crs = crs
        self.y_column = y_column
        self.x_column = x_column
        self.gdf = gdf
