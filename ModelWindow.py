from PyQt5 import QtWidgets
from pyqtgraph.flowchart import Flowchart
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import pyqtgraph.flowchart.library as fclib
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QRegExp
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QRegExpValidator
from UI_ModelWindow import Ui_ModelWindow
from UI_AddLayerWindow import Ui_AddLayerWindow
import os
import json
import networkx as nx
import numpy as np
import random
from FCNodes import CovNode, PoolNode, LinearNode, ConcatNode, Concat1dNode, SoftmaxNode, \
    LogSoftmaxNode, BachNorm1dNode, BachNorm2dNode, AddNode


class ModelWindow(QtWidgets.QMainWindow, Ui_ModelWindow):
    def __init__(self):
        super(ModelWindow, self).__init__()
        self.setupUi(self)
        self.global_id = 0
        self.nodes = dict()
        self.id_name = dict()
        self.name_id = dict()
        self.net = nx.DiGraph()
        self.library = fclib.LIBRARY.copy()
        self.library.addNodeType(CovNode, [('CovNode',)])
        self.library.addNodeType(PoolNode, [('PoolNode',)])
        self.library.addNodeType(LinearNode, [('LinearNode',)])
        self.library.addNodeType(ConcatNode, [('ConcatNode',)])
        self.library.addNodeType(Concat1dNode, [('Concat1dNode',)])
        self.library.addNodeType(SoftmaxNode, [('SoftmaxNode',)])
        self.library.addNodeType(LogSoftmaxNode, [('LogSoftmaxNode',)])
        self.library.addNodeType(BachNorm1dNode, [('BachNorm1dNode',)])
        self.library.addNodeType(BachNorm2dNode, [('BachNorm2dNode',)])
        self.library.addNodeType(AddNode, [('ResAddNode',)])
        self.type_name = {2:'Cov2d', 3:'Pool2d', 4:'Linear', 5:'Softmax', 6:'LogSoftmax', 7:'BachNorm1d',
                          8:'BachNorm2d', 9:'Res_Add', 10:'Concat2d', 11: 'Concat1d'}
        self.fc = Flowchart()
        self.fc.setLibrary(self.library)
        self.outputs = list()
        w = self.fc.widget()
        self.fc_inputs = dict()
        main_widget = QWidget()
        main_layout = QGridLayout()
        main_widget.setLayout(main_layout)
        self.detail = QTreeWidget()
        self.detail.setColumnCount(2)
        self.detail.setHeaderLabels(["属性", "值"])
        self.root = QTreeWidgetItem(self.detail)
        self.root.setText(0, "所有属性")
        main_layout.addWidget(self.fc.widget(), 0, 0, 1, 2)
        main_layout.addWidget(self.detail, 0, 2)
        self.setCentralWidget(main_widget)

    def add_layer(self):
        self.addlayer_window = AddLayerWindow()
        self.addlayer_window.datasignal.connect(self.accept_layer)
        self.addlayer_window.show()

    def accept_layer(self, data):
        if not data['type'] == 1:
            inputs = data['input'].split(";")
            data['input'] = list()
            for i in range(len(inputs)):
                try:
                    layer = self.name_id[inputs[i]]
                    if data['type'] == 3 and (self.nodes[inputs[i]]['type'] not in [2, 8, 9, 10]):
                        QMessageBox.warning(self, "错误", "输入：{}层类型不合法".format(inputs[i]))
                        return 0
                    elif (data['type'] in [5, 6, 7, 11]) and (self.nodes[inputs[i]]['type'] not in [4, 7, 11]):
                        QMessageBox.warning(self, "错误", "输入：{}层类型不合法".format(inputs[i]))
                        return 0
                    elif (data['type'] in [2, 8, 10]) and (self.nodes[inputs[i]]['type'] not in [1, 2, 3, 8, 9, 10]):
                        QMessageBox.warning(self, "错误", "输入：{}层类型不合法".format(inputs[i]))
                        return 0
                    data['input'].append(layer)
                except:
                    QMessageBox.warning(self, "错误", "输入来自未生成的层：{}".format(inputs[i]))
                    return 0
        else:
            data['input'] = list()
        if data['type'] == 9:
            layer_id = data['input'][0]
            cur_size = self.nodes[self.id_name[layer_id]]['para']['out_size']
            for layer_id in data['input']:
                layer = self.nodes[self.id_name[layer_id]]
                if layer['para']['out_size'] != cur_size:
                    QMessageBox.warning(self, "错误", "输入尺寸不匹配")
                    return 0
        if data['name'] in self.name_id.keys():
            id = self.name_id[data['name']]
            self.net.remove_node(id)
            self.net.add_node(id)
            for i in data['input']:
                self.net.add_edge(i, id)
            self.fc.removeNode(self.fc.nodes()[data['name']])
            data['ID'] = id
        else:
            data['ID'] = self.global_id
            self.name_id[data['name']] = self.global_id
            self.id_name[self.global_id] = data['name']
            self.net.add_node(self.global_id)
            for i in data['input']:
                self.net.add_edge(i, self.global_id)
            self.global_id += 1
        self.nodes[data['name']] = data
        if data['type'] == 1:
            self.fc.addInput(data['name'])
            self.fc_inputs[data['name']] = data['para']['out_size']
            self.fc.setInput(**self.fc_inputs)
        elif data['type'] in [9, 10, 11]:
            node = self.fc.createNode(self.type_name[data['type']], name=data['name'],
                                      pos=(data['input'][0] * 120, (data['ID'] - data['input'][0]) * 150 - 500))
            node.setPara(data['para'])
            node.setView(self.root)
            for i in data['input']:
                in_name = self.id_name[i]
                in_size = self.nodes[in_name]['para']['out_size']
                node.addInput(in_name)
                if self.nodes[in_name]['type'] == 1:
                    self.fc.connectTerminals(self.fc[in_name], node[in_name])
                else:
                    self.fc.connectTerminals(self.fc.nodes()[in_name]['dataOut'], node[in_name])
            if data['isoutput']:
                self.fc.addOutput(data['name'])
                self.fc.connectTerminals(node['dataOut'], self.fc[data['name']])
        else:
            node = self.fc.createNode(self.type_name[data['type']], name=data['name'],
                                          pos=(data['input'][0] * 120, (data['ID'] - data['input'][0]) * 150 - 500))
            node.setPara(data['para'])
            node.setView(self.root)
            if self.nodes[self.id_name[data['input'][0]]]['type'] == 1:
                self.fc.connectTerminals(self.fc[self.id_name[data['input'][0]]], node['dataIn'])
            else:
                self.fc.connectTerminals(self.fc.nodes()[self.id_name[data['input'][0]]]['dataOut'], node['dataIn'])
            if data['isoutput']:
                self.fc.addOutput(data['name'])
                self.fc.connectTerminals(node['dataOut'], self.fc[data['name']])
        if data['isoutput']:
            self.outputs.append(data['ID'])

    def export_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, '导出模型', 'C:\\', 'Python Files (*.py)')
        filedir, filename_text = os.path.split(filename)
        filename_text = filename_text.split(".")[0]
        sort = self.check()
        if sort is None:
            return 0
        content = list()
        for id in sort:
            content.append(self.nodes[self.id_name[id]])
        with open(filedir+'/'+filename_text+".json", 'w') as f1:
            json.dump(content, f1)
        with open(filename, 'w') as f:
            space = "    "
            f.write('import torch\nimport torch.nn as nn\nimport torch.nn.functional as F\n')
            f.write("class Net(nn.Module):\n")
            f.write(space+"def __init__(self):\n")
            f.write(space*2+"super(Net, self).__init__()\n")
            for id in sort:
                name = self.id_name[id]
                layer = self.nodes[name]
                if layer['type'] == 2:
                    f.write(space*2+"self."+layer['name']+" = nn.Conv2d(")
                    f.write(str(layer['para']['in_size'][0])+","+str(layer['para']['outchannels'])+","\
                            +str(layer['para']['kernel']))
                    for k, v in layer['para'].items():
                        if k in ['stride', 'padding', 'dilation', 'bias', 'padding_mode'] and v is not None:
                            f.write(","+k+"="+str(v))
                    f.write(")\n")
                elif layer['type'] == 3:
                    if layer['para']['type'] == "max":
                        f.write(space*2+"self."+layer['name']+" = nn.MaxPool2d(")
                        f.write(str(layer['para']['kernel']))
                        for k,v in layer['para'].items():
                            if k in ['stride', 'padding'] and v is not None:
                                f.write(","+k+"="+str(v))
                    elif layer['para']['type'] == "average":
                        f.write(space*2+"self."+layer['name']+" = nn.AvgPool2d(")
                        f.write(str(layer['para']['kernel']))
                        for k, v in layer['para'].items():
                            if k in ['stride', 'padding'] and v is not None:
                                f.write("," + k + "=" + str(v))
                    else:
                        f.write(space*2+"self."+layer['name']+" = nn.LPPool2d(")
                        f.write(str(layer['para']['power'])+",")
                        f.write(str(layer['para']['kernel']))
                        for k, v in layer['para'].items():
                            if k in ['stride', 'padding'] and v is not None:
                                f.write("," + k + "=" + str(v))
                    f.write(")\n")
                elif layer['type'] == 4:
                    f.write(space*2+"self."+layer['name']+" = nn.Linear(")
                    f.write(str(layer['para']['in_size'])+",")
                    f.write(str(layer['para']['out_features'])+",")
                    f.write("bias="+str(layer['para']['bias']))
                    f.write(")\n")
                elif layer['type'] == 7:
                    f.write(space * 2 + "self." + layer['name'] + " = nn.BatchNorm2d(")
                    f.write(str(layer['para']['in_size'])+",")
                    f.write("eps="+str(layer['para']['eps'])+",")
                    f.write("momentum=" + str(layer['para']['momentum']) + ",")
                    f.write("affine=" + str(layer['para']['affine']) + ",")
                    f.write("track_running_stats=" + str(layer['para']['track_running_stats']) + ")\n")
                elif layer['type'] == 8:
                    f.write(space * 2 + "self." + layer['name'] + " = nn.BatchNorm1d(")
                    f.write(str(layer['para']['in_size'][0]) + ",")
                    f.write("eps=" + str(layer['para']['eps']) + ",")
                    f.write("momentum=" + str(layer['para']['momentum']) + ",")
                    f.write("affine=" + str(layer['para']['affine']) + ",")
                    f.write("track_running_stats=" + str(layer['para']['track_running_stats']) + ")\n")
            #以下为forward函数
            f.write(space+"def forward(self")
            for input in self.fc_inputs.keys():
                f.write(","+input)
            f.write("):\n")
            for layer_id in sort:
                layer = self.nodes[self.id_name[layer_id]]
                if layer['type'] == 2 or layer['type'] == 4:
                    f.write(space*2+layer['name']+" = ")
                    inner_str = "self."+ layer['name'] + "(" + self.id_name[layer['input'][0]] + ")"
                    if layer['para']['activate'] != "None":
                        tmp = "F."+layer['para']['activate'] + "({})".format(inner_str)
                        inner_str = tmp
                    if layer['para']['dropout']:
                        tmp = "F.dropout({}, p=".format(inner_str)+str(layer['para']['dropout_radio'])+")"
                        inner_str = tmp
                    f.write(inner_str)
                    f.write("\n")
                elif layer['type'] == 3:
                    f.write(space*2+layer['name']+" = self.{}({})\n".format(layer['name'],
                                                                            self.id_name[layer['input'][0]]))
                elif layer['type'] == 5:
                    f.write(space*2+layer['name']+" = F.softmax({})\n".format(self.id_name[layer['input'][0]]))
                elif layer['type'] == 6:
                    f.write(space*2+layer['name']+" = F.log_softmax({})\n".format(self.id_name[layer['input'][0]]))



    def check(self):
        if len(self.outputs) == 0:
            return None
        return list(nx.topological_sort(self.net))


class AddLayerWindow(QtWidgets.QDialog, Ui_AddLayerWindow):
    datasignal = pyqtSignal(dict)

    def __init__(self):
        super(AddLayerWindow, self).__init__()
        self.setupUi(self)
        self.setFixedSize(433, 374)

    def fill_content(self):
        while self.content.count():
            child = self.content.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        if self.layertype.currentIndex() == 1:
            reg = QRegExp('[0-9]+$')
            pValidator = QRegExpValidator(self)
            pValidator.setRegExp(reg)
            label_h = QLabel("输入维度：h")
            label_w = QLabel("w:")
            label_c = QLabel("c:")
            self.sizeh = QLineEdit()
            self.sizew = QLineEdit()
            self.sizec = QLineEdit()
            self.sizeh.setValidator(pValidator)
            self.sizew.setValidator(pValidator)
            self.sizec.setValidator(pValidator)
            self.content.addWidget(label_h, 0, 0)
            self.content.addWidget(self.sizeh, 0, 1)
            self.content.addWidget(label_w, 0, 2)
            self.content.addWidget(self.sizew, 0, 3)
            self.content.addWidget(label_c, 0, 4)
            self.content.addWidget(self.sizec, 0, 5)
            self.content.addWidget(QLabel(" "), 1, 0)
        elif self.layertype.currentIndex() == 2:
            reg = QRegExp('[0-9]+$')
            pValidator = QRegExpValidator(self)
            pValidator.setRegExp(reg)
            # label_inchannels = QLabel("输入宽度:")
            label_outchannels = QLabel("卷积核数:")
            # self.inchannels = QLineEdit()
            self.outchannels = QLineEdit()
            # self.inchannels.setValidator(pValidator)
            self.outchannels.setValidator(pValidator)
            label_kernelsize = QLabel("卷积核大小:")
            label_X = QLabel("X")
            self.kernelheight = QLineEdit()
            self.kernelwidth = QLineEdit()
            self.kernelwidth.setValidator(pValidator)
            self.kernelheight.setValidator(pValidator)
            label_stride = QLabel("stride:")
            self.stride_1 = QLineEdit()
            self.stride_2 = QLineEdit()
            self.stride_1.setValidator(pValidator)
            self.stride_2.setValidator(pValidator)
            label_padding = QLabel("padding:")
            self.padding_1 = QLineEdit()
            self.padding_2 = QLineEdit()
            self.padding_1.setValidator(pValidator)
            self.padding_2.setValidator(pValidator)
            self.dilation = QCheckBox("dilation:")
            self.dilation_1 = QLineEdit()
            self.dilation_2 = QLineEdit()
            self.dilation_1.setValidator(pValidator)
            self.dilation_2.setValidator(pValidator)
            self.bias = QCheckBox("bias")
            label_paddingmode = QLabel("padding mode:")
            self.paddingmode = QComboBox()
            self.paddingmode.addItem("zeros")
            label_activate = QLabel("激活函数：")
            self.activate = QComboBox()
            self.activate.addItem("None")
            self.activate.addItem("relu")
            self.activate.addItem("gelu")
            self.activate.addItem("sigmoid")
            self.activate.addItem("logsigmoid")
            self.activate.addItem("tanh")
            self.use_dropout = QCheckBox("Dropout")
            self.dropout_radio = QLineEdit()
            self.dropout_radio.setText("0.5")
            self.content.addWidget(label_outchannels, 0, 0)
            self.content.addWidget(self.outchannels, 0, 1, 1, 3)
            self.content.addWidget(label_kernelsize, 1, 0)
            self.content.addWidget(self.kernelheight, 1, 1)
            self.content.addWidget(QLabel("X"), 1, 2)
            self.content.addWidget(self.kernelwidth, 1, 3)
            self.content.addWidget(label_stride, 2, 0)
            self.content.addWidget(self.stride_1, 2, 1)
            self.content.addWidget(QLabel("X"), 2, 2)
            self.content.addWidget(self.stride_2, 2, 3)
            self.content.addWidget(label_padding, 3, 0)
            self.content.addWidget(self.padding_1, 3, 1)
            self.content.addWidget(QLabel("X"), 3, 2)
            self.content.addWidget(self.padding_2, 3, 3)
            self.content.addWidget(self.dilation, 4, 0)
            self.content.addWidget(self.dilation_1, 4, 1)
            self.content.addWidget(QLabel("X"), 4, 2)
            self.content.addWidget(self.dilation_2, 4, 3)
            self.content.addWidget(label_paddingmode, 5, 0)
            self.content.addWidget(self.paddingmode, 5, 1)
            self.content.addWidget(self.bias, 5, 3)
            self.content.addWidget(label_activate, 6, 0)
            self.content.addWidget(self.activate, 6, 1)
            self.content.addWidget(self.use_dropout, 7, 0)
            self.content.addWidget(self.dropout_radio, 7, 1)
        elif self.layertype.currentIndex() == 3:
            reg = QRegExp('[0-9]+$')
            pValidator = QRegExpValidator(self)
            pValidator.setRegExp(reg)
            reg2 = QRegExp('[0-9.]+$')
            pValidator2 = QRegExpValidator(self)
            pValidator2.setRegExp(reg2)
            label_poolingtype = QLabel("池化类型：")
            self.poolingtype = QComboBox()
            self.poolingtype.addItem("average")
            self.poolingtype.addItem("max")
            self.poolingtype.addItem("LP")
            self.content.addWidget(label_poolingtype, 0, 0)
            self.content.addWidget(self.poolingtype, 0, 1)
            label_kernelsize = QLabel("卷积核大小:")
            self.kernelheight = QLineEdit()
            self.kernelwidth = QLineEdit()
            self.kernelwidth.setValidator(pValidator)
            self.kernelheight.setValidator(pValidator)
            self.content.addWidget(label_kernelsize, 1, 0)
            self.content.addWidget(self.kernelheight, 1, 1)
            self.content.addWidget(QLabel("X"), 1, 2)
            self.content.addWidget(self.kernelwidth, 1, 3)
            label_stride = QLabel("stride:")
            self.stride_1 = QLineEdit()
            self.stride_2 = QLineEdit()
            self.stride_1.setValidator(pValidator)
            self.stride_2.setValidator(pValidator)
            self.content.addWidget(label_stride, 2, 0)
            self.content.addWidget(self.stride_1, 2, 1)
            self.content.addWidget(QLabel("X"), 2, 2)
            self.content.addWidget(self.stride_2, 2, 3)
            label_padding = QLabel("padding:")
            self.padding_1 = QLineEdit()
            self.padding_2 = QLineEdit()
            self.padding_1.setValidator(pValidator)
            self.padding_2.setValidator(pValidator)
            self.content.addWidget(label_padding, 3, 0)
            self.content.addWidget(self.padding_1, 3, 1)
            self.content.addWidget(QLabel("X"), 3, 2)
            self.content.addWidget(self.padding_2, 3, 3)
            label_power = QLabel("power\n(仅适用于LP Pooling)")
            self.power = QLineEdit()
            self.power.setValidator(pValidator2)
            self.content.addWidget(label_power, 4, 0)
            self.content.addWidget(self.power, 4, 1)
        elif self.layertype.currentIndex() == 4:
            reg = QRegExp('[0-9]+$')
            pValidator = QRegExpValidator(self)
            pValidator.setRegExp(reg)
            label_out = QLabel("输出宽度：")
            self.out_features = QLineEdit()
            self.out_features.setValidator(pValidator)
            self.bias = QCheckBox("bias")
            label_activate = QLabel("激活函数：")
            self.activate = QComboBox()
            self.activate.addItem("None")
            self.activate.addItem("relu")
            self.activate.addItem("gelu")
            self.activate.addItem("sigmoid")
            self.activate.addItem("logsigmoid")
            self.activate.addItem("tanh")
            self.use_dropout = QCheckBox("Dropout")
            self.dropout_radio = QLineEdit()
            self.dropout_radio.setText("0.5")
            self.content.addWidget(label_out, 0, 0)
            self.content.addWidget(self.out_features, 0, 1)
            self.content.addWidget(self.bias, 0, 3)
            self.content.addWidget(label_activate, 1, 0)
            self.content.addWidget(self.activate, 1, 1)
            self.content.addWidget(self.use_dropout, 1, 2)
            self.content.addWidget(self.dropout_radio, 1, 3)
        elif self.layertype.currentIndex() == 7 or self.layertype.currentIndex() == 8:
            reg = QRegExp('[0-9e.-]+$')
            pValidator = QRegExpValidator(self)
            pValidator.setRegExp(reg)
            label_eps = QLabel("epsilon:")
            self.eps = QLineEdit()
            self.eps.setValidator(pValidator)
            self.eps.setText("1e-5")
            reg2 = QRegExp('[0-9.]+$')
            pValidator2 = QRegExpValidator(self)
            pValidator2.setRegExp(reg2)
            label_momentum = QLabel("momentum")
            self.momentum = QLineEdit()
            self.momentum.setValidator(pValidator2)
            self.momentum.setText("0.1")
            self.affine = QCheckBox("affine")
            self.track_running_stats = QCheckBox("track running stats")
            self.content.addWidget(label_eps, 0, 0)
            self.content.addWidget(self.eps, 0, 1)
            self.content.addWidget(label_momentum, 1, 0)
            self.content.addWidget(self.momentum, 1, 1)
            self.content.addWidget(self.affine, 2, 0)
            self.content.addWidget(self.track_running_stats, 3, 0)

    def gen_layer(self):
        send_data = True
        data = dict()
        if self.layername.text() == "":
            QMessageBox.warning(self, "警告", "不合法输入：未指定层的名字")
            send_data = False
        else:
            data['name'] = self.layername.text()
        if self.layertype.currentIndex() == 0:
            QMessageBox.warning(self, "警告", "不合法输入：未选择层的类型")
            send_data = False
        else:
            data['type'] = self.layertype.currentIndex()
        if self.layerinput.text() == "":
            QMessageBox.warning(self, "警告", "不合法输入：未指定层的输入")
            send_data = False
        elif self.layertype.currentIndex() not in [9, 10, 11] \
                and len(self.layerinput.text().split(";")) > 1:
            QMessageBox.warning(self, "警告", "不合法输入：输入多于一个")
            send_data = False
        else:
            data['input'] = self.layerinput.text()
        data['isoutput'] = self.layeroutput.isChecked()
        data['para'] = dict()
        if self.layertype.currentIndex() == 1:
            try:
                data['para']['out_size'] = (int(self.sizec.text()), int(self.sizeh.text()), int(self.sizew.text()))
            except:
                QMessageBox.warning(self, "警告", "不合法输入：输入维度均应为正整数")
                send_data = False
        elif self.layertype.currentIndex() == 2:
            try:
                data['para']['outchannels'] = int(self.outchannels.text())
            except:
                QMessageBox.warning(self, "警告", "不合法输入：输出宽度应为正整数")
                send_data = False
            try:
                data['para']['kernel'] = (int(self.kernelheight.text()), int(self.kernelwidth.text()))
            except:
                QMessageBox.warning(self, "警告", "不合法输入：卷积核大小均应为正整数")
                send_data = False
            try:
                data['para']['stride'] = (int(self.stride_1.text()), int(self.stride_2.text()))
            except:
                QMessageBox.warning(self, "警告", "不合法输入：stride参数均应为正整数")
                send_data = False
            try:
                data['para']['padding'] = (int(self.padding_1.text()), int(self.padding_2.text()))
            except:
                QMessageBox.warning(self, "警告", "不合法输入：padding参数均应为正整数")
                send_data = False
            if self.dilation.isChecked():
                try:
                    data['para']['dilation'] = (int(self.dilation_1.text()), int(self.dilation_2.text()))
                except:
                    QMessageBox.warning(self, "警告", "不合法输入：dilation参数均应为正整数")
                    send_data = False
            else:
                data['para']['dilation'] = None
            data['para']['activate'] = self.activate.currentText()
            data['para']['bias'] = self.bias.isChecked()
            data['para']['paddingmode'] = self.paddingmode.currentText()
            data['para']['dropout'] = self.use_dropout.isChecked()
            if data['para']['dropout']:
                try:
                    radio = float(self.dropout_radio.text())
                    if 0 <= radio <= 1:
                        data['para']['dropout_radio'] = radio
                    else:
                        QMessageBox.warning(self, "警告", "不合法输入：dropout参数应为0-1之间的数")
                        send_data = False
                except:
                    QMessageBox.warning(self, "警告", "不合法输入：dropout参数应为0-1之间的数")
                    send_data = False
        elif self.layertype.currentIndex() == 3:
            data['para']['type'] = self.poolingtype.currentText()
            try:
                data['para']['kernel'] = (int(self.kernelheight.text()), int(self.kernelwidth.text()))
            except:
                QMessageBox.warning(self, "警告", "不合法输入：卷积核大小均应为正整数")
                send_data = False
            try:
                data['para']['stride'] = (int(self.stride_1.text()), int(self.stride_2.text()))
            except:
                QMessageBox.warning(self, "警告", "不合法输入：stride参数均应为正整数")
                send_data = False
            try:
                data['para']['padding'] = (int(self.padding_1.text()), int(self.padding_2.text()))
            except:
                QMessageBox.warning(self, "警告", "不合法输入：padding参数均应为正整数")
                send_data = False
            if data['para']['type'] == "LP":
                try:
                    data['para']['power'] = self.power.text()
                except:
                    QMessageBox.warning(self, "警告", "不合法输入：power参数应为正整数")
                    send_data = False
        elif self.layertype.currentIndex() == 4:
            try:
                data['para']['out_features'] = int(self.out_features.text())
            except:
                QMessageBox.warning(self, "警告", "不合法输入：输出宽度应为正整数")
                send_data = False
            data['para']['bias'] = self.bias.isChecked()
            data['para']['activate'] = self.activate.currentText()
            data['para']['dropout'] = self.use_dropout.isChecked()
            if data['para']['dropout']:
                try:
                    radio = float(self.dropout_radio.text())
                    if 0 <= radio <= 1:
                        data['para']['dropout_radio'] = radio
                    else:
                        QMessageBox.warning(self, "警告", "不合法输入：dropout参数应为0-1之间的数")
                        send_data = False
                except:
                    QMessageBox.warning(self, "警告", "不合法输入：dropout参数输入格式错误")
                    send_data = False
        elif self.layertype.currentIndex() == 5 or self.layertype.currentIndex() == 6:
            data['para']['dim'] = -1
        elif self.layertype.currentIndex() == 7 or self.layertype.currentIndex() == 8:
            try:
                eps = float(self.eps.text())
                if 0 <= eps <= 1:
                    data['para']['eps'] = eps
                else:
                    QMessageBox.warning(self, "警告", "不合法输入：epsilon参数应为0-1之间的数")
                    send_data = False
            except:
                QMessageBox.warning(self, "警告", "不合法输入：epsilon参数输入格式错误")
                send_data = False
            try:
                momentum = float(self.momentum.text())
                if 0 <= momentum <= 1:
                    data['para']['momentum'] = momentum
                else:
                    QMessageBox.warning(self, "警告", "不合法输入：momentum参数应为0-1之间的数")
                    send_data = False
            except:
                QMessageBox.warning(self, "警告", "不合法输入：momentum参数输入格式错误")
                send_data = False
            data['para']['affine'] = self.affine.isChecked()
            data['para']['track_running_stats'] = self.track_running_stats.isChecked()
        if send_data:
            self.datasignal.emit(data)
            self.destroy()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    myshow = ModelWindow()
    myshow.show()
    sys.exit(app.exec_())
