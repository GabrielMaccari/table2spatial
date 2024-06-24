import matplotlib
import numpy
import geopandas
import mplstereonet
import os
import matplotlib.pyplot as plt
from PyQt6 import QtCore, QtGui, QtWidgets
from icecream import ic

matplotlib.use("svg")

COLORMAPS = ('Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds', 'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu',
             'BuPu', 'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn')

MEASUREMENT_TYPES = {
    'Planos (dip direction/dip)': ('Dip direction', 'Dip'),
    'Planos (strike/dip)': ('Strike', 'Dip'),
    'Linhas (plunge/bearing)': ('Bearing', 'Plunge'),
    'Linhas em planos (strike/dip/rake)': ('Strike', 'Dip', 'Rake')
}

# Strike, dip direction e bearing: 0 - 360°
# Dip e plunge: 0 - 90°
# Rake: -180° - 180°


class StereogramWindow(QtWidgets.QMainWindow):
    def __init__(self, parent: QtWidgets.QMainWindow, gdf: geopandas.GeoDataFrame):
        super(StereogramWindow, self).__init__(parent)
        self.parent = parent
        self.gdf = gdf.copy()

        self.setWindowTitle('Estereograma')
        self.setWindowIcon(QtGui.QIcon('icons/graph.png'))

        self.frame_stack = QtWidgets.QStackedWidget(self)
        self.setCentralWidget(self.frame_stack)

        config_layout = QtWidgets.QVBoxLayout()
        config_layout.setSpacing(5)
        config_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignCenter)
        config_page = QtWidgets.QWidget(self.frame_stack)
        config_page.setLayout(config_layout)
        self.frame_stack.addWidget(config_page)

        plot_layout = QtWidgets.QGridLayout()
        plot_layout.setSpacing(5)
        plot_page = QtWidgets.QWidget(self.frame_stack)
        plot_page.setLayout(plot_layout)
        self.frame_stack.addWidget(plot_page)

        # CONFIG PAGE
        msr_type = "Planos (dip direction/dip)"
        lb1, lb2, lb3 = MEASUREMENT_TYPES[msr_type][0]+"s:", MEASUREMENT_TYPES[msr_type][1]+"s:", "Rakes:"
        self.measurement_type_lbl = QtWidgets.QLabel("Tipo de medida:", config_page)
        self.measurement_type_cbx = QtWidgets.QComboBox(config_page)
        self.measurement_type_cbx.addItems(MEASUREMENT_TYPES)
        self.measurement_type_cbx.setMinimumWidth(300)
        self.azimuths_column_lbl = QtWidgets.QLabel(lb1, config_page)
        self.azimuths_column_cbx = QtWidgets.QComboBox(config_page)
        self.azimuths_column_cbx.addItems(self.filter_angle_columns("azimuth"))
        self.dips_column_lbl = QtWidgets.QLabel(lb2, config_page)
        self.dips_column_cbx = QtWidgets.QComboBox(config_page)
        self.dips_column_cbx.addItems(self.filter_angle_columns("dip"))
        self.rakes_column_lbl = QtWidgets.QLabel(lb3, config_page)
        self.rakes_column_lbl.setEnabled(False)
        self.rakes_column_cbx = QtWidgets.QComboBox(config_page)
        self.rakes_column_cbx.setEnabled(False)
        self.plot_poles_chk = QtWidgets.QCheckBox("Plotar planos como pólos")
        self.ok_btn = QtWidgets.QPushButton("OK")

        config_layout.addWidget(self.measurement_type_lbl)
        config_layout.addWidget(self.measurement_type_cbx)
        config_layout.addWidget(self.azimuths_column_lbl)
        config_layout.addWidget(self.azimuths_column_cbx)
        config_layout.addWidget(self.dips_column_lbl)
        config_layout.addWidget(self.dips_column_cbx)
        config_layout.addWidget(self.rakes_column_lbl)
        config_layout.addWidget(self.rakes_column_cbx)
        config_layout.addWidget(self.plot_poles_chk)
        config_layout.addWidget(self.ok_btn)

        self.measurement_type_cbx.currentTextChanged.connect(self.measurement_type_selected)
        self.ok_btn.clicked.connect(self.ok_button_clicked)

        # PLOT PAGE
        self.save_btn = QtWidgets.QPushButton(plot_page)
        self.save_btn.setIcon(QtGui.QIcon("icons/save.png"))
        self.save_btn.setIconSize(QtCore.QSize(28, 28))
        self.save_btn.setFixedSize(30, 30)
        self.image_lbl = QtWidgets.QLabel(plot_page)
        self.image_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter | QtCore.Qt.AlignmentFlag.AlignCenter)
        self.image_lbl.resize(400, 300)

        plot_layout.addWidget(self.save_btn, 0, 0, 1, 1)
        plot_layout.addWidget(self.image_lbl, 1, 0, 10, 10)

        self.save_btn.clicked.connect(self.save_button_clicked)

    def filter_angle_columns(self, angle_type):
        try:
            ranges = {
                "azimuth": (0, 360),
                "dip": (0, 90),
                "rake": (-180, 180)
            }
            min_angle, max_angle = ranges[angle_type][0], ranges[angle_type][1]
            valid_columns = []
            for column in self.gdf:
                if not self.gdf[column].dtype in ("float64", "float32", "float16", 'int64', 'uint64', 'int32', 'uint32', 'int16', 'uint16', 'int8', 'uint8'):
                    continue
                if self.gdf[column].dropna().between(min_angle, max_angle).all():
                    valid_columns.append(column)
            return valid_columns
        except Exception as error:
            handle_exception(error, "stereogram - filter_angle_columns()", "Ops! Ocorreu um erro!")

    def measurement_type_selected(self):
        try:
            msr_type = self.measurement_type_cbx.currentText()
            msr_components = MEASUREMENT_TYPES[msr_type]
            self.azimuths_column_lbl.setText(msr_components[0]+"s:")
            self.dips_column_lbl.setText(msr_components[1]+"s:")
            self.rakes_column_lbl.setEnabled(len(msr_components) > 2)
            self.rakes_column_cbx.setEnabled(len(msr_components) > 2)
            self.plot_poles_chk.setEnabled(msr_type.startswith("Planos"))
            if len(msr_components) > 2:
                self.rakes_column_cbx.addItems(self.filter_angle_columns("rake"))
            else:
                self.rakes_column_cbx.clear()
        except Exception as error:
            handle_exception(error, "stereogram - measurement_type_selected()", "Ops! Ocorreu um erro!")

    def ok_button_clicked(self):
        try:
            toggle_wait_cursor(True)

            msr_type = self.measurement_type_cbx.currentText()
            plot_poles = self.plot_poles_chk.isChecked()

            azimuths = self.gdf[self.azimuths_column_cbx.currentText()].values
            dips = self.gdf[self.dips_column_cbx.currentText()].values
            rakes = None

            if msr_type.startswith("Planos"):
                plot_type = "poles" if plot_poles else "planes"
            elif msr_type.startswith("Linhas em planos"):
                plot_type = "rakes"
                rakes = self.gdf[self.rakes_column_cbx.currentText()].values
            else:
                plot_type = "lines"

            az_type = MEASUREMENT_TYPES[msr_type][0].lower() if MEASUREMENT_TYPES[msr_type][0] != "Bearing" else "strike"

            plot_stereogram(azimuths, dips, rakes, plot_type, az_type)

            self.frame_stack.setCurrentIndex(1)
            self.load_image()

            toggle_wait_cursor(False)
        except Exception as error:
            handle_exception(error, "stereogram - ok_button_clicked()", "Ops! Ocorreu um erro ao plotar o gráfico!")

    def load_image(self):
        pixmap = QtGui.QPixmap('plots/plot.png')
        width = 400
        height = int(pixmap.height() * width / pixmap.width())
        pixmap = pixmap.scaled(width, height, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
        self.image_lbl.setPixmap(pixmap)

    def save_button_clicked(self):
        try:
            file_name, file_type = QtWidgets.QFileDialog.getSaveFileName(
                self, caption="Salvar gráfico",
                filter="Formatos suportados (*.png *.jpg *.svg);;"
                       "PNG (*.png);;"
                       "JPG (*.jpg);;"
                       "SVG (*.svg)"
            )
            file_type = file_name[-3:]
            plt.savefig(file_name, dpi=300, format=file_type, transparent=True)
        except Exception as error:
            handle_exception(error, "stereogram - save_button_clicked()", "Ops! Ocorreu um erro!")

    def center_to_parent(self):
        self.setFixedSize(self.geometry().width(), self.geometry().height())
        self.geometry().moveCenter(self.parent.geometry().center())
        self.move(self.geometry().topLeft())


def handle_exception(error, context, message: str = "Ocorreu um erro.", ):
    toggle_wait_cursor(False)
    ic(context, error)
    show_popup(f"{message}", "error", f"Descrição do erro: {error}\n\nContexto: {context}")


def plot_stereogram(azimuths, dips, rakes: str = None, plot_type: str = "poles", plane_azimuth_type: str = "strike"):

    if plot_type not in ("planes", "poles", "lines", "rakes"):
        raise ValueError("plot_type deve ser \"poles\", \"lines\" ou \"rakes\".")
    if plane_azimuth_type not in ("strike", "dip direction"):
        raise ValueError("azimuth_type deve ser \"strike\", \"dip direction\" ou \"bearing\".")
    if rakes is not None and not (len(azimuths) == len(dips) == len(rakes)):
        raise IndexError(f"A quantidade de azimutes, mergulhos e rakes não é a mesma (azimuths={len(azimuths)}, dips={len(dips)}, rakes={len(rakes)}).")
    elif rakes is None and not (len(azimuths) == len(dips)):
        raise IndexError(f"A quantidade de azimutes e mergulhos não é a mesma (azimuths={len(azimuths)}, dips={len(dips)}).")

    # Cria e estiliza a figura base
    fig, ax = mplstereonet.subplots(figsize=[5, 5], projection="stereonet")
    ax.set_facecolor('white')
    ax.set_azimuth_ticks([])
    ax.grid(color='black', alpha=0.1)

    if plane_azimuth_type == "dip direction":
        azimuths -= 90

    if plot_type == "planes":
        ax.plane(azimuths, dips, color="black")
    elif plot_type == "poles":
        ax.pole(azimuths, dips, color="black")
    elif plot_type == "lines":
        ax.line(dips, azimuths, color="black")
    else:
        ax.plane(azimuths, dips, color="black")
        ax.rake(azimuths, dips, rakes, color="black")

    labels = ['N', 'E', 'S', 'W']
    lbl_angles = numpy.arange(0, 360, 360 / len(labels))
    label_x = 0.5 - 0.55 * numpy.cos(numpy.radians(lbl_angles + 90))
    label_y = 0.5 + 0.55 * numpy.sin(numpy.radians(lbl_angles + 90))
    for i in range(len(labels)):
        ax.text(label_x[i], label_y[i], labels[i], transform=ax.transAxes, ha='center', va='center')

    plots_folder = os.getcwd() + "/plots"
    if not os.path.exists(plots_folder):
        os.makedirs(plots_folder)
    plt.savefig(f"{plots_folder}/plot.png", dpi=300, format="png", transparent=True)


def show_popup(message: str, msg_type: str = "notification", details: str | None = None):
    title = "Erro" if msg_type == "error" else "Notificação"
    icon = QtGui.QIcon("icons/error.png" if msg_type == "error" else "icons/info.png")

    popup = QtWidgets.QMessageBox()

    popup.setText(message)
    popup.setWindowTitle(title)
    popup.setWindowIcon(icon)

    if details is not None:
        popup.setDetailedText(details)

    popup.exec()


def toggle_wait_cursor(activate: bool = True):
    if activate:
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
    else:
        QtWidgets.QApplication.restoreOverrideCursor()
