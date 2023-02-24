from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel, QFileDialog, QLineEdit, QSpinBox, QCheckBox, QProgressBar
from PyQt5 import uic
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QLocale
from PyQt5.QtGui import QDoubleValidator
from os import listdir
from os.path import isfile, join, isdir
import ctypes
import sys
from numpy import empty, shape, fromfile, reshape, amax
from scipy.ndimage import gaussian_filter


class FileReader(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    files_counter = pyqtSignal(int)

    def __init__(self, dir, filter, sigma, truncate, sampling_step, normalize):
        super(FileReader, self).__init__()
        self.dir = dir
        self.filter = filter
        self.sigma = sigma
        self.truncate = truncate
        self.sampling_step = sampling_step
        self.normalize = normalize

        self.data = None

    def load_data(self):
        if isdir(self.dir):
            files = [f for f in listdir(self.dir) if isfile(join(self.dir, f))]
            files.sort(key=lambda f: len(f))

            try:
                (Bscan1, n_Ascans, n_pts) = self.loadBin(join(self.dir, files[0]))

                self.files_counter.emit(len(files))

                D = empty(shape=(len(files), n_Ascans, n_pts))
                D[0, :, :] = Bscan1

                for i in range(1, len(files)):
                    (B, _, _) = self.loadBin(join(self.dir, files[i]))
                    D[i, :, :] = B
                    self.progress.emit(i)

                self.data = D
                self.finished.emit()
            except:
                display_error("Folder has no suitable data")
        else:
            display_error("Folder doesn't exist!")

        self.finished.emit()

    def loadBin(self, fname):
        N = fromfile(fname, count=2, dtype='>u4')

        n_Ascans = N[0]
        n_pts = N[1]

        A = fromfile(fname, count=n_Ascans*n_pts, dtype='>f8')
        B = reshape(A, (n_Ascans, n_pts))

        if self.filter:
            sigma = float(self.sigma)
            truncate = float(self.truncate)

            B = gaussian_filter(B, sigma=sigma, truncate=truncate)
        
        if self.sampling_step != 1:
            B_sampled = B[::self.sampling_step, :]
            B = B_sampled
            n_Ascans = shape(B)[0]

        if self.normalize:
            B_norm = empty(shape=(n_Ascans, n_pts))
            for i in range(n_Ascans):
                Ascan = B[i, :]
                max_in_Ascan = amax(Ascan)
                B_norm[i, :] = Ascan / max_in_Ascan
            
            return (B_norm, n_Ascans, n_pts)
        else:
            max_in_B = amax(B)
            B /= max_in_B

        return (B, n_Ascans, n_pts)

      
class FileUI(QMainWindow):
    def __init__(self):
        super(FileUI, self).__init__()

        uic.loadUi("uis/fileDialog.ui", self)
        self.setWindowTitle("Load data")

        self.label1 = self.findChild(QLabel, "label_1")
        self.dir_path_line = self.findChild(QLineEdit, "dir_path_line")
        self.ds_spinbox = self.findChild(QSpinBox, "ds_spinBox")
        self.gauss_checkbox = self.findChild(QCheckBox, "gauss_checkbox")
        self.sigma_edit = self.findChild(QLineEdit, "sigma_edit")
        self.truncate_edit = self.findChild(QLineEdit, "truncate_edit")
        self.normalize_checkbox = self.findChild(QCheckBox, "normalize_checkbox")
        self.browse_button = self.findChild(QPushButton, "browse_button")
        self.runGUI_button = self.findChild(QPushButton, "runGUI_button")
        self.progress_bar = self.findChild(QProgressBar, "progressBar")
        self.progress_bar.setVisible(False)

        self.data = None

        validator = GaussParamsValidator()
        self.sigma_edit.setValidator(validator)
        self.truncate_edit.setValidator(validator)

        self.browse_button.clicked.connect(self.browse_dir)
        self.runGUI_button.clicked.connect(self.run_GUI)
        self.gauss_checkbox.stateChanged.connect(self.check_gauss_state)

        self.show()

    def browse_dir(self):
        dir = QFileDialog.getExistingDirectory(self, caption="Select folder")
        if dir:
            self.dir_path_line.setText(dir)

    def run_GUI(self):
        dir = self.dir_path_line.text()
        filter = self.gauss_checkbox.isChecked()
        sigma = self.sigma_edit.text()
        truncate = self.truncate_edit.text()
        sampling_step = self.ds_spinbox.value()
        normalize = self.normalize_checkbox.isChecked()

        self.thread = QThread()
        self.fileReader = FileReader(dir, filter, sigma, truncate, sampling_step, normalize)
        self.fileReader.moveToThread(self.thread)

        self.thread.started.connect(self.fileReader.load_data)
        self.fileReader.finished.connect(self.thread.quit)
        self.fileReader.finished.connect(self.fileReader.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.fileReader.files_counter.connect(
            lambda count: self.progress_bar.setRange(1, count-1)
        )
        self.fileReader.progress.connect(
            lambda val: self.progress_bar.setValue(val)
        )

        self.thread.start()

        self.progress_bar.setVisible(True)
        self.enable_ui(False)
        self.label1.setText("Loading files. Please wait...")
        
        self.fileReader.finished.connect(
            lambda: self.set_data(self.fileReader.data)
        )

        self.thread.finished.connect(self.reset_ui)
    
    def check_gauss_state(self):
        if self.gauss_checkbox.isChecked():
            self.sigma_edit.setEnabled(True)
            self.truncate_edit.setEnabled(True)
        else:
            self.sigma_edit.setEnabled(False)
            self.truncate_edit.setEnabled(False)

    def set_data(self, data):
        self.data = data
    
    def enable_ui(self, bool_val):
        self.browse_button.setEnabled(bool_val)
        self.runGUI_button.setEnabled(bool_val)
        self.ds_spinbox.setEnabled(bool_val)
        self.gauss_checkbox.setEnabled(bool_val)
        self.normalize_checkbox.setEnabled(bool_val)
        self.dir_path_line.setEnabled(bool_val)
        self.sigma_edit.setEnabled(bool_val)
        self.truncate_edit.setEnabled(bool_val)

    def reset_ui(self):
        if self.data is not None:
            self.close()

        self.enable_ui(True)
        self.check_gauss_state()
        self.label1.setText("Enter a valid path to folder with data")
        self.progress_bar.setVisible(False)
    
    def get_params(self):
        return (self.data, self.ds_spinbox.value())


def display_error(message):
    ctypes.windll.user32.MessageBoxW(0, message, "Error", 0)


class GaussParamsValidator(QDoubleValidator):
    def __init__(self):
        super().__init__(bottom=0.01, decimals=3)
        
        locale = QLocale(QLocale.English, QLocale.UnitedStates)
        self.setLocale(locale)
        self.setNotation(QDoubleValidator.StandardNotation)
    
    def fixup(self, input):
        input = "1"
        return super().fixup(input)


if __name__ == '__main__':
    # Initialize the App
    app = QApplication(sys.argv)
    UIWindow = FileUI()
    app.exec_()