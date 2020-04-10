from UI_TrainWindow import Ui_UI_TrainWindow
from UI_NewDatasetWindow import Ui_NewDatasetWindow
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
            self.log.append("从{}加载模型Net\n".format(filename))
        else:
            self.is_pretrained = QCheckBox("使用预训练模型")
            self.pretrained_layout.addWidget(self.is_pretrained)
            self.model['type'] = 2
            self.model['name'] = self.model_to_load.currentText()
            self.log.append("加载模型:{}\n".format(self.model['name']))

    def load_dataset(self):
        if self.dataset_to_load.currentIndex() == 1:
            filename, _ = QFileDialog.getOpenFileName(self, '加载数据集', 'C:\\', 'Python Files (*.py)')
            filedir, filename_text = os.path.split(filename)
            self.dataset['type'] = 1
            self.dataset['dir'] = filedir
            self.dataset['module'] = filename_text.split(".")[0]
            self.log.append("从{}加载数据集\n".format(filename))
        elif self.dataset_to_load.currentIndex() == 2:
            self.new_dataset = NewDatasetWindow()
            self.new_dataset.show()
        else:
            self.dataset['type'] = 2
            self.dataset['name'] = self.dataset_to_load.currentText()
            filename, _ = QFileDialog.getExistingDirectory(self, caption="下载数据集", directory="/")
            filedir, filename_text = os.path.split(filename)
            self.log.append("加载数据集:{}".format(self.dataset['name']))
            if self.dataset_to_load.currentIndex() == 3:
                self.root =
                self.dataset_layout.addWidget()
        reg = QRegExp('[0-9]+$')
        pValidator = QRegExpValidator(self)
        pValidator.setRegExp(reg)
        label_batch_size = QLabel("batch size:")
        self.batch_size = QLineEdit()
        self.batch_size.setValidator(pValidator)
        self.shuffle = QCheckBox("shuffle")


    def load_loss_function(self):
        pass

    def load_optim(self):
        pass


class NewDatasetWindow(QDialog, Ui_NewDatasetWindow):
    def __init__(self):
        super(NewDatasetWindow, self).__init__()
        self.setupUi(self)
        space = "    "
        self.codefield.setPlainText("from torch.utils.data import DataLoader, Dataset\n\nclass MyDataset(Dataset):\n")
        self.codefield.append(space+"def __init__(self, root_dir, transform=None):#初始化参数\n\n\n")
        self.codefield.append(space+"def __len__(self):#返回整个数据集的大小\n\n\n")
        self.codefield.append(space+"def __getitem__(self, index):#根据索引index返回dataset[index]\n\n\n")

    def accept(self):
        filename, _ = QFileDialog.getSaveFileName(self, '储存数据集', 'C:\\', 'Python Files (*.py)')
        text = self.codefield.toPlainText()
        with open(filename, 'w') as f:
            f.write(text)
        self.destroy()

    def reject(self):
        self.destroy()