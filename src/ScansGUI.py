from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QComboBox, QCheckBox, QLineEdit, QWidget, QProgressBar, QSpinBox
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtCore import QLocale, QObject, pyqtSignal, QThread, QTimer
from PyQt5 import uic
from filter_dialog import FilterDialog
from numpy import shape, amax, fft, load
import pyqtgraph as pg
import sys


class ScansGUI(QMainWindow):
    def __init__(self, data, sampling_step):
        super().__init__()

        uic.loadUi("dist/mainWindow.ui", self)
        pg.setConfigOption('imageAxisOrder', 'col-major')
        self.setWindowTitle('Graphical User Interface')

        self.data = data

        self.pw1 = self.findChild(pg.PlotWidget, "pw1")
        self.pw2 = self.findChild(pg.PlotWidget, "pw2")
        self.pw3 = self.findChild(pg.PlotWidget, "pw3")
        self.pw4 = self.findChild(pg.PlotWidget, "pw4")
        self.cmap_comboBox = self.findChild(QComboBox, "cmap_comboBox")
        self.glw1 = self.findChild(pg.GraphicsLayoutWidget, "glw1")
        self.glw2 = self.findChild(pg.GraphicsLayoutWidget, "glw2")
        self.cAuto_cb = self.findChild(QCheckBox, "cAuto_cb")
        self.bAuto_cb = self.findChild(QCheckBox, "bAuto_cb")
        self.c_min = self.findChild(QLineEdit, "c_min")
        self.c_max = self.findChild(QLineEdit, "c_max")
        self.b_min = self.findChild(QLineEdit, "b_min")
        self.b_max = self.findChild(QLineEdit, "b_max")
        self.c_aspect_cb = self.findChild(QCheckBox, "c_aspect_cb")
        self.b1_aspect_cb = self.findChild(QCheckBox, "b1_aspect_cb")
        self.b2_aspect_cb = self.findChild(QCheckBox, "b2_aspect_cb")
        self.filter_button = self.findChild(QPushButton, "filter_button")
        self.c_clim_sym_cb = self.findChild(QCheckBox, "c_clim_sym_cb")
        self.b_clim_sym_cb = self.findChild(QCheckBox, "b_clim_sym_cb")
        self.start_d = self.findChild(QSpinBox, "start_d")
        self.end_d = self.findChild(QSpinBox, "end_d")
        self.timestep = self.findChild(QSpinBox, "timestep")
        self.play_button = self.findChild(QPushButton, "play_button")
        self.stop_button = self.findChild(QPushButton, "stop_button")

        self.start_d.setMaximum(shape(self.data)[2])
        self.end_d.setMaximum(shape(self.data)[2])
        self.end_d.setValue(shape(self.data)[2])

        validator = ClimValidator()
        self.c_min.setValidator(validator)
        self.c_max.setValidator(validator)
        self.b_min.setValidator(validator)
        self.b_max.setValidator(validator)

        self.cAuto_cb.stateChanged.connect(lambda: self.set_manual_clim("C", not self.cAuto_cb.isChecked()))
        self.c_min.editingFinished.connect(lambda: self.clim_edited("cmin"))
        self.c_max.editingFinished.connect(lambda: self.clim_edited("cmax"))
        
        self.bAuto_cb.stateChanged.connect(lambda: self.set_manual_clim("B", not self.bAuto_cb.isChecked()))
        self.b_min.editingFinished.connect(lambda: self.clim_edited("bmin"))
        self.b_max.editingFinished.connect(lambda: self.clim_edited("bmax"))

        self.c_aspect_cb.stateChanged.connect(self.change_aspect)
        self.b1_aspect_cb.stateChanged.connect(self.change_aspect)
        self.b2_aspect_cb.stateChanged.connect(self.change_aspect)

        self.filter_button.clicked.connect(self.open_filter_dialog)

        self.c_clim_sym_cb.stateChanged.connect(lambda: self.symmetric_clim("C", self.c_clim_sym_cb.isChecked()))
        self.b_clim_sym_cb.stateChanged.connect(lambda: self.symmetric_clim("B", self.b_clim_sym_cb.isChecked()))

        self.play_button.clicked.connect(self.prepare_animation)
        self.stop_button.clicked.connect(self.stop_animation)

        self.colorbar1 = pg.ColorBarItem(interactive=False, orientation='horizontal')
        self.colorbar2 = pg.ColorBarItem(interactive=False, orientation='horizontal')
        self.glw1.addItem(self.colorbar1)
        self.glw2.addItem(self.colorbar2)

        self.cmap_comboBox.addItem("gray", "CET-L1")
        self.cmap_comboBox.addItem("cividis", "cividis")
        self.cmap_comboBox.addItem("inferno", "inferno")
        self.cmap_comboBox.addItem("viridis", "viridis")
        self.cmap_comboBox.addItem("rainbow", "CET-R4")
        self.cmap_comboBox.addItem("plasma", "plasma")
        self.cmap_comboBox.currentTextChanged.connect(self.change_colormap)

        label_style = "<span style=\"color:white;font-size:12px\">[mm]</span>"

        fs = 200 * 10e6
        v = 3000 * 10e3

        self.x_scale = 0.05
        self.y_scale = 0.05*sampling_step
        self.d_scale = v/(fs*2)

        self.max = amax(self.data)
        
        self.x = int(shape(self.data)[0]/2)
        self.y = int(shape(self.data)[1]/2)
        self.d = int(shape(self.data)[2]/2)

        self.pw1.setTitle("C scan")
        self.C_scan = ScanImage()
        self.C_scan.setImage(self.data[:,:,self.d])
        self.pw1.addItem(self.C_scan)
        self.pw1.invertY(True)
        self.pw1.setLabel('left', label_style)
        self.pw1.setLabel('bottom', label_style)
        self.pw1.getAxis('bottom').setScale(self.x_scale)
        self.pw1.getAxis('left').setScale(self.y_scale)

        self.pw2.setTitle("B1 scan")
        self.B1_scan = ScanImage()
        self.B1_scan.setImage(self.data[self.x,:,:])
        self.pw2.addItem(self.B1_scan)
        self.pw2.invertY(True)
        self.pw2.setLabel('left', label_style)
        self.pw2.setLabel('bottom', label_style)
        self.pw2.getAxis('bottom').setScale(self.y_scale)
        self.pw2.getAxis('left').setScale(self.d_scale)
        
        self.pw3.setTitle("B2 scan")
        self.B2_scan = ScanImage()
        self.B2_scan.setImage(self.data[:,self.y,:])
        self.pw3.addItem(self.B2_scan)
        self.pw3.invertY(True)
        self.pw3.setLabel('left', label_style)
        self.pw3.setLabel('bottom', label_style)
        self.pw3.getAxis('bottom').setScale(self.x_scale)
        self.pw3.getAxis('left').setScale(self.d_scale)

        self.pw4.setTitle("A scan")
        self.A_scan = ScanPlot()
        self.A_scan.setData(self.data[self.x,self.y,:])
        self.pw4.addItem(self.A_scan)
        self.pw4.setLabel('bottom', label_style)
        self.pw4.getAxis('bottom').setScale(self.d_scale)

        self.c_levels = tuple(self.C_scan.getLevels())
        self.colorbar1.setLevels(self.c_levels)

        self.b_levels = tuple(self.B1_scan.getLevels())
        self.colorbar2.setLevels(self.b_levels)

        self.b_min.setText(str(round(self.b_levels[0], 3)))
        self.b_max.setText(str(round(self.b_levels[1], 3)))
        self.c_min.setText(str(round(self.c_levels[0], 3)))
        self.c_max.setText(str(round(self.c_levels[1], 3)))

        self.change_colormap()
        self.update_scans()

        self.C_scan.scene().sigMouseClicked.connect(lambda: self.scan_clicked("C"))
        self.B1_scan.scene().sigMouseClicked.connect(lambda: self.scan_clicked("B1"))
        self.B2_scan.scene().sigMouseClicked.connect(lambda: self.scan_clicked("B2"))
        self.A_scan.scene().sigMouseClicked.connect(lambda: self.scan_clicked("A"))

        self.show()

    def change_colormap(self):
        chosen_cmap = self.cmap_comboBox.currentData()

        if chosen_cmap == 'inferno' or chosen_cmap == 'plasma':
            pen = (0,255,255)
        elif chosen_cmap == 'CET-R4':
            pen = (0,0,0)
        else:
            pen = (255,0,0)

        self.C_scan.vLine.setPen(pen)
        self.C_scan.hLine.setPen(pen)
        self.B1_scan.vLine.setPen(pen)
        self.B1_scan.hLine.setPen(pen)
        self.B2_scan.vLine.setPen(pen)
        self.B2_scan.hLine.setPen(pen)

        self.C_scan.setColorMap(chosen_cmap)
        self.B1_scan.setColorMap(chosen_cmap)
        self.B2_scan.setColorMap(chosen_cmap)
        self.colorbar1.setColorMap(chosen_cmap)
        self.colorbar2.setColorMap(chosen_cmap)
    
    def scan_clicked(self, scan):
        if scan == "C":
            self.x = self.C_scan.x
            self.y = self.C_scan.y
        elif scan == "B1":
            self.y = self.B1_scan.x
            self.d = self.B1_scan.y
        elif scan == "B2":
            self.x = self.B2_scan.x
            self.d = self.B2_scan.y
        elif scan == "A":
            self.d = self.A_scan.x
        
        self.update_scans()
        self.update_color_range()

    def update_scans(self):
        self.C_scan.setImage(self.data[:,:,self.d])
        self.B1_scan.setImage(self.data[self.x,:,:])
        self.B2_scan.setImage(self.data[:,self.y,:])
        self.C_scan.vLine.setPos(self.x)
        self.C_scan.hLine.setPos(self.y)
        self.B1_scan.vLine.setPos(self.y)
        self.B1_scan.hLine.setPos(self.d)
        self.B2_scan.vLine.setPos(self.x)
        self.B2_scan.hLine.setPos(self.d)
        self.A_scan.setData(self.data[self.x,self.y,:])
        self.A_scan.vLine.setPos(self.d)
    
    def update_color_range(self):
        if self.cAuto_cb.isChecked():
            min, max = self.C_scan.getLevels()
            self.colorbar1.setLevels((min, max))
        else:
            self.C_scan.setLevels(self.c_levels)
            self.colorbar1.setLevels(self.c_levels)
        
        if self.bAuto_cb.isChecked():
            min, max = self.B1_scan.getLevels()
            self.colorbar2.setLevels((min, max))
        else:
            self.B1_scan.setLevels(self.b_levels)
            self.B2_scan.setLevels(self.b_levels)
            self.colorbar2.setLevels(self.b_levels)
    
    def set_manual_clim(self, scan, enabled):
        if scan == "C":
            if not enabled:
                self.c_min.setEnabled(False)
                self.c_max.setEnabled(False)
                self.c_clim_sym_cb.setEnabled(False)
            else:
                self.c_min.setEnabled(True)
                self.c_max.setEnabled(True)
                self.c_clim_sym_cb.setEnabled(True)
                min = float(self.c_min.text())
                max = float(self.c_max.text())
                self.c_levels = (min, max)
        elif scan == "B":
            if not enabled:
                self.b_min.setEnabled(False)
                self.b_max.setEnabled(False)
                self.b_clim_sym_cb.setEnabled(False)
            else:
                self.b_min.setEnabled(True)
                self.b_max.setEnabled(True)
                self.b_clim_sym_cb.setEnabled(True)
                min = float(self.b_min.text())
                max = float(self.b_max.text())
                self.b_levels = (min, max)
        
        self.update_scans()
        self.update_color_range()

    def symmetric_clim(self, scan, bool_val):
        if scan == "C" and bool_val:
            max_abs_val = max(abs(float(self.c_min.text())), abs(float(self.c_max.text())))
            self.c_min.setText(str(-max_abs_val))
            self.c_max.setText(str(max_abs_val))
        elif scan == "B" and bool_val:
            max_abs_val = max(abs(float(self.b_min.text())), abs(float(self.b_max.text())))
            self.b_min.setText(str(-max_abs_val))
            self.b_max.setText(str(max_abs_val))
        
        self.set_manual_clim(scan, True)

    def clim_edited(self, line_edit):
        if line_edit == "cmin" and self.c_clim_sym_cb.isChecked():
            c_min_val = float(self.c_min.text())
            if c_min_val > 0:
                self.c_min.setText(str(-c_min_val))
                self.c_max.setText(str(c_min_val))
            else:
                self.c_max.setText(str(abs(c_min_val)))
        elif line_edit == "cmax" and self.c_clim_sym_cb.isChecked():
            c_max_val = float(self.c_max.text())
            if c_max_val < 0:
                self.c_min.setText(str(c_max_val))
                self.c_max.setText(str(abs(c_max_val)))
            else:
                self.c_min.setText(str(-c_max_val))
        elif line_edit == "bmin" and self.b_clim_sym_cb.isChecked():
            b_min_val = float(self.b_min.text())
            if b_min_val > 0:
                self.b_min.setText(str(-b_min_val))
                self.b_max.setText(str(b_min_val))
            else:
                self.b_max.setText(str(abs(b_min_val)))
        elif line_edit == "bmax" and self.b_clim_sym_cb.isChecked():
            b_max_val = float(self.b_max.text())
            if b_max_val < 0:
                self.b_min.setText(str(b_max_val))
                self.b_max.setText(str(abs(b_max_val)))
            else:
                self.b_min.setText(str(-b_max_val))

        if line_edit == "cmin" or line_edit == "cmax":
            self.set_manual_clim("C", True)
        elif line_edit == "bmin" or line_edit == "bmax":
            self.set_manual_clim("B", True)

    def change_aspect(self):
        if self.c_aspect_cb.isChecked():
            ratio = self.x_scale/self.y_scale
            self.C_scan.getViewBox().setAspectLocked(lock=True, ratio=ratio)
        else:
            self.C_scan.getViewBox().setAspectLocked(lock=False)

        if self.b1_aspect_cb.isChecked():
            ratio = self.y_scale/self.d_scale
            self.B1_scan.getViewBox().setAspectLocked(lock=True, ratio=ratio)
        else:
            self.B1_scan.getViewBox().setAspectLocked(lock=False)
        
        if self.b2_aspect_cb.isChecked():
            ratio = self.x_scale/self.d_scale
            self.B2_scan.getViewBox().setAspectLocked(lock=True, ratio=ratio)
        else:
            self.B2_scan.getViewBox().setAspectLocked(lock=False)
    
    def prepare_animation(self):
        start = self.start_d.value()
        end = self.end_d.value()
        step = self.timestep.value()

        if start is not end:
            self.timer = QTimer()
            self.timer.timeout.connect(self.start_animation)
            self.timer.start(step)
            self.play_button.setEnabled(False)
            self.start_d.setEnabled(False)
            self.end_d.setEnabled(False)
            self.timestep.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.d = start-1
            self.start_animation()

    def start_animation(self):
        start = self.start_d.value()
        end = self.end_d.value()

        if (start < end):
            self.d += 1
        if (start > end):
            self.d -= 1

        self.C_scan.setImage(self.data[:,:,self.d])
        if not self.cAuto_cb.isChecked():
            self.C_scan.setLevels(self.c_levels)

        self.B1_scan.hLine.setPos(self.d)
        self.B2_scan.hLine.setPos(self.d)
        self.A_scan.vLine.setPos(self.d)

        if self.d == end-1:
            self.stop_animation()

    def stop_animation(self):
        self.timer.stop()
        self.play_button.setEnabled(True)
        self.start_d.setEnabled(True)
        self.end_d.setEnabled(True)
        self.timestep.setEnabled(True)
        self.stop_button.setEnabled(False)

    def open_filter_dialog(self):
        Ascan = self.data[self.x,self.y,:]
        self.dialog = FilterDialog(Ascan, parent=self)
        self.dialog.filterButtonClicked.connect(self.filter_data)
    
    def filter_data(self, filter_window):
        self.thread = QThread()
        self.dfc = DataFilteringClass(self.data, filter_window)
        self.dfc.moveToThread(self.thread)

        self.thread.started.connect(self.dfc.filter_data)
        self.dfc.finished.connect(self.thread.quit)
        self.dfc.finished.connect(self.dfc.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.loadingWindow = LoadingWindow()
        self.loadingWindow.progress_bar.setRange(1, shape(self.data)[0]-1)
        self.dfc.progress.connect(
            lambda val: self.loadingWindow.progress_bar.setValue(val)
        )

        self.loadingWindow.show()
        self.thread.start()

        self.dialog.close()
        self.filter_button.setEnabled(False)

        self.thread.finished.connect(
            lambda: self.loadingWindow.close()
        )
        self.thread.finished.connect(
            lambda: self.filter_button.setEnabled(True)
        )

        self.dfc.finished.connect(lambda: self.update_scans())
        self.dfc.finished.connect(lambda: self.update_color_range())
        

class ScanImage(pg.ImageItem):

    def __init__(self, image=None, **kwargs):
        super().__init__(image, **kwargs)

        self.vLine = pg.InfiniteLine(angle=90, movable=False, pen=(255,0,0))
        self.hLine = pg.InfiniteLine(angle=0, movable=False, pen=(255,0,0))
        self.vLine.setParentItem(self)
        self.hLine.setParentItem(self)

    def mouseClickEvent(self, ev):
        pos = ev.pos()
        self.x, self.y = round(pos[0]), round(pos[1])
        self.vLine.setPos(self.x)
        self.hLine.setPos(self.y)

        
class ScanPlot(pg.PlotCurveItem):
    def __init__(self, parent=None):
        super(ScanPlot, self).__init__(parent)

        self.vLine = pg.InfiniteLine(angle=90, movable=False, pen=(255,0,0))
        self.vLine.setParentItem(self)
        
    def mouseClickEvent(self, ev):
        pos = ev.pos()
        self.x = round(pos[0])
        self.vLine.setPos(self.x)
      

class ClimValidator(QDoubleValidator):
    def __init__(self):
        super().__init__(bottom=-10, top=10, decimals=4)
        
        locale = QLocale(QLocale.English, QLocale.UnitedStates)
        self.setLocale(locale)
        self.setNotation(QDoubleValidator.StandardNotation)
    
    def fixup(self, input):
        input = "0"
        return super().fixup(input)


class DataFilteringClass(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, data, filter_win):
        super().__init__()

        self.data = data
        self.filter_win = filter_win

    def filter_data(self):
        x_pts = shape(self.data)[0]
        y_pts = shape(self.data)[1]

        for x in range(x_pts):
            for y in range(y_pts):
                Ascan = self.data[x,y,:]
                A_fft = fft.rfft(Ascan)
                A_filt = A_fft * self.filter_win
                A_t = fft.irfft(A_filt) * 2
                self.data[x,y,:] = A_t

            self.progress.emit(x)
        self.finished.emit()


class LoadingWindow(QWidget):
    def __init__(self):
        super().__init__()

        uic.loadUi("dist/loading_window.ui", self)
        self.progress_bar = self.findChild(QProgressBar)

        
if __name__ == '__main__':
    # Initialize the App
    app = QApplication(sys.argv)

    test_data = load("sample_data\\data5.npy")
    sampling_step = 5

    gui = ScansGUI(test_data, sampling_step)
    sys.exit(app.exec_())
