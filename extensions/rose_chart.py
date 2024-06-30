# -*- coding: utf-8 -*-
"""
@author: Gabriel Maccari
"""

import matplotlib
import os
import numpy
import pandas
import matplotlib.pyplot as plt
from PyQt6 import QtCore, QtGui, QtWidgets

from extensions.shared_functions import handle_exception, toggle_wait_cursor, select_figure_save_location

matplotlib.use("svg")

PLOT_WIDTH = 350


class RoseChartWindow(QtWidgets.QMainWindow):
    def __init__(self, parent: QtWidgets.QMainWindow, df: pandas.DataFrame):
        super(RoseChartWindow, self).__init__(parent)
        self.parent = parent
        self.df = df.drop(columns="geometry")

        self.setWindowTitle('Diagrama de Roseta')
        self.setWindowIcon(QtGui.QIcon('icons/graph.png'))

        self.frame_stack = QtWidgets.QStackedWidget(self)
        self.setCentralWidget(self.frame_stack)

        # CONFIG PAGE
        self.config_layout = QtWidgets.QGridLayout()
        self.config_layout.setSpacing(5)
        self.config_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignCenter)
        self.config_page = QtWidgets.QWidget(self.frame_stack)
        self.config_page.setLayout(self.config_layout)
        self.frame_stack.addWidget(self.config_page)

        self.direction_column_lbl = QtWidgets.QLabel("Azimutes:", self.config_page)
        self.direction_column_cbx = QtWidgets.QComboBox(self.config_page)
        self.direction_column_cbx.addItems(self.filter_azimuth_columns())
        self.mirror_directions_chk = QtWidgets.QCheckBox("Espelhar dados direcionais", self.config_page)
        self.divisions_lbl = QtWidgets.QLabel("Número de setores:", self.config_page)
        self.divisions_edt = QtWidgets.QSpinBox(self.config_page)
        self.divisions_edt.setRange(4, 360)
        self.divisions_edt.setValue(16)
        self.ok_btn = QtWidgets.QPushButton("OK", self.config_page)

        self.config_layout.addWidget(self.direction_column_lbl, 0, 0, 1, 10)
        self.config_layout.addWidget(self.direction_column_cbx, 1, 0, 1, 10)
        self.config_layout.addWidget(self.mirror_directions_chk, 2, 0, 1, 10)
        self.config_layout.addWidget(self.divisions_lbl, 3, 0, 1, 8)
        self.config_layout.addWidget(self.divisions_edt, 3, 8, 1, 2)
        self.config_layout.addWidget(self.ok_btn, 4, 0, 1, 10)

        self.ok_btn.clicked.connect(self.ok_button_clicked)

        # PLOT PAGE
        self.plot_layout = QtWidgets.QGridLayout()
        self.plot_layout.setSpacing(5)
        self.plot_page = QtWidgets.QWidget(self.frame_stack)
        self.plot_page.setLayout(self.plot_layout)
        self.frame_stack.addWidget(self.plot_page)

        self.save_btn = QtWidgets.QPushButton(self.plot_page)
        self.save_btn.setIcon(QtGui.QIcon("icons/save.png"))
        self.save_btn.setIconSize(QtCore.QSize(28, 28))
        self.save_btn.setFixedSize(30, 30)
        self.image_btn = QtWidgets.QPushButton(self.plot_page)
        self.image_btn.setFlat(True)

        self.plot_layout.addWidget(self.save_btn, 0, 0, 1, 1)
        self.plot_layout.addWidget(self.image_btn, 1, 0, 10, 10)

        self.save_btn.clicked.connect(self.save_button_clicked)

    def filter_azimuth_columns(self):
        try:
            valid_columns = []
            for column in self.df:
                if not self.df[column].dtype in ("float64", "float32", "float16", 'int64', 'uint64', 'int32', 'uint32', 'int16', 'uint16', 'int8', 'uint8'):
                    continue
                if self.df[column].dropna().between(0, 360).all():
                    valid_columns.append(column)
            return valid_columns
        except Exception as error:
            handle_exception(error, "rose_chart - filter_azimuth_columns()", "Ops! Ocorreu um erro!", self)

    def ok_button_clicked(self):
        try:
            toggle_wait_cursor(True)

            azimuths = self.df[self.direction_column_cbx.currentText()].values.copy()
            mirror_data = self.mirror_directions_chk.isChecked()
            sectors = self.divisions_edt.value()

            plot_rose_chart(azimuths, mirror_data, sectors)

            self.frame_stack.setCurrentIndex(1)
            self.load_image()

            toggle_wait_cursor(False)
        except Exception as error:
            handle_exception(error, "stereogram - ok_button_clicked()", "Ops! Ocorreu um erro ao plotar o gráfico!", self)

    def load_image(self):
        self.image_btn.setIcon(QtGui.QIcon("plots/rose_chart.png"))
        pixmap = QtGui.QPixmap("plots/rose_chart.png")
        height = int(pixmap.height() * PLOT_WIDTH / pixmap.width())
        self.image_btn.setIconSize(QtCore.QSize(PLOT_WIDTH, height))
        self.image_btn.resize(PLOT_WIDTH, height)
        # self.setFixedSize(self.geometry().width(), self.geometry().height())

    def save_button_clicked(self):
        try:
            file_path, file_extension = select_figure_save_location(self)
            if not file_path:
                return
            plt.savefig(file_path, dpi=300, format=file_extension, transparent=True)
        except Exception as error:
            handle_exception(error, "rose_chart - save_button_clicked()", "Ops! Ocorreu um erro!", self)


def plot_rose_chart(azimuths, mirror=False, number_of_sectors=8):
    sector_width = 360 / number_of_sectors
    start_angle = 0 - (sector_width / 2)

    bin_edges = numpy.arange(start_angle, 361, sector_width)
    # Realiza a contagem de valores em cada uma das direções a partir das divisões criadas
    counts, bin_edges = numpy.histogram(azimuths, bin_edges)
    # Soma a primeira e a última contagem (ambas são N)
    counts[0] += counts[-1]

    fig = plt.figure(figsize=(5, 5), dpi=300)
    ax = fig.add_subplot(111, projection='polar')

    if mirror:
        # Divide os dados em dois conjuntos (0-180 e 180-360), soma os dois e duplica
        half = numpy.sum(numpy.split(counts, 2), 0)
        counts = numpy.concatenate([half, half])

    ax.bar(numpy.deg2rad(numpy.arange(0, 360, sector_width)), counts, width=numpy.deg2rad(sector_width*0.75),
           bottom=0.0, color="black")  # edgecolor="white", linewidth=0.1

    r_grid = (numpy.arange(0, max(counts), max(counts) / 5))
    r_grid = numpy.append(r_grid, max(counts))

    ax.set_facecolor('white')
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_thetagrids(numpy.arange(0, 360, 90), labels=[])
    ax.set_rgrids(r_grid, labels=[])
    ax.grid(alpha=0.1, color="black")

    # Fiz os rótulos dessa forma pra figura ficar igual à do estereograma
    labels = ['N', 'E', 'S', 'W']
    lbl_angles = numpy.arange(0, 360, 360 / len(labels))
    label_x = 0.5 - 0.55 * numpy.cos(numpy.radians(lbl_angles + 90))
    label_y = 0.5 + 0.55 * numpy.sin(numpy.radians(lbl_angles + 90))
    for i in range(len(labels)):
        ax.text(label_x[i], label_y[i], labels[i], transform=ax.transAxes, ha='center', va='center')

    plots_folder = os.getcwd() + "/plots"
    if not os.path.exists(plots_folder):
        os.makedirs(plots_folder)
    plt.savefig(f"{plots_folder}/rose_chart.png", dpi=300, format="png", transparent=True)
