import pandas
import pyproj
from csv import Sniffer
from collections import Counter
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import sys

dtype_dict = {
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
        "pandas_type": "timedelta[ns]",
        "icon": "icons/timedelta.png",
    },
    "Category": {
        "pandas_type": "category",
        "icon": "icons/category.png",
    }
}

crs_dict = {}
for crs in pyproj.database.query_crs_info(
        pj_types=["GEOGRAPHIC_2D_CRS", "PROJECTED_CRS"]):
    key = f"{crs.name} ({crs.auth_name}:{crs.code})"
    crs_dict[key] = {
        "name": crs.name,
        "auth_name": crs.auth_name,
        "code": crs.code,
        "type": crs.type,
        "area_of_use": crs.area_of_use
    }

class GeographicTable():

    def __init__(self):
        self.path = None
        self.excel_file = None
        self.multiple_sheets = False
        self.df = None

        self.crs = None
        self.coordinate_columns = [None, None]
        self.gdf = None
