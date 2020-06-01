from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from UI_TestWindow import Ui_TestWindow2
import os
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
import subprocess as sub
import threading

class TestWindow(QDialog, Ui_TestWindow2):#测试界面对应的类
    def __init__(self):
        super(TestWindow, self).__init__()
        self.setupUi(self)
        self.p = None
        self.model = dict()
        self.dataset = dict()
        self.script = None
        self.param_path = None

    def run_script(self, filename='tmp2.py'):#创建子进程运行脚本
        print("run_script starts!")
        if self.p is not None and self.p.poll() is None:
            self.p.kill()
        self.p = sub.Popen("python {}".format(filename), encoding='utf-8', stdout=sub.PIPE, stderr=sub.STDOUT)
        while True:
            buff = self.p.stdout.readline()
            print(buff)
            if buff == '' and self.p.poll() != None:
                break
            if buff != '':
                self.log.append(buff)
                QApplication.processEvents()

    def load_model(self):#加载模型的槽函数
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
            self.model['type'] = self.model_to_load.currentIndex()
            self.model['name'] = self.model_to_load.currentText()
            self.log.append("加载模型:{}\n".format(self.model['name']))

    def load_param(self):#加载参数的槽函数
        filename, _ = QFileDialog.getOpenFileName(self, '加载模型参数', '/', 'Model state dict (*.pth)')
        if filename is None or filename == "":
            return 0
        self.param_path = filename
        self.log.append("加载模型参数：{}".format(filename))

    def load_acc(self):#加载测试脚本的槽函数
        if self.acc_to_load.currentIndex() == 1:
            filename, _ = QFileDialog.getOpenFileName(self, '自定义脚本', '/', 'Python File (*.py)')
            if filename is None or filename == "":
                return 0
            self.script = filename
            self.log.append("加载脚本:{}".format(filename))

    def load_dataset(self):#加载数据集的槽函数
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
        else:
            self.dataset['type'] = self.dataset_to_load.currentIndex()
            self.dataset['name'] = self.dataset_to_load.currentText()
            filename = QFileDialog.getExistingDirectory(self, caption="下载数据集", directory="/")
            self.log.append("加载数据集:{}, 路径为:{}".format(self.dataset['name'], filename))
            self.dataset['para'] = dict()
            self.dataset['para']['root'] = filename
            self.dataset['para']['train'] = True
            if self.dataset_to_load.currentIndex() == 4:
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

    def start(self):#运行默认的测试脚本
        if self.acc_to_load.currentIndex() == 1:
            self.run_script(filename=self.script)
        else:
            if self.dataset_to_load.currentIndex() == 0:
                QMessageBox.warning(self, "警告", "未加载数据集")
                return 0
            if self.model_to_load.currentIndex() == 0:
                QMessageBox.warning(self, "警告", "未加载模型")
                return 0
            if self.param_path is None:
                QMessageBox.warning(self, "警告", "未加载模型参数")
                return 0
            if self.acc_to_load.currentIndex() == 1:
                self.run_script(filename=self.script)
            space = "    "
            appended_dirs = list()
            with open("tmp2.py", 'w') as f:
                f.write("import torch\nimport sys\nimport torchvision\nimport torchvision.transforms as transforms\n"
                    "import torch.optim as optim\nimport torch.nn as nn\nfrom torch.utils.data import DataLoader\n")
                if self.use_GPU.isChecked():
                    f.write("device = torch.device(\"cuda:0\" if torch.cuda.is_available() else \"cpu\")\n")
                else:
                    f.write("device = torch.device(\"cpu\")\n")
                if self.resize_w.text() == "" or self.resize_h.text() == "" or self.resize is False:
                    f.write("transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize"
                            "(mean=[0.485, 0.456, 0.406], std = [0.229, 0.224, 0.225])])\n")
                else:
                    f.write("transform = transforms.Compose([transforms.Resize(size=({},{}),transfroms.ToTensor(), "
                            "transforms.Normalize(mean=[0.485, 0.456, 0.406], std = [0.229, 0.224, 0.225])])\n".format(
                        self.resize_h.text(), self.resize_w.text()
                    ))
                if self.dataset['type'] == 1:
                    if self.dataset['dir'] not in appended_dirs:
                        f.write("sys.path.append(r\'{}\')\n".format(self.dataset['dir']))
                        appended_dirs.append(self.dataset['dir'])
                    f.write("from {} import MyDataset\n".format(self.dataset['module']))
                    f.write("testset = MyDataset()\n")
                elif self.dataset['type'] in [2, 4]:
                    f.write("testset = torchvision.datasets.{}(root=\'{}\', train=False, transform=transform, download="
                            "True)\n".format(self.dataset['name'], self.dataset['para']['root']))
                elif self.dataset['type'] == 3:
                    f.write("testset = torchvision.datasets.{0}(root={1}, split=\'val\', download=True,"
                            "transform=transform)\n".format(self.dataset['name'], self.dataset['para']['root']))
                f.write("testloader = DataLoader(testset, batch_size={}, shuffle={}, drop_last={})\n".format(
                    self.batch_size.text(), self.shuffle.isChecked(), self.drop_last.isChecked()
                ))
                if self.model['type'] == 1:
                    f.write("sys.path.append(r\'{}\')\n".format(self.model['dir']))
                    appended_dirs.append(self.model['dir'])
                    f.write("from {} import Net\n".format(self.model['module']))
                    f.write("net = Net()\n")
                    f.write("net.to(device)\n")
                else:
                    f.write("import torchvision.models as models\n")
                    f.write("net = models.{}(pretrained=False)\n".format(self.model['name']))
                f.write("net.load_state_dict(torch.load(\'{}\'))\n".format(self.param_path))
                f.write("correct = 0\n")
                f.write("total = 0\n")
                f.write("with torch.no_grad():\n")
                f.write(space+"for data in testloader:\n")
                f.write(space*2+"images, labels = data[0].to(device), data[1].to(device)\n")
                f.write(space*2+"outputs = net(images)\n")
                f.write(space*2+"_, predicted = torch.max(outputs.data, 1)\n")
                f.write(space*2+"total += labels.size(0)\n")
                f.write(space * 2 + "correct += (predicted == labels).sum().item()\n")
                f.write("print(\'Accuracy of the network on the testset: %d %%\' % (100 * correct / total))\n")
            t = threading.Thread(target=self.run_script, name='t', daemon=True)
            t.start()