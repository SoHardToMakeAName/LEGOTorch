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
        self.model = dict()
        self.dataset = dict()
        self.optim = dict()
        self.loss_function = dict()

    def load_model(self):
        if self.model_to_load.currentIndex() == 1:
            filename, _ = QFileDialog.getOpenFileName(self, '加载模型', 'C:\\', 'Python Files (*.py)')
            filedir, filename_text = os.path.split(filename)
            self.model['type'] = 1
            self.model['dir'] = filedir
            self.model['module'] = filename_text.split(".")[0]
            for k, v in self.model.items():
                print(k, v)
        else:
            self.is_pretrained = QCheckBox("使用预训练模型")
            self.pretrained_layout.addWidget(self.is_pretrained)
            self.model['type'] = 2
            self.model['name'] = self.model_to_load.currentText()
            for k, v in self.model.items():
                print(k, v)

    def load_dataset(self):
        pass

    def load_loss_function(self):
        pass

    def load_optim(self):
        pass