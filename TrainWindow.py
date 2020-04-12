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
        while self.pretrained_layout.count():
            child = self.pretrained_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
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
        while self.dataset_layout.count():
            child = self.dataset_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
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
        while self.loss_layout.count():
            child = self.loss_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
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
                reg2 = QRegExp('^[0-9]+(([.]?[0-9]*)|([eE]?[-]?[0-9]*))$')
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
                self.loss_layout.addWidget(self.reduction, 2, 1)

    def load_optim(self):
        while self.optim_layout.count():
            child = self.optim_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        reg2 = QRegExp('^[0-9]+(([.]?[0-9]*)|([eE]?[-]?[0-9]*))$')
        pValidator2 = QRegExpValidator(self)
        pValidator2.setRegExp(reg2)
        if self.optim_to_load.currentIndex() == 1:
            label_lr = QLabel("learning rate:")
            self.lr = QLineEdit()
            self.lr.setValidator(pValidator2)
            label_momentum = QLabel("momentum:")
            self.momuntum = QLineEdit()
            self.momuntum.setValidator(pValidator2)
            self.momuntum.setText("0")
            label_dampening = QLabel("dampening:")
            self.dampening = QLineEdit()
            self.dampening.setValidator(pValidator2)
            self.dampening.setText("0")
            label_weight_decay = QLabel("weight_decay:")
            self.weight_decay = QLineEdit()
            self.weight_decay.setValidator(pValidator2)
            self.weight_decay.setText("0")
            self.nesterov = QCheckBox("使用Nesterov momentum")
            self.optim_layout.addWidget(label_lr, 0, 0)
            self.optim_layout.addWidget(self.lr, 0, 1)
            self.optim_layout.addWidget(label_momentum, 0, 2)
            self.optim_layout.addWidget(self.momuntum, 0, 3)
            self.optim_layout.addWidget(label_dampening, 1, 0)
            self.optim_layout.addWidget(self.dampening, 1, 1)
            self.optim_layout.addWidget(label_weight_decay, 1, 2)
            self.optim_layout.addWidget(self.weight_decay, 1, 3)
            self.optim_layout.addWidget(self.nesterov, 2, 0)
        elif self.optim_to_load.currentIndex() == 2:
            label_lr = QLabel("learning rate:")
            self.lr = QLineEdit()
            self.lr.setValidator(pValidator2)
            self.lr.setText("0.001")
            label_beta_1 = QLabel("beta_1:")
            label_beta_2 = QLabel("beta_2:")
            self.beta_1 = QLineEdit()
            self.beta_1.setValidator(pValidator2)
            self.beta_1.setText("0.9")
            self.beta_2 = QLineEdit()
            self.beta_2.setValidator(pValidator2)
            self.beta_2.setText("0.999")
            label_eps = QLabel("epsilon:")
            self.eps = QLineEdit()
            self.eps.setValidator(pValidator2)
            self.eps.setText("1e-8")
            label_weight_decay = QLabel("weight decay:")
            self.weight_decay = QLineEdit()
            self.weight_decay.setValidator(pValidator2)
            self.weight_decay.setText("0")
            self.amsgrad = QCheckBox("使用AMSGrad")
            self.optim_layout.addWidget(label_lr, 0, 0)
            self.optim_layout.addWidget(self.lr, 0, 1)
            self.optim_layout.addWidget(label_eps, 0, 2)
            self.optim_layout.addWidget(self.eps, 0, 3)
            self.optim_layout.addWidget(label_beta_1, 1, 0)
            self.optim_layout.addWidget(self.beta_1, 1, 1)
            self.optim_layout.addWidget(label_beta_2, 1, 2)
            self.optim_layout.addWidget(self.beta_2, 1, 3)
            self.optim_layout.addWidget(label_weight_decay, 2, 0)
            self.optim_layout.addWidget(self.weight_decay, 2, 1)
            self.optim_layout.addWidget(self.amsgrad, 2, 2)
        elif self.optim_to_load.currentIndex() == 3:
            label_lr = QLabel("learning rate:")
            self.lr = QLineEdit()
            self.lr.setValidator(pValidator2)
            self.lr.setText("1.0")
            label_rho = QLabel("rho:")
            self.rho = QLineEdit()
            self.rho.setValidator(pValidator2)
            self.rho.setText("0.9")
            label_eps = QLabel("epsilon:")
            self.eps = QLineEdit()
            self.eps.setValidator(pValidator2)
            self.eps.setText("1e-6")
            label_weight_decay = QLabel("weight decay:")
            self.weight_decay = QLineEdit()
            self.weight_decay.setValidator(pValidator2)
            self.weight_decay.setText("0")
            self.optim_layout.addWidget(label_lr, 0, 0)
            self.optim_layout.addWidget(self.lr, 0, 1)
            self.optim_layout.addWidget(label_rho, 0, 2)
            self.optim_layout.addWidget(self.rho, 0, 3)
            self.optim_layout.addWidget(label_eps, 1, 0)
            self.optim_layout.addWidget(self.eps, 1, 1)
            self.optim_layout.addWidget(label_weight_decay, 1, 2)
            self.optim_layout.addWidget(self.weight_decay, 1, 3)
        elif self.optim_to_load.currentIndex() == 3:
            label_lr = QLabel("learning rate:")
            self.lr = QLineEdit()
            self.lr.setValidator(pValidator2)
            self.lr.setText("0.01")
            label_alpha = QLabel("alpha:")
            self.alpha = QLineEdit()
            self.alpha.setValidator(pValidator2)
            self.alpha.setText("0.99")
            label_eps = QLabel("epsilon:")
            self.eps = QLineEdit()
            self.eps.setValidator(pValidator2)
            self.eps.setText("1e-8")
            label_weight_decay = QLabel("weight decay:")
            self.weight_decay = QLineEdit()
            self.weight_decay.setValidator(pValidator2)
            self.weight_decay.setText("0")
            label_momentum = QLabel("momentum:")
            self.momuntum = QLineEdit()
            self.momuntum.setValidator(pValidator2)
            self.momuntum.setText("0")
            self.centered = QCheckBox("使用centered RMSprop")
            self.optim_layout.addWidget(label_lr, 0, 0)
            self.optim_layout.addWidget(self.lr, 0, 1)
            self.optim_layout.addWidget(label_alpha, 0, 2)
            self.optim_layout.addWidget(self.alpha, 0, 3)
            self.optim_layout.addWidget(label_eps, 1, 0)
            self.optim_layout.addWidget(self.eps, 1, 1)
            self.optim_layout.addWidget(label_momentum, 1, 2)
            self.optim_layout.addWidget(self.momuntum, 1, 3)
            self.optim_layout.addWidget(label_weight_decay, 2, 0)
            self.optim_layout.addWidget(self.weight_decay, 2, 1)
            self.optim_layout.addWidget(self.centered, 2, 2)


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