from UI_TrainWindow import Ui_UI_TrainWindow
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from pyqtgraph.flowchart import Flowchart
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import os

class TrainWindow(QtWidgets.QWidget, Ui_UI_TrainWindow):
    def __init__(self):
        super(TrainWindow, self).__init__()
        self.setupUi(self)
        with open("tmp.py", 'w') as self.f:
            self.f.write("import torch\nimport torch.nn as nn\n")
        self.model = dict()

    def load_model(self):
        print("load_model run")
        if self.model_to_load.currentIndex() == 1:
            filename, _ = QFileDialog.getOpenFileName(self, '加载模型', 'C:\\', 'Python Files (*.py)')
            filedir, filename_text = os.path.split(filename)
            self.f.write("From {} import Net\n".format(filename_text.split(".")[0]))
            self.log.append("从{}加载模型\n".format(filename))