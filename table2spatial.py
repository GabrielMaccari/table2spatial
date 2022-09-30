# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 10:15:33 2022

@author: Gabriel Maccari
"""

from sys import argv as sys_argv
from sys import exit as sys_exit
from os import getcwd as os_getcwd
from PyQt6.QtWidgets import QMainWindow, QApplication, QLabel, QCheckBox, QComboBox, QPushButton, QFileDialog, QMessageBox, QScrollArea, QGroupBox, QGridLayout, QInputDialog
from PyQt6.QtGui import QIcon, QFont
from pyproj.database import query_crs_info
from numpy import nan
import pandas
import geopandas
from MapWindow import MapWindow

class table2spatialApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('table2spatial')
        self.setWindowIcon(QIcon('icons/windowIcon.ico'))
        
        #Variáveis
        self.folder = os_getcwd()
        self.inFile = None
        self.DF = None
        self.columns = None
        self.dTypes = None
        self.mergeColumn = None
        self.CRS = 'SIRGAS 2000'
        self.N_column = None
        self.E_column = None
        
        self.dTypeDict = {'String':'object','Integer':'int64','Float':'float64','Datetime':'datetime64','Boolean':'bool','Timestamp':'<M8[ns]'}
        
        #Interface
        self.section1 = []
        
        x, y, h, w = 5, 5, 22, 400
        self.file_lbl = QLabel('Selecione um arquivo .xlsx.', self)
        self.file_lbl.setGeometry(x, y, 310, h)
        self.file_btn = QPushButton('Selecionar', self)
        self.file_btn.setGeometry(315, y-1, 80, h+2)
        self.file_btn.clicked.connect(self.open_file)
        
        self.section1.append(self.file_lbl)
        self.section1.append(self.file_btn)
        
        self.section2 = []
        
        y, h = y+h+5, 22
        self.merge_chk = QCheckBox('Mesclar abas com a coluna:', self)
        self.merge_chk.setGeometry(x, y, 175, h)
        self.merge_chk.clicked.connect(self.enable_merge)
        self.merge_chk.setEnabled(False)
        self.mergeColumn_cmb = QComboBox(self)
        self.mergeColumn_cmb.setGeometry(175, y, 187, h)
        self.mergeColumn_cmb.setEnabled(False)
        self.merge_btn = QPushButton('OK', self)
        self.merge_btn.setGeometry(365, y-1, 30, h+2)
        self.merge_btn.clicked.connect(self.merge_sheets)
        self.merge_btn.setEnabled(False)
        
        self.section2.append(self.merge_chk)
        self.section2.append(self.mergeColumn_cmb)
        self.section2.append(self.merge_btn)
        
        self.section3 = []
        
        y, h = y+h+5, 350
        self.columnsList_lyt = QGridLayout()
        self.columnsList_lyt.setEnabled(False)
        self.columnsList_lyt.setVerticalSpacing(3)
        self.columnsList_lyt.setColumnMinimumWidth(1, 145)
        self.columnsList_lyt.setColumnMinimumWidth(2, 85)
        self.columnsList_lyt.setColumnMinimumWidth(3, 70)
        self.columnsList_box = QGroupBox('Colunas do DataFrame')
        self.columnsList_box.setLayout(self.columnsList_lyt)
        self.columnsList_box.setEnabled(False)
        self.columnsList_scl = QScrollArea(self)
        self.columnsList_scl.setWidget(self.columnsList_box)
        self.columnsList_scl.setWidgetResizable(True)
        self.columnsList_scl.setFixedHeight(h)
        self.columnsList_scl.setGeometry(x, y, w-10, h)
        self.columnsList_scl.setEnabled(False)
        
        self.section3.append(self.columnsList_lyt)
        self.section3.append(self.columnsList_box)
        self.section3.append(self.columnsList_scl)
        
        self.section4 = []
        
        y, h = y+h+5, 22
        self.CRS_lbl = QLabel('Sistema de referência de coordenadas:', self)
        self.CRS_lbl.setGeometry(x, y, w-10, h)
        self.CRS_lbl.setEnabled(False)
        
        y, h = y+h, 22
        self.CRS_type_cmb = QComboBox(self)
        self.CRS_type_cmb.setGeometry(x, y, 85, h)
        self.CRS_type_cmb.addItems(['Projetado','Geográfico'])
        self.CRS_type_cmb.currentTextChanged.connect(lambda: self.get_CRS_list(self.CRS_type_cmb.currentText()))
        self.CRS_type_cmb.setEnabled(False)
        self.CRS_cmb = QComboBox(self)
        self.CRS_cmb.setGeometry(100, y, 290, h)
        self.get_CRS_list(self.CRS_type_cmb.currentText())
        self.CRS_cmb.currentTextChanged.connect(self.update_coordinates_columns)
        self.CRS_cmb.setEnabled(False)
        
        y, h = y+h, 22
        self.N_lbl = QLabel('Latitude/Northing:', self)
        self.N_lbl.setGeometry(x, y, 193, h)
        self.N_lbl.setEnabled(False)
        self.E_lbl = QLabel('Longitude/Easting:', self)
        self.E_lbl.setGeometry(201, y, 193, h)
        self.E_lbl.setEnabled(False)
        
        y, h = y+h, 22
        self.N_cmb = QComboBox(self)
        self.N_cmb.setGeometry(x, y, 193, h)
        self.N_cmb.setEnabled(False)
        self.E_cmb = QComboBox(self)
        self.E_cmb.setGeometry(201, y, 193, h)
        self.E_cmb.setEnabled(False)
        
        y, h = y+h+5, 30
        self.export_btn = QPushButton('Exportar', self)
        self.export_btn.setGeometry(x, y, w-10, h)
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(self.export_file)
        
        self.section4.append(self.CRS_lbl)
        self.section4.append(self.CRS_type_cmb)
        self.section4.append(self.CRS_cmb)
        self.section4.append(self.N_lbl)
        self.section4.append(self.E_lbl)
        self.section4.append(self.N_cmb)
        self.section4.append(self.E_cmb)
        self.section4.append(self.export_btn)
        
        y, h = y+h+3, 15
        self.copyrightLabel = QLabel('© 2022 Gabriel Maccari <gabriel.maccari@hotmail.com>', self)
        self.copyrightLabel.setGeometry(x, y, w-10, h)
        self.copyrightLabel.setFont(QFont('Sans Serif', 8))
        
        self.setMaximumWidth(w)
        self.setMinimumWidth(w)
        self.setMaximumHeight(y+h+5)
        self.setMinimumHeight(y+h+5)

    def open_file(self):
        try:
            self.inFile = QFileDialog.getOpenFileName(self, caption='Selecione uma tabela contendo os dados de entrada.', directory=self.folder, filter='Formatos suportados (*.xlsx *.xlsm *.csv *.ods);;Pasta de Trabalho do Excel (*.xlsx);;Pasta de Trabalho Habilitada para Macro do Excel (*.xlsm);;CSV (*.csv);; OpenDocument Spreadsheet (*.ods)')
        except Exception as e:
            self.file_lbl.setText(str(e))
            self.file_lbl.setStyleSheet('QLabel {color: red}')
            self.enable_widgets([1,2,3], False)
            self.mergeColumn_cmb.clear()
            self.clear_columns_list()
        
        if self.inFile[0]!='':
            try:
                if self.inFile[0].endswith('.csv'):
                    try:
                        self.DF = pandas.read_csv(self.inFile[0])
                        msg = QMessageBox(parent=self, text='Você selecionou um arquivo de texto separado por delimitador (CSV). Para um funcionamento adequado da ferramenta, certifique-se de que o separador de campo utilizado no arquivo não está presente no conteúdo das células e não coincide com o separador decimal.')
                        msg.setWindowTitle('Atenção')
                        msg.setIcon(QMessageBox.Icon.Warning)
                        msg.exec()
                    except Exception as e:
                        msg = QMessageBox(parent=self, text='Não foi possível realizar a leitura do arquivo CSV. Certifique-se de que o separador de campo utilizado no arquivo não está presente no conteúdo das células e não coincide com o separador decimal.\n\n'+str(e))
                        msg.setWindowTitle('Erro')
                        msg.setIcon(QMessageBox.Icon.Critical)
                        msg.exec()
                        return
                else:
                    eng=('odf' if self.inFile[0].endswith('.ods') else 'openpyxl')
                    file = pandas.ExcelFile(self.inFile[0], engine=eng)
                    if len(file.sheet_names) > 1:
                        self.enable_widgets([1], True)
                        msg = QMessageBox(parent=self, text='O arquivo selecionado contém múltiplas abas. Caso deseje mesclar todas as abas em uma única planilha, marque a caixa "Mesclar abas com a coluna" na interface da ferramenta e selecione uma coluna em comum para realizar a mesclagem.')
                        msg.setWindowTitle('Mesclar abas')
                        msg.exec()
                    else:
                        self.enable_widgets([1], False)
                    self.DF = pandas.read_excel(file, engine=eng)
                    self.DF.columns = self.DF.columns.astype(str)
                    remove_cols = [col for col in self.DF.columns if 'Unnamed' in col]
                    self.DF.drop(remove_cols, axis='columns', inplace=True)
                    self.DF.dropna(how='all', axis='index', inplace=True)
                    self.DF.replace(r'^\s*$', nan, inplace=True, regex=True)
                
                self.columns = self.DF.columns.to_list()
                self.dTypes = self.DF.dtypes.to_list()
            except Exception as e:
                msg = QMessageBox(parent=self, text='Não foi possível abrir o arquivo.\n\n'+str(e))
                msg.setWindowTitle('Erro')
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.exec()
            
            self.mergeColumn_cmb.clear()
            self.mergeColumn_cmb.addItems(self.columns)
            self.update_columns_list()
            self.enable_widgets([2, 3], True)  
            
            self.file_lbl.setText('Arquivo carregado com sucesso.')
            self.file_lbl.setStyleSheet('QLabel {color: green}')
        else:
            self.enable_widgets([1,2,3], False)
    
    def merge_sheets(self):
        self.mergeColumn = self.mergeColumn_cmb.currentText()
        eng=('odf' if self.inFile[0].endswith('.ods') else 'openpyxl')
        file = pandas.ExcelFile(self.inFile[0], engine=eng)
        
        n = len(file.sheet_names)
        
        #Verifica quais abas do arquivo possuem a coluna de mescla
        sheets_to_merge, sheets_to_ignore = [], []
        allSheets = True
        for i in range(0, n):
            if self.mergeColumn in file.parse(i).columns.to_list():
                sheets_to_merge.append(i)
            else:
                sheets_to_ignore.append(file.sheet_names[i])
                allSheets = False
        
        #Notifica o usuário caso alguma aba seja deixada de fora da mesclagem
        if not allSheets:
            msg = QMessageBox(parent=self, text='As seguintes abas não possuem a coluna "%s", e portanto não serão adicionadas ao dataframe:\n%s' % (self.mergeColumn,str(sheets_to_ignore)))
            msg.setWindowTitle('Atenção')
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.exec()
            
        try:
            #Lê todas as abas do arquivo e armazena em uma lista. Armazena também os dtypes das colunas de merge de cada aba
            sheets, merge_dts = [], []
            for i in range(0, n):
                if i in sheets_to_merge:
                    s = pandas.read_excel(file, sheet_name=i)
                    remove_cols= [col for col in s.columns if 'Unnamed' in col]
                    s.drop(remove_cols, axis='columns', inplace=True)
                    s.dropna(how='all', axis='index', inplace=True)
                    sheets.append(s)
                    merge_dts.append(s[self.mergeColumn].dtype)
    
            #Verifica se a coluna de mescla tem o mesmo dtype em todas as abas. Se não tiver, converte todas para string
            if not merge_dts.count(merge_dts[0]) == len(merge_dts):
                for s in sheets:
                    s[self.mergeColumn] = s[self.mergeColumn].astype(str)
                    
            #Mescla todas as abas com base na coluna de mescla selecionada pelo usuário
            df = sheets[0]
            for i in range(1, len(sheets)):
                df = pandas.merge(df, sheets[i], how='outer', on=self.mergeColumn)
                
            #self.DF.dropna(how='all', axis='columns', inplace=True)
      
            cols = df.columns.to_list()
            cols.remove(self.mergeColumn)
            columns = [self.mergeColumn] + cols
            
            self.DF = df[columns]
            self.DF.sort_values(by=[self.mergeColumn], inplace=True)
            
            self.columns = self.DF.columns.to_list()
            self.dTypes = self.DF.dtypes.to_list()
            self.update_columns_list()
        except Exception as e:
            msg = QMessageBox(parent=self, text='Não foi possível mesclar as abas com a coluna especificada.\n\n'+str(e))
            msg.setWindowTitle('Erro')
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.exec()
    
    def enable_widgets(self, to_enable, state):
        sections = [self.section1, self.section2, self.section3, self.section4]
        for s in range(len(sections)):
            if s in to_enable:
                for widget in sections[s]:
                    if widget == self.mergeColumn_cmb or widget == self.merge_btn:
                        if state==True and self.merge_chk.isChecked():
                            widget.setEnabled(state)
                    else:
                        widget.setEnabled(state)
    
    def enable_merge(self):
        state = self.merge_chk.isChecked()
        self.mergeColumn_cmb.setEnabled(state)
        self.merge_btn.setEnabled(state)
    
    def update_columns_list(self):
        self.clear_columns_list()
        
        self.columnLabels, self.dTypeCombos, self.statusLabels = [], [], []
        x, y, w1, w2, w3, h = 0, 15, 145, 85, 65, 20
        for i in range(len(self.columns)):
            c, dt = self.columns[i], self.dTypes[i]
            label = QLabel(c)
            label.setGeometry(x, y, w1, h)
            combo = QComboBox()
            combo.addItems(self.dTypeDict)
            combo.setGeometry(w1, y, w2, h)
            combo.setCurrentText(list(self.dTypeDict.keys())[list(self.dTypeDict.values()).index(dt)])
            combo.currentTextChanged.connect(lambda wontWorkWhitoutThis, x=i: self.switch_dType(x))
            status = QLabel('OK')
            status.setGeometry(w2+5, y, w3, h)
            
            self.columnLabels.append(label)
            self.dTypeCombos.append(combo)
            self.statusLabels.append(status)

            if i+1==len(self.columns):
                self.switch_dType(i)
            else:
                self.switch_dType(i, False)
            
            for j in range(1,4):
                if j==1:
                    self.columnsList_lyt.addWidget(self.columnLabels[i], i, j)
                elif j==2:
                    self.columnsList_lyt.addWidget(self.dTypeCombos[i], i, j)
                else:
                    self.columnsList_lyt.addWidget(self.statusLabels[i], i, j)
            
            y+=22
            self.update_coordinates_columns()
    
    def switch_dType(self, i, update_NS_columns=True):
        c = self.columns[i]
        dt = self.dTypeCombos[i].currentText()
        target_dType = self.dTypeDict[dt]
        try:
            if self.dTypes[i]=='<M8[ns]' and target_dType=='object':
                #self.DF[c] = self.DF[c].dt.strftime('%d/%m/%Y')
                self.DF[c] = self.DF[c].astype(str)
            else:
                self.DF[c] = self.DF[c].astype(target_dType, errors='raise')
            self.dTypes[i] = self.DF[c].dtype
            self.statusLabels[i].setStyleSheet('QLabel {color: green}')
            if self.DF[self.columns[i]].dropna(inplace=False).empty:
                self.statusLabels[i].setText('Vazia')
            else:
                self.statusLabels[i].setText('OK')
        except Exception as e:
            self.statusLabels[i].setText('Fora de formato')
            self.statusLabels[i].setStyleSheet('QLabel {color: red}')
            msg = QMessageBox(parent=self, text='Os dados da coluna "%s" não podem ser convertidos para o formato %s.\n\nMotivo: %s' % (self.columns[i], self.dTypeCombos[i].currentText(), str(e)))
            msg.setWindowTitle('Atenção')
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.exec()

        if update_NS_columns:
            self.update_coordinates_columns()
    
    def clear_columns_list(self):
        while self.columnsList_lyt.count():
            child = self.columnsList_lyt.takeAt(0)
            if child.widget():
              child.widget().deleteLater()
    
    def get_CRS_list(self, CRS_type):
        if CRS_type == 'Geográfico':
            CRS_data = query_crs_info(pj_types='GEOGRAPHIC_2D_CRS')
            default_CRS = 'SIRGAS 2000'
        elif CRS_type == 'Projetado':
            CRS_data = query_crs_info(pj_types='PROJECTED_CRS')
            default_CRS = 'SIRGAS 2000 / UTM zone 22S'
        
        self.CRS_dict = {}
        for info in CRS_data:
            if info.auth_name=='EPSG':
                self.CRS_dict[info.name] = int(info.code)
        
        self.CRS_cmb.clear()
        self.CRS_cmb.addItems(sorted(self.CRS_dict.keys()))
        self.CRS_cmb.setCurrentText(default_CRS)
    
    def update_coordinates_columns(self):
        CRS_type = self.CRS_type_cmb.currentText()
        
        if CRS_type=='Geográfico':
            allowed_dTypes = ['float64']
            y_range_min, y_range_max = -90, 90
            x_range_min, x_range_max = -180, 180
        elif CRS_type=='Projetado':
            allowed_dTypes = ['float64', 'int64']
            y_range_min, y_range_max = 1099000, 10000000
            x_range_min, x_range_max = 165000, 835000
        
        y_columns_list, x_columns_list = [], []
        for i in range(len(self.columns)):
            if self.dTypes[i] in allowed_dTypes:
                c = self.columns[i]
                if self.DF[c].dropna().between(y_range_min, y_range_max).all() and not self.DF[c].dropna().empty:
                    y_columns_list.append(c)
                if self.DF[c].dropna().between(x_range_min, x_range_max).all() and not self.DF[c].dropna().empty:
                    x_columns_list.append(c)
        
        self.N_cmb.clear()
        self.E_cmb.clear()
        self.N_cmb.addItems(y_columns_list)
        self.E_cmb.addItems(x_columns_list)
    
    def export_file(self):
        self.CRS = self.CRS_cmb.currentText()
        self.N_column = self.N_cmb.currentText()
        self.E_column = self.E_cmb.currentText()
        
        if self.N_column=='' or self.E_column=='':
            file_options = 'Pasta de Trabalho do Excel (*.xlsx);;CSV (*.csv)'
            output_type = 'DataFrame'
        else:
            file_options = 'Geopackage (pontos) (*.gpkg);;ESRI Shapefile (pontos) (*.shp);;GeoJSON (*.json);; Pasta de Trabalho do Excel (*.xlsx);;CSV (*.csv)'
            output_type = 'GeoDataFrame'
            EPSG = self.CRS_dict[self.CRS]
        
        self.outFile = QFileDialog.getSaveFileName(self, 'Salvar DataFrame', self.folder, file_options)
        path = self.outFile[0]
        
        if path!='':
            try:
                if output_type == 'DataFrame' or path.endswith('.xlsx') or path.endswith('.csv'):
                    if path.endswith('.xlsx'):
                        self.DF.to_excel(path, index=False)
                    if path.endswith('.csv'):
                        self.DF.to_csv(path, sep=';', encoding='utf-8', decimal=',', index=False)
                    
                    msg = QMessageBox(parent=self, text='DataFrame exportado com sucesso!')
                    msg.setWindowTitle('Sucesso')
                    msg.exec()
                    
                else:
                    GDF = geopandas.GeoDataFrame(self.DF, geometry=geopandas.points_from_xy(self.DF[self.E_column], self.DF[self.N_column]))
                    GDF.set_crs(epsg=EPSG, inplace=True)
                    
                    if path.endswith('.shp'):
                        GDF.to_file(path)
                        ok = True
                    elif path.endswith('.gpkg'):
                        layerName, ok = QInputDialog.getText(self, 'Nome da camada', 'Nome para a camada do GeoPackage:', text='layer')
                        if ok:
                            GDF.to_file(path, driver='GPKG', layer=layerName)
                    elif path.endswith('.json'):
                        GDF.to_file(path, driver='GeoJSON')
                        ok = True
                        
                    if ok and len(GDF)<=150:
                        dlg = QMessageBox(QMessageBox.Icon.Question, 'Sucesso',
                                          'DataFrame exportado com sucesso! Deseja visualizar uma prévia dos resultados?',
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                          self)
                        reply = dlg.exec()
                        
                        if reply == QMessageBox.StandardButton.Yes:
                            try:
                                new_GDF = geopandas.read_file(path)
                                new_GDF.set_crs(epsg=EPSG, inplace=True, allow_override=True)
                                mapView = MapWindow(new_GDF, self)
                                mapView.show()
                            except Exception as e:
                                msg = QMessageBox(parent=self, text='Não foi possível plotar os dados no mapa.\n\n%s' % (str(e)))
                                msg.setWindowTitle('Erro')
                                msg.setIcon(QMessageBox.Icon.Critical)
                                msg.exec()
                    else:
                        msg = QMessageBox(parent=self, text='DataFrame exportado com sucesso!')
                        msg.setWindowTitle('Sucesso')
                        msg.exec()
                
            except Exception as e:
                if str(e)=="ESRI Shapefile does not support datetime fields":
                    msg = QMessageBox(parent=self, text='O formato shapefile não suporta campos de data e hora. Converta as colunas do tipo "Timestamp" e "Datetime" para "String" e tente novamente.')
                elif str(e)=="Invalid field type <class 'datetime.datetime'>":
                    msg = QMessageBox(parent=self, text='Há um campo de data e hora com formato inválido no DataFrame. Converta as colunas de data/hora para "Datetime" ou "Timestamp" e tente novamente.')
                else:
                    msg = QMessageBox(parent=self, text='Ocorreu um erro ao exportar os dados.\n\n%s' % (str(e)))
                msg.setWindowTitle('Erro')
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.exec()
        
if __name__ == '__main__':
    app = QApplication(sys_argv)
    window = table2spatialApp()
    window.show()
    sys_exit(app.exec())