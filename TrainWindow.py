from UI_TrainWindow import Ui_UI_TrainWindow
from UI_NewDatasetWindow import Ui_NewDatasetWindow
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
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
        self.loss = dict()

    def load_model(self):
        if self.model_to_load.currentIndex() == 1:
            filename, _ = QFileDialog.getOpenFileName(self, '加载模型', '/', 'Python Files (*.py)')
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
            filename, _ = QFileDialog.getOpenFileName(self, '加载数据集', '/', 'Python Files (*.py)')
            filedir, filename_text = os.path.split(filename)
            self.dataset['type'] = 1
            self.dataset['dir'] = filedir
            self.dataset['module'] = filename_text.split(".")[0]
            self.log.append("从{}加载数据集MyDataset\n".format(filename))
        elif self.dataset_to_load.currentIndex() == 2:
            self.new_dataset = NewDatasetWindow()
            self.new_dataset.show()
        else:
            self.dataset['type'] = 2
            self.dataset['name'] = self.dataset_to_load.currentText()
            filename = QFileDialog.getExistingDirectory(self, caption="下载数据集", directory="/")
            self.log.append("加载数据集:{}, 路径为:{}".format(self.dataset['name'], filename))
            self.dataset['para'] = dict()
            self.dataset['para']['root'] = filename
            self.dataset['para']['train'] = True
            if self.dataset_to_load.currentIndex() in [4, 5]:
                self.dataset['para']['annFile'] = self.dataset['para']['root']
            elif self.dataset_to_load.currentIndex() == 6:
                self.dataset['para']['split'] = 'train'
        reg = QRegExp('[0-9]+$')
        pValidator = QRegExpValidator(self)
        pValidator.setRegExp(reg)
        self.resize = QCheckBox("resize:")
        self.resize_h = QLineEdit()
        self.resize_h.setValidator(pValidator)
        self.resize_w = QLineEdit()
        self.resize_w.setValidator(pValidator)
        label_batch_size = QLabel("batch size:")
        self.batch_size = QLineEdit()
        self.batch_size.setValidator(pValidator)
        self.shuffle = QCheckBox("shuffle")
        self.drop_last = QCheckBox("drop last")
        label_sampler = QLabel("采样器(Sampler)")
        self.sampler = QComboBox()
        self.sampler.addItem("Sequential")
        self.sampler.addItem("Random")
        self.sampler.addItem("自定义")
        self.dataset_layout.addWidget(self.resize, 0, 0)
        self.dataset_layout.addWidget(self.resize_h, 0, 1)
        self.dataset_layout.addWidget(QLabel("X"), 0, 2)
        self.dataset_layout.addWidget(self.resize_w, 0, 3)
        self.dataset_layout.addWidget(label_batch_size, 1, 0)
        self.dataset_layout.addWidget(self.batch_size, 1, 1)
        self.dataset_layout.addWidget(self.shuffle, 2, 0)
        self.dataset_layout.addWidget(self.drop_last, 2, 1)
        self.dataset_layout.addWidget(label_sampler, 3, 0)
        self.dataset_layout.addWidget(self.sampler, 3, 1)

    def load_loss_function(self):
        if self.loss_to_load.currentIndex() == 1:
            filename, _ = QFileDialog.getOpenFileName(self, '加载损失函数', '/', 'Python Files (*.py)')
            filedir, filename_text = os.path.split(filename)
            self.loss['type'] = 1
            self.loss['dir'] = filedir
            self.loss['module'] = filename_text.split(".")[0]
            self.log.append("从{}加载损失函数MyLoss\n".format(filename))
        elif self.loss_to_load.currentIndex() == 2:
            self.new_loss = NewLossWindow()
            self.new_loss.show()
        else:
            self.loss['type'] = 2
            self.loss['name'] = self.loss_to_load.currentText()
            self.log.append("选定损失函数为:{}\n".format(self.loss['name']))
            if self.loss_to_load.currentIndex() in [3, 4, 5, 6]:
                label_reduction = QLabel("reduction:")
                self.reduction = QComboBox()
                self.reduction.addItem("none")
                self.reduction.addItem("mean")
                self.reduction.addItem("sum")
                self.loss_layout.addWidget(label_reduction, 0, 0)
                self.loss_layout.addWidget(self.reduction, 0, 1)
            elif self.loss_to_load.currentIndex() == 7:
                reg = QRegExp('[0-9]+$')
                pValidator = QRegExpValidator(self)
                pValidator.setRegExp(reg)
                reg2 = QRegExp('[0-9.]+$')
                pValidator2 = QRegExpValidator(self)
                pValidator2.setRegExp(reg2)
                label_margin = QLabel("margin:")
                self.margin = QLineEdit()
                self.margin.setValidator(pValidator2)
                self.margin.setText("1")
                label_p = QLabel("p:")
                self.p = QLineEdit()
                self.p.setValidator(pValidator)
                self.p.setText("2")
                label_reduction = QLabel("reduction:")
                self.reduction = QComboBox()
                self.reduction.addItem("none")
                self.reduction.addItem("mean")
                self.reduction.addItem("sum")
                self.loss_layout.addWidget(label_margin, 0, 0)
                self.loss_layout.addWidget(self.margin, 0, 1)
                self.loss_layout.addWidget(label_p, 1, 0)
                self.loss_layout.addWidget(self.p, 1, 1)
                self.loss_layout.addWidget(label_reduction, 2, 0)
                self.loss_layout.addWidget(self.margin, 2, 1)

    def load_optim(self):
        pass


class NewDatasetWindow(QDialog, Ui_NewDatasetWindow):
    def __init__(self):
        super(NewDatasetWindow, self).__init__()
        self.setupUi(self)
        space = "    "
        self.codefield.setPlainText("from torch.utils.data import DataLoader, Dataset\n\nclass MyDataset(Dataset):\n")
        self.codefield.append(space+"def __init__(self, root_dir, transform=None):#初始化参数\n{}\n{}\n".format(space*2))
        self.codefield.append(space+"def __len__(self):#返回整个数据集的大小\n{}\n{}\n".format(space*2))
        self.codefield.append(space+"def __getitem__(self, index):#根据索引index返回dataset[index]\n{}\n{}\n".format(space*2))

    def accept(self):
        filename, _ = QFileDialog.getSaveFileName(self, '储存数据集', '/', 'Python Files (*.py)')
        text = self.codefield.toPlainText()
        with open(filename, 'w') as f:
            f.write(text)
        self.destroy()

    def reject(self):
        self.destroy()

class NewLossWindow(QDialog, Ui_NewDatasetWindow):
    def __init__(self):
        super(NewDatasetWindow, self).__init__()
        self.setupUi(self)
        space = "    "
        self.codefield.setPlainText("import torch\nimport torch.nn as nn\nimport torch.nn.functional as F\n\n")
        self.codefield.append("class MyLoss(nn.Moudle):\n")
        self.codefield.append(space+"def __init__(self):#定义超参数\n{}\n{}\n".format(space*2))
        self.codefield.append(space+"def forward(self):#定义计算过程\n{}\n{}\n".format(space*2))
        self.codefield.append(space*2+"return ")

    def accept(self):
        filename, _ = QFileDialog.getSaveFileName(self, '储存数据集', '/', 'Python Files (*.py)')
        text = self.codefield.toPlainText()
        with open(filename, 'w') as f:
            f.write(text)
        self.destroy()

    def reject(self):
        self.destroy()