from UI_TrainWindow import Ui_UI_TrainWindow
from UI_NewDatasetWindow import Ui_NewDatasetWindow
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from pyqtgraph.flowchart import Flowchart
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import os, shutil
import subprocess as sub
import torchvision
import sys
import re

class TrainWindow(QtWidgets.QWidget, Ui_UI_TrainWindow):
    def __init__(self):
        super(TrainWindow, self).__init__()
        self.setupUi(self)
        self.model = dict()
        self.dataset = dict()
        self.optim = dict()
        self.loss = dict()
        self.p = None
        self.data_x = list()
        self.data_loss = list()
        self.data_acc = list()
        self.curve = None
        reg = QRegExp('[0-9]+$')
        pValidator = QRegExpValidator(self)
        pValidator.setRegExp(reg)
        self.epochs = QLineEdit()
        self.epochs.setValidator(pValidator)
        self.show_every = QLineEdit()
        self.show_every.setValidator(pValidator)
        self.save_every = QLineEdit()
        self.save_every.setValidator(pValidator)
        self.bottom_layout.addWidget(QLabel("epochs"), 0 ,0)
        self.bottom_layout.addWidget(self.epochs, 0, 1)
        self.bottom_layout.addWidget(QLabel("显示频率:"), 1, 0)
        self.bottom_layout.addWidget(self.show_every, 1, 1)
        self.bottom_layout.addWidget(QLabel("储存频率:"), 2, 0)
        self.bottom_layout.addWidget(self.save_every, 2, 1)

    def load_model(self):
        while self.pretrained_layout.count():
            child = self.pretrained_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        if self.model_to_load.currentIndex() == 1:
            filename, _ = QFileDialog.getOpenFileName(self, '加载模型', '/', 'Python Files (*.py)')
            if filename is None or filename == "":
                return 0
            filedir, filename_text = os.path.split(filename)
            self.model['type'] = 1
            self.model['dir'] = filedir
            self.model['module'] = filename_text.split(".")[0]
            self.log.append("从{}加载模型Net\n".format(filename))
        else:
            self.is_pretrained = QCheckBox("使用预训练模型")
            self.pretrained_layout.addWidget(self.is_pretrained)
            self.model['type'] = self.model_to_load.currentIndex()
            self.model['name'] = self.model_to_load.currentText()
            self.log.append("加载模型:{}\n".format(self.model['name']))

    def load_dataset(self):
        while self.dataset_layout.count():
            child = self.dataset_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        if self.dataset_to_load.currentIndex() == 1:
            filename, _ = QFileDialog.getOpenFileName(self, '加载数据集', '/', 'Python Files (*.py)')
            if filename is None or filename == "":
                return 0
            filedir, filename_text = os.path.split(filename)
            self.dataset['type'] = 1
            self.dataset['dir'] = filedir
            self.dataset['module'] = filename_text.split(".")[0]
            self.log.append("从{}加载数据集MyDataset\n".format(filename))
        elif self.dataset_to_load.currentIndex() == 2:
            self.new_dataset = NewDatasetWindow()
            self.new_dataset.show()
        else:
            self.dataset['type'] = self.dataset_to_load.currentIndex()
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
        # label_sampler = QLabel("采样器(Sampler)")
        # self.sampler = QComboBox()
        # self.sampler.addItem("Sequential")
        # self.sampler.addItem("Random")
        # # self.sampler.addItem("自定义")
        self.dataset_layout.addWidget(self.resize, 0, 0)
        self.dataset_layout.addWidget(self.resize_h, 0, 1)
        self.dataset_layout.addWidget(QLabel("X"), 0, 2)
        self.dataset_layout.addWidget(self.resize_w, 0, 3)
        self.dataset_layout.addWidget(label_batch_size, 1, 0)
        self.dataset_layout.addWidget(self.batch_size, 1, 1)
        self.dataset_layout.addWidget(self.shuffle, 2, 0)
        self.dataset_layout.addWidget(self.drop_last, 2, 1)
        # self.dataset_layout.addWidget(label_sampler, 3, 0)
        # self.dataset_layout.addWidget(self.sampler, 3, 1)

    def load_loss_function(self):
        while self.loss_layout.count():
            child = self.loss_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        if self.loss_to_load.currentIndex() == 1:
            filename, _ = QFileDialog.getOpenFileName(self, '加载损失函数', '/', 'Python Files (*.py)')
            if filename is None or filename == "":
                return 0
            filedir, filename_text = os.path.split(filename)
            self.loss['type'] = 1
            self.loss['dir'] = filedir
            self.loss['module'] = filename_text.split(".")[0]
            self.log.append("从{}加载损失函数MyLoss\n".format(filename))
        elif self.loss_to_load.currentIndex() == 2:
            self.new_loss = NewLossWindow()
            self.new_loss.show()
        else:
            self.loss['type'] = self.loss_to_load.currentIndex()
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
        self.log.append("选定优化器:{}".format(self.optim_to_load.currentText()))
        self.optim['type'] = self.optim_to_load.currentIndex()
        self.optim['name'] = self.optim_to_load.currentText()
        if self.optim_to_load.currentIndex() == 1:
            self.optim['type'] = 1
            label_lr = QLabel("learning rate:")
            self.lr = QLineEdit()
            self.lr.setValidator(pValidator2)
            self.lr.setText("0.001")
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

    def start(self):
        if self.model_to_load.currentIndex() == 0:
            QMessageBox.warning(self, "警告", "未加载模型")
            return 0
        if self.dataset_to_load.currentIndex() == 0:
            QMessageBox.warning(self, "警告", "未加载数据集")
            return 0
        if self.loss_to_load.currentIndex() == 0:
            QMessageBox.warning(self, "警告", "未选择损失函数")
            return 0
        if self.optim_to_load.currentIndex() == 0:
            QMessageBox.warning(self, "警告", "未选择优化器")
            return 0
        appended_dirs = list()
        with open("tmp.py", 'w') as f:
            space = "    "
            f.write("import torch\nimport sys\nimport torchvision\nimport torchvision.transforms as transforms\n"
                    "import torch.optim as optim\nimport torch.nn as nn\nfrom torch.utils.data import DataLoader\n")
            f.write("device = torch.device(\"cuda:0\" if torch.cuda.is_available() else \"cpu\")\n")
            if self.model['type'] == 1:
                f.write("sys.path.append(r\'{}\')\n".format(self.model['dir']))
                appended_dirs.append(self.model['dir'])
                f.write("from {} import Net\n".format(self.model['module']))
                f.write("net = Net()\n")
                f.write("net.to(device)\n")
            else:
                f.write("import torchvision.models as models\n")
                if self.is_pretrained.isChecked():
                    f.write("net = models.{}(pretrained=True)\n".format(self.model['name']))
                else:
                    f.write("net = models.{}(pretrained=False)\n".format(self.model['name']))
            if self.resize_w.text() == "" or self.resize_h.text() == "" or self.resize is False:
                f.write("transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize"
                        "(mean=[0.485, 0.456, 0.406], std = [0.229, 0.224, 0.225])\n")
            else:
                f.write("transform = transforms.Compose([transforms.Resize(size=({},{}),transfroms.ToTensor(), "
                        "transforms.Normalize(mean=[0.485, 0.456, 0.406], std = [0.229, 0.224, 0.225])\n".format(
                    self.resize_h.text(), self.resize_w.text()
                ))
            if self.dataset['type'] == 1:
                if self.dataset['dir'] not in appended_dirs:
                    f.write("sys.path.append(r\'{}\')\n".format(self.dataset['dir']))
                    appended_dirs.append(self.dataset['dir'])
                f.write("from {} import MyDataset\n".format(self.dataset['module']))
                f.write("trainset = MyDataset()\n")
            elif self.dataset['type'] in [3, 7]:
                f.write("trainset = torchvision.datasets.{}(root={}, train=True, transform=transform, download="
                        "True)\n".format(self.dataset['name'], self.dataset['para']['root']))
            elif self.dataset['type'] in [4, 5]:
                f.write("trainset = torchvision.datasets.{0}(root={1}, annFile={1}, transform=transform)\n".format(
                    self.dataset['name'], self.dataset['para']['root']))
            elif self.dataset['type'] == 6:
                f.write("trainset = torchvision.datasets.{0}(root={1}, split=\'train\', download=True,"
                        "transform=transform)\n".format(self.dataset['name'], self.dataset['para']['root']))
            f.write("trainloader = DataLoader(trainset, batch_size={}, shuffle={}, drop_last={})\n".format(
                self.batch_size.text(), self.shuffle.text(), self.drop_last.isChecked()
            ))
            if self.loss['type'] == 1:
                if self.loss['dir'] not in appended_dirs:
                    f.write("sys.path.append(r\'{}\')\n".format(self.loss['dir']))
                    appended_dirs.append(self.loss['dir'])
                f.write("from {} import MyLoss\n".format(self.loss['module']))
                f.write("criterion = MyLoss()\n")
            elif self.loss_to_load.currentIndex() in [3, 4, 5, 6]:
                f.write("criterion = nn.{}(reduction={})\n".format(self.loss['name'], self.reduction.currentText()))
            elif self.loss_to_load.currentIndex() == 7:
                f.write("criterion = nn.{}(reduction={}, margin={}, eps={})\n".format(self.loss['name'],
                        self.reduction.currentText(), self.p.text(), self.eps.text()))
            if self.optim['type'] == 1:
                f.write("optimizer = optim.SGD(net.parameters(), lr={}, momentum={}, dempening={}, weight_decay={}, "
                        "nesterov={})\n".format(self.lr.text(), self.momuntum.text(), self.dampening.text()
                                                ,self.weight_decay.text(), self.nesterov.isChecked()))
            elif self.optim['type'] == 2:
                f.write("optimizer = optim.Adam(net.parameters(), lr={}, betas=({},{}), eps={}, weight_decay={}"
                        ", amsgrad={})\n".format(self.lr.text(), self.beta_1.text(), self.beta_2.text(),
                                                 self.eps.text(), self.weight_decay.text(), self.amsgrad.isChecked()))
            elif self.optim['type'] == 3:
                f.write("optimizer = optim.Adadelta(net.parameters(), lr={}, rho={}, eps={}, weight_decay={})\n".format(
                    self.lr.text(), self.rho.text(), self.eps.text(), self.weight_decay.text()))
            elif self.optm['type'] == 4:
                f.write("optimizer = optim.RMSprop(net.parameters(), lr={}, alpha={}, eps={}, weight_decay={},"
                        "momentum={}, centered={})\n".format(self.lr.text(), self.alpha.text(), self.eps.text(),
                                                          self.weight_decay.text(), self.momuntum.text(),
                                                          self.centered.isChecked()))
            if self.epochs.text() == "":
                f.write("epochs = 1000\n")
            else:
                f.write("epochs = {}\n".format(self.epochs.text()))
            if self.show_every.text() == "":
                f.write("show_every = 50\n")
            else:
                f.write("show_every = {}\n".format(self.show_every.text()))
            if self.save_every.text() == "":
                f.write("save_every = 100\n")
            else:
                f.write("save_every = {}\n".format(self.save_every.text()))
            f.write("for epoch in range(epochs):\n")
            f.write(space+"running_loss = 0.0\n")
            f.write(space+"for i, data in enumerate(trainLoader, 0):\n")
            f.write(space*2+"inputs, labels = data[0].to(device), data[1].to(device)\n")
            f.write(space*2+"optimizer.zero_grad()\n")
            f.write(space*2+"outputs = net(inputs)\n")
            f.write(space * 2 + "loss = criterion(outputs, labels)\n")
            f.write(space * 2 + "loss.backward()\n")
            f.write(space * 2 + "optimizer.step()\n")
            f.write(space * 2 + "running_loss += loss.item()\n")
            f.write(space*2+"if (i+1) % show_every == 0:\n")
            f.write(space * 3 + "print(\'epoch %d loss: %.3f\' % (epoch+1, running_loss))\n")
            f.write(space * 2 + "if (i+1) % save_every == 0:\n")
            f.write(space * 3 + "torch.save(net.state_dict(), \'\\save_model_{}\'.format(i+1))\n")
            self.p = sub.Popen("py -3 tmp.py", encoding='utf-8', stdout=sub.PIPE, stderr=sub.STDOUT)
            while True:
                buff = self.p.stdout.readline()
                if buff == '' and self.p.poll() != None:
                    break
                if buff != '':
                    self.log.append(buff)
                    self.cursor = self.log.textCursor()
                    self.log.moveCursor(self.cursor.End)
                    QApplication.processEvents()

    def stop(self):
        if self.p is not None and self.p.poll() is None:
            self.p.kill()

    def reset(self):
        pass

    def show_result(self):
        pass

    def load_script(self):
        has_set = False
        filename, _ = QFileDialog.getOpenFileName(self, '加载脚本', '/', 'Python Files (*.py)')
        if self.p is not None and self.p.poll() is None:
            self.p.kill()
        self.p = sub.Popen("py -3 {}".format(filename), stdout=sub.PIPE, stderr=sub.STDOUT, encoding='utf-8')
        while True:
            next_line = self.p.stdout.readline()
            if next_line == '' and self.p.poll() is not None:
                break
            if next_line != '':
                self.log.append(next_line)
                self.cursor = self.log.textCursor()
                self.log.moveCursor(self.cursor.End)
                QApplication.processEvents()
                patten = re.compile('([0-9]+(([.]?[0-9]*)|([eE]?[-]?[0-9]*)))')
                result = patten.findall(next_line)
                if len(result) >= 2:
                    if not has_set:
                        has_set = True
                        self.curve = PlotWindowCustom()
                        self.curve.setPw(1)
                        self.curve.show()
                    self.data_x.append(float(result[0][0]))
                    self.data_loss.append(float(result[1][0]))
                    self.curve.plot(data_x=self.data_x, data_y=self.data_loss)

    def save(self):
        filename, _ = QFileDialog.getSaveFileName(self, '导出脚本', '/', 'Python Files (*.py)')
        if filename is None or filename == "":
            return 0
        if os.path.exists('tmp.py'):
            shutil.copyfile('tmp.py', filename)

class NewDatasetWindow(QDialog, Ui_NewDatasetWindow):
    def __init__(self):
        super(NewDatasetWindow, self).__init__()
        self.setupUi(self)
        space = "    "
        self.codefield.setPlainText("from torch.utils.data import DataLoader, Dataset\n\nclass MyDataset(Dataset):\n")
        self.codefield.append(space+"def __init__(self):#初始化参数\n{}\n{}\n".format(space*2))
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
        filename, _ = QFileDialog.getSaveFileName(self, '储存损失函数', '/', 'Python Files (*.py)')
        text = self.codefield.toPlainText()
        with open(filename, 'w') as f:
            f.write(text)
        self.destroy()

    def reject(self):
        self.destroy()


class PlotWindowCustom(QMainWindow):
    def __init__(self):
        super(QMainWindow,self).__init__()
        self.resize(450, 350)
        self.setWindowTitle("训练图示")
        self.cw = QtGui.QWidget()
        self.setCentralWidget(self.cw)
        self.l = QtGui.QVBoxLayout()
        self.cw.setLayout(self.l)
        self.pw = pg.PlotWidget()
        self.l.addWidget(self.pw)

    def setPw(self, type):
        if type == 1:
            self.pw.setLabel('left', 'loss')
            self.pw.setLabel('bottom', 'epoch')

    def plot(self, data_x, data_y):
        self.pw.plot(x=data_x, y=data_y)