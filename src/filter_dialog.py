from PyQt5.QtWidgets import QDialog, QPushButton, QApplication, QLineEdit
from PyQt5 import uic
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import pyqtSignal
from numpy import arange, ndarray, shape, fft, abs, amax, exp
import pyqtgraph as pg
import sys
from bin_functions import loadBin


class FilterDialog(QDialog):
    filterButtonClicked = pyqtSignal(ndarray)

    def __init__(self, data, parent=None):
        super().__init__(parent=parent)

        uic.loadUi("uis/filter_dialog.ui", self)

        self.data = data

        self.filter_button = self.findChild(QPushButton, "filter_button")
        self.preview_button = self.findChild(QPushButton, "preview_button")
        self.f0_edit = self.findChild(QLineEdit, "f0_edit")
        self.f1_edit = self.findChild(QLineEdit, "f1_edit")
        self.pw1 = self.findChild(pg.PlotWidget, "pw1")
        self.pw2 = self.findChild(pg.PlotWidget, "pw2")

        self.preview_button.clicked.connect(self.update_plots)
        self.filter_button.clicked.connect(self.start_filtration)

        amplitude_label = "<span style=\"color:white;font-size:11px\">amplitude</span>"

        self.pw1.setTitle("Ascan - time domain")
        self.pw1.setLabel('bottom', "<span style=\"color:white;font-size:11px\">samples</span>")
        self.pw1.setLabel('left', amplitude_label)
        self.pw2.setTitle("Ascan - frequency domain")
        self.pw2.setLabel('bottom', "<span style=\"color:white;font-size:11px\">frequency [Hz]</span>")
        self.pw2.setLabel('left', amplitude_label)

        validator = FreqInputValidator()
        self.f0_edit.setValidator(validator)
        self.f1_edit.setValidator(validator)

        fs = 200_000_000
        N = shape(self.data)[0]
        df = fs/N
        self.f = arange(0, fs/2+df, df)

        f0 = int(100 * 1e3)
        f1 = int(8.42 * 1e6)
        self.f0_edit.setText(str(f0))
        self.f1_edit.setText(str(f1))

        self.pw1_curve1 = pg.PlotCurveItem()
        self.pw1_curve1.setPen(0,150,255)
        self.pw1_curve2 = pg.PlotCurveItem()
        self.pw1_curve2.setPen(255,165,0)
        self.pw2_curve1 = pg.PlotCurveItem()
        self.pw2_curve1.setPen(0,150,255)
        self.pw2_curve2 = pg.PlotCurveItem()
        self.pw2_curve2.setPen(255,0,0)

        self.pw1.addItem(self.pw1_curve1)
        self.pw1.addItem(self.pw1_curve2)
        self.pw2.addItem(self.pw2_curve1)
        self.pw2.addItem(self.pw2_curve2)

        legend1 = pg.LegendItem((80,60), offset=(100,20))
        legend1.setParentItem(self.pw1.getPlotItem())
        legend1.addItem(self.pw1_curve1, 'original')
        legend1.addItem(self.pw1_curve2, 'filtered')

        legend2 = pg.LegendItem((80,60), offset=(100,20))
        legend2.setParentItem(self.pw2.getPlotItem())
        legend2.addItem(self.pw2_curve1, 'fft')
        legend2.addItem(self.pw2_curve2, 'filter window')

        self.pw1_curve1.setData(self.data)

        A_fft = fft.rfft(self.data)
        A_fft = abs(A_fft)
        A_fft = A_fft[0:(N//2+1)]
        self.pw2_curve1.setData(self.f, A_fft/amax(A_fft))

        self.update_plots()
        self.show()

    def update_plots(self):
        f0 = int(self.f0_edit.text())
        f1 = int(self.f1_edit.text())
        self.filter_win = (1 - exp(-(self.f/f0)**2)) * exp(-(self.f/f1)**2 - (self.f/f1)**4)
        self.pw2_curve2.setData(self.f, self.filter_win)

        Ascan_fft = fft.rfft(self.data)
        Ascan_filt = Ascan_fft * self.filter_win
        Ascan_t = fft.irfft(Ascan_filt)*2
        self.pw1_curve2.setData(Ascan_t)
    
    def start_filtration(self):
        self.filterButtonClicked.emit(self.filter_win)
        

class FreqInputValidator(QIntValidator):
    def __init__(self):
        super().__init__(bottom=1)
    
    def fixup(self, input):
        input = "1"
        return super().fixup(input)


if __name__ == '__main__':
    # Initialize the App
    app = QApplication(sys.argv)

    fid = "data\\500avg.bin"

    Bscan, n_Ascans, n_pts = loadBin(fid)
    Ascan = Bscan[1400,:]

    dialog = FilterDialog(Ascan)
    app.exec_()
