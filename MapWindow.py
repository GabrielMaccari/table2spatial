# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 13:40:59 2022

@author: Gabriel Maccari
"""

from os import getcwd
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtGui import QIcon
from PyQt6.QtWebEngineWidgets import QWebEngineView #pip install PyQt6-WebEngine
import folium
from folium.plugins import MeasureControl, MousePosition, Geocoder
from io import BytesIO
#from geopandas import GeoDataFrame

class MapWindow(QMainWindow):
    def __init__(self, GDF, parent=None):
        
        super(MapWindow, self).__init__(parent)
        
        self.folder = getcwd()
        self.GDF = GDF
 
        self.setWindowTitle("Map view")
        self.setWindowIcon(QIcon('icons/windowIcon.ico'))
        
        m = self.build_webmap()
        
        data = BytesIO()
        m.save(data, close_file=False)
        
        webView = QWebEngineView(self)
        webView.setHtml(data.getvalue().decode())
        webView.setGeometry(0, 0, 700, 500)
        
        self.setMinimumWidth(700)
        self.setMaximumWidth(700)
        self.setMinimumHeight(500)
        self.setMaximumHeight(500)
        
    def build_webmap(self):
        GDF = self.GDF.to_crs(4326)
        fields = GDF.columns.to_list()
        dtypes = GDF.dtypes.to_list()
        
        for i in range(len(dtypes)):
            if dtypes[i]=='Timestamp' or dtypes[i]=='<M8[ns]' or dtypes[i]=='datetime64':
                GDF[fields[i]] = GDF[fields[i]].astype(str, errors='ignore')
        
        yx = [GDF.geometry.y[0], GDF.geometry.x[0]]
        
        webmap = folium.Map(location=yx, zoom_start = 12, minZoom = 5, 
                            control_scale = True, zoomControl=True, 
                            tiles='openstreetmap', attributionControl=True)
        
        folium.raster_layers.WmsTileLayer('https://www.google.cn/maps/vt?lyrs=s@189&gl=cn&x={x}&y={y}&z={z}',
                                          'Google Satellite', name='Google Satellite', overlay=False).add_to(webmap)
        
        f = fields[0:-1] if len(fields)<=11 else fields[0:11]
        
        folium.GeoJson(
            GDF.to_json(),
            name='Pontos',
            show=True,
            tooltip=folium.features.GeoJsonTooltip(
                fields=[fields[0]],
                labels=False
            ),
            popup=folium.features.GeoJsonPopup(
                fields=f,
                aliases=f
            )
        ).add_to(webmap)
        
        folium.map.LayerControl().add_to(webmap)
        MeasureControl(position='topright', 
                                       primary_length_unit='meters', 
                                       secondary_length_unit='kilometers', 
                                       primary_area_unit='sqmeters', 
                                       secondary_area_unit='hectares').add_to(webmap)
        Geocoder(position='topright', collapsed=True).add_to(webmap)
        MousePosition(position='bottomright', separator=' / ').add_to(webmap)
        
        return webmap