from ScansGUI import ScansGUI
from file_dialog import FileUI
import sys
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication
from pyqtgraph.Qt import mkQApp


if __name__ == '__main__':
    app = QApplication(sys.argv)
    file_window = FileUI()
    app.exec_()

    data, sampling_step = file_window.get_params()

    if data is None:
        sys.exit()

    mkQApp("Ultrasonic data visualization")
    gui = ScansGUI(data, sampling_step)

    pg.exec()
