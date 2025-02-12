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
from TrainWindow import TrainWindow
from TestWindow import TestWindow
import os
import json
import networkx as nx
import numpy as np
import random
from FCNodes import CovNode, PoolNode, LinearNode, ConcatNode, Concat1dNode, SoftmaxNode, \
    LogSoftmaxNode, BachNorm1dNode, BachNorm2dNode, AddNode, IdentityNode


class ModelWindow(QtWidgets.QMainWindow, Ui_ModelWindow):#模型界面对应的类
    def __init__(self):
        super(ModelWindow, self).__init__()
        self.setupUi(self)
        self.global_id = 0#每个层对应的唯一ID，用于基于DAG图的校验和代码生成
        self.nodes = dict()#所有层的信息
        self.id_name = dict()#ID-名字映射
        self.name_id = dict()#名字-ID映射
        self.net = nx.DiGraph()#图，节点为层的ID
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
        self.library.addNodeType(IdentityNode, [('IdentityNode',)])
        self.type_name = {2:'Cov2d', 3:'Pool2d', 4:'Linear', 5:'Softmax', 6:'LogSoftmax', 7:'BachNorm1d',
                          8:'BachNorm2d', 9:'Res_Add', 10:'Concat2d', 11: 'Concat1d', 12: 'Identity'}
        self.fc = Flowchart()#模型可视化的流程图，对应FlowChart按钮
        self.fc.setLibrary(self.library)#引入FCNodes.py中定义的Node
        self.outputs = list()#模型所有输出
        w = self.fc.widget()
        self.fc_inputs = dict()#self.fc流程图的输入
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

    def add_layer(self):#用于弹出“层-新建”动作对应的层操作界面
        self.addlayer_window = AddLayerWindow()
        self.addlayer_window.datasignal.connect(self.accept_layer)
        self.addlayer_window.show()

    def modifiey_layer(self):#用于弹出“层-更改”动作对应的层操作界面
        self.addlayer_window = AddLayerWindow()
        self.addlayer_window.datasignal.connect(self.accept_layer)
        self.addlayer_window.layertype.addItem("恒等层(Identity)")
        self.addlayer_window.show()

    def clear(self):#对应“层-清除”，清除当前模型
        self.fc.clear()
        self.id_name = dict()
        self.name_id = dict()
        self.nodes = dict()
        self.net = nx.DiGraph()
        self.fc.clear()
        self.fc_inputs = dict()
        self.global_id = 0
        self.outputs = list()
        self.detail.clear()
        self.detail.setColumnCount(2)
        self.detail.setHeaderLabels(["属性", "值"])
        self.root = QTreeWidgetItem(self.detail)
        self.root.setText(0, "所有属性")

    def to_train(self):#对应“功能-训练”动作，跳转到训练界面
        self.train_window = TrainWindow()
        self.train_window.show()

    def to_test(self):#对应“功能-测试”动作，跳转到测试界面
        self.test_window  = TestWindow()
        self.test_window.show()

    def accept_layer(self, data):#接收层操作界面中信号的槽函数，接收层操作界面传来的数据并显示在该界面上
        reset_flag = False
        if not data['type'] in [1, 12]:#对输入层和恒等层不检查输入
            inputs = data['input'].split(";")
            data['input'] = list()
            for i in range(len(inputs)):#判断连接是否合法
                try:
                    name = inputs[i]
                    layer = self.name_id[name]
                    if data['type'] == 3 and (self.nodes[inputs[i]]['type'] not in [2, 8, 9, 10]):
                        QMessageBox.warning(self, "错误", "输入：{}层类型不合法".format(inputs[i]))
                        return 0
                    elif (data['type'] in [5, 6, 7, 11]) and (self.nodes[inputs[i]]['type'] not in [4, 7, 11]):
                        QMessageBox.warning(self, "错误", "输入：{}层类型不合法".format(inputs[i]))
                        return 0
                    elif (data['type'] in [2, 8, 10]) and (self.nodes[inputs[i]]['type'] not in [1, 2, 3, 8, 9, 10]):
                        QMessageBox.warning(self, "错误", "输入：{}层类型不合法".format(inputs[i]))
                        return 0
                    data['input'].append(layer)#将input中的层名替换为对应的ID
                except:
                    QMessageBox.warning(self, "错误", "输入来自未生成的层：{}".format(inputs[i]))
                    return 0
        else:
            data['input'] = list()
        if data['type'] == 9:#残差连接层判断两个输入size是否相同
            layer_id = data['input'][0]
            cur_size = self.nodes[self.id_name[layer_id]]['para']['out_size']
            for layer_id in data['input']:
                layer = self.nodes[self.id_name[layer_id]]
                if layer['para']['out_size'] != cur_size:
                    QMessageBox.warning(self, "错误", "输入尺寸不匹配")
                    return 0
        if data['name'] in self.name_id.keys():#替换同名层的情形
            id = self.name_id[data['name']]
            for input_id in data['input']:
                if input_id >= id:
                    QMessageBox.warning(self, "错误", "输入来自后继层")
                    return 0
            if data['type'] == 12:
                data['para']['former_type'] = self.nodes[data['name']]['type']
                if len(data['input']) == 0:
                    data['input'].append(self.nodes[data['name']]['input'][0])
            self.net.remove_node(id)
            self.net.add_node(id)
            for i in data['input']:
                self.net.add_edge(i, id)
            self.fc.removeNode(self.fc.nodes()[data['name']])
            data['ID'] = id
            reset_flag = True
        else:#新建层
            data['ID'] = self.global_id
            self.name_id[data['name']] = self.global_id
            self.id_name[self.global_id] = data['name']
            self.net.add_node(self.global_id)
            for i in data['input']:
                self.net.add_edge(i, self.global_id)
            self.global_id += 1
        self.nodes[data['name']] = data
        if data['type'] == 1:#输入层对应的流程图操作
            self.fc.addInput(data['name'])
            self.fc_inputs[data['name']] = data['para']['out_size']
            self.fc.setInput(**self.fc_inputs)
        elif data['type'] in [9, 10, 11]:#concat2D、concat1D和残差连接层的流程图操作
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
        else:#其他层的流程图操作
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
        if data['isoutput']:#添加流程图输出
            self.outputs.append(data['ID'])
        if reset_flag:#对替换的层恢复后向的连接
            for everynode in self.nodes.values():
                if data['ID'] in everynode['input']:
                    out_terminal = node.outputs()['dataOut']
                    if everynode['type'] in [9, 10, 11]:
                        in_terminal = self.fc.nodes()[everynode['name']].inputs()[data['name']]
                    else:
                        in_terminal = self.fc.nodes()[everynode['name']].inputs()['dataIn']
                    self.fc.connectTerminals(in_terminal, out_terminal)
                    self.net.add_edge(data['ID'], everynode['ID'])

    def export_file(self):#导出pytorch脚本
        filename, _ = QFileDialog.getSaveFileName(self, '导出模型', 'C:\\', 'Python Files (*.py)')
        if filename is None or filename == "":
            return 0
        filedir, filename_text = os.path.split(filename)
        filename_text = filename_text.split(".")[0]
        if self.check() == 0:
            QMessageBox.warning(self, "错误", "出现size<=0或模型没有输出")
            return 0
        sort = list(nx.topological_sort(self.net))
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
            f.write(space*2+"super(Net, self).__init__()\n")#一下为__init__函数
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
                elif layer['type'] == 12:
                    f.write(space*2+"self.{} = nn.Identity()\n".format(name))
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
                            if k == 'stride' and v is not None:
                                f.write("," + k + "=" + str(v))
                    f.write(")\n")
                elif layer['type'] == 4:
                    f.write(space*2+"self."+layer['name']+" = nn.Linear(")
                    f.write(str(layer['para']['in_size'])+",")
                    f.write(str(layer['para']['out_features'])+",")
                    f.write("bias="+str(layer['para']['bias']))
                    f.write(")\n")
                elif layer['type'] == 7:
                    f.write(space * 2 + "self." + layer['name'] + " = nn.BatchNorm1d(")
                    f.write(str(layer['para']['in_size'])+",")
                    f.write("eps="+str(layer['para']['eps'])+",")
                    f.write("momentum=" + str(layer['para']['momentum']) + ",")
                    f.write("affine=" + str(layer['para']['affine']) + ",")
                    f.write("track_running_stats=" + str(layer['para']['track_running_stats']) + ")\n")
                elif layer['type'] == 8:
                    f.write(space * 2 + "self." + layer['name'] + " = nn.BatchNorm2d(")
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
            return_layers = list()
            for layer_id in sort:
                layer = self.nodes[self.id_name[layer_id]]
                if layer['type'] == 2 or layer['type'] == 4:
                    f.write(space*2+layer['name']+" = ")
                    if layer['type'] == 4:
                        input_name = self.id_name[layer['input'][0]]
                        inner_str = "self.{0}({1}.view({1}.size()[0], -1))".format(layer['name'], input_name)
                    else:
                        inner_str = "self."+ layer['name'] + "(" + self.id_name[layer['input'][0]] + ")"
                    if layer['para']['activate'] != "None":
                        if layer['para']['activate'] in ['tanh', 'sigmoid']:
                            tmp = "torch." + layer['para']['activate'] + "({})".format(inner_str)
                        else:
                            tmp = "F."+layer['para']['activate'] + "({})".format(inner_str)
                        inner_str = tmp
                    if layer['para']['dropout']:
                        tmp = "F.dropout({}, p=".format(inner_str)+str(layer['para']['dropout_radio'])+")"
                        inner_str = tmp
                    f.write(inner_str)
                    f.write("\n")
                elif layer['type'] in [3, 7, 8]:
                    f.write(space*2+layer['name']+" = self.{}({})\n".format(layer['name'],
                                                                            self.id_name[layer['input'][0]]))
                elif layer['type'] == 5:
                    f.write(space*2+layer['name']+" = F.softmax({}, dim=1)\n".format(self.id_name[layer['input'][0]]))
                elif layer['type'] == 6:
                    f.write(space*2+layer['name']+" = F.log_softmax({}, dim=1)\n".format(self.id_name[layer['input'][0]]))
                elif layer['type'] == 9:
                    f.write(space*2+layer['name']+ " = ")
                    for i in range(len(layer['input'])-1):
                        f.write(self.id_name[layer['input'][i]]+"+")
                    f.write(self.id_name[layer['input'][len(layer['input'])-1]]+"\n")
                elif layer['type'] == 10:
                    layers_to_cat = list()
                    for input_id in layer['input']:
                        input_name = self.id_name[input_id]
                        input_layer = self.nodes[input_name]
                        layers_to_cat.append(input_name)
                        pad_up, pad_down, pad_left, pad_right = 0, 0, 0, 0
                        if input_layer['para']['out_size'][1] != layer['para']['out_size'][1]:
                            rest = (layer['para']['out_size'][1] - input_layer['para']['out_size'][1])/2
                            if rest != int(rest):
                                pad_up, pad_down = int(rest), int(rest)+1
                            else:
                                pad_up, pad_down = int(rest), int(rest)
                        if input_layer['para']['out_size'][2] != layer['para']['out_size'][2]:
                            rest = (layer['para']['out_size'][2] - input_layer['para']['out_size'][2])/2
                            if rest != int(rest):
                                pad_left, pad_right = int(rest), int(rest)+1
                            else:
                                pad_left, pad_right = int(rest), int(rest)
                            pad = (pad_left, pad_right, pad_up, pad_down)
                        f.write(space*2+input_name+" = F.pad({}, ({}, {}, {}, {}))\n".format(input_name,\
                                                        pad_left, pad_right, pad_up, pad_down))
                    f.write(space*2+layer['name']+" = torch.cat([{}], 1)\n".format(",".join(layers_to_cat)))
                elif layer['type'] == 11:
                    layers_to_cat = list()
                    for input_id in layer['input']:
                        input_name = self.id_name[input_id]
                        layers_to_cat.append(input_name)
                    f.write(space * 2 + layer['name'] + " = torch.cat([{}], 1)\n".format(",".join(layers_to_cat)))
                elif layer['type'] == 12:
                    f.write(space*2+layer['name']+" = self.{}({})\n".format(layer['name'],
                                                                            self.id_name[layer['input'][0]]))
                if layer['isoutput']:
                    return_layers.append(layer['name'])
            if len(return_layers) > 1:
                f.write(space*2+"return {}\n".format(",".join(return_layers)))
            else:
                f.write(space*2+"return {}".format(return_layers[0]))

    def check(self):#基于DAG的校验
        if len(self.outputs) == 0:
            QMessageBox.warning(self, "错误", "模型没有输出")
            return 0
        for item in self.nodes.values():
            if type(item['para']['out_size']) is int:
                if item['para']['out_size'] <= 0:
                    QMessageBox.warning(self, "错误", "{}层输出尺寸为负数或0".format(item['name']))
                    return 0
            else:
                for size in item['para']['out_size']:
                    if size <= 0:
                        QMessageBox.warning(self, "错误", "{}层输出尺寸为负数或0".format(item['name']))
                        return 0

    def import_file(self):#导入json文件重建模型
        filename, _ = QFileDialog.getOpenFileName(self, '导入模型', 'C:\\', 'JSON Files (*.json)')
        if filename is None or filename == "":
            return 0
        d_json = json.load(open(filename, 'r'))
        self.id_name = dict()
        self.name_id = dict()
        self.nodes = dict()
        self.net = nx.DiGraph()
        self.fc.clear()
        self.fc_inputs = dict()
        self.global_id = 0
        self.outputs = list()
        self.detail.clear()
        self.detail.setColumnCount(2)
        self.detail.setHeaderLabels(["属性", "值"])
        self.root = QTreeWidgetItem(self.detail)
        self.root.setText(0, "所有属性")
        for data in d_json:
            self.id_name[data['ID']] = data['name']
            self.name_id[data['name']] = data['ID']
            self.nodes[data['name']] = data
            self.net.add_node(data['ID'])
            for i in data['input']:
                self.net.add_edge(i, data['ID'])
            if data['type'] == 1:
                if not data['name'] in self.fc.inputs().keys():
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
                    if not data['name'] in self.fc.outputs().keys():
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
                    if not data['name'] in self.fc.outputs().keys():
                        self.fc.addOutput(data['name'])
                    self.fc.connectTerminals(node['dataOut'], self.fc[data['name']])
            if data['isoutput']:
                self.outputs.append(data['ID'])


class AddLayerWindow(QtWidgets.QDialog, Ui_AddLayerWindow):#层操作界面对应的类
    datasignal = pyqtSignal(dict)#定义信号，类型为python字典

    def __init__(self):
        super(AddLayerWindow, self).__init__()
        self.setupUi(self)
        self.setFixedSize(433, 374)

    def fill_content(self):#按层的种类动态填充参数面板
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
            self.stride_1.setText("1")
            self.stride_2.setText("1")
            label_padding = QLabel("padding:")
            self.padding_1 = QLineEdit()
            self.padding_2 = QLineEdit()
            self.padding_1.setValidator(pValidator)
            self.padding_2.setValidator(pValidator)
            self.padding_1.setText("0")
            self.padding_2.setText("0")
            self.dilation = QCheckBox("dilation:")
            self.dilation_1 = QLineEdit()
            self.dilation_2 = QLineEdit()
            self.dilation_1.setValidator(pValidator)
            self.dilation_2.setValidator(pValidator)
            self.dilation_1.setText("1")
            self.dilation_2.setText("1")
            self.bias = QCheckBox("bias")
            label_paddingmode = QLabel("padding mode:")
            self.paddingmode = QComboBox()
            self.paddingmode.addItem("zeros")
            label_activate = QLabel("激活函数：")
            self.activate = QComboBox()
            self.activate.addItem("None")
            self.activate.addItem("relu")
            self.activate.addItem("leaky_relu")
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
            self.padding_1.setText("0")
            self.padding_2.setText("0")
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
            self.activate.addItem("leaky_relu")
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

    def gen_layer(self):#“添加”按钮对应的槽函数，收集界面参数并发送信号
        send_data = True
        data = dict()#一个层所有信息都在data中
        if self.layername.text() == "":
            QMessageBox.warning(self, "警告", "不合法输入：未指定层的名字")
            send_data = False
        else:
            data['name'] = self.layername.text()#层名
        if self.layertype.currentIndex() == 0:
            QMessageBox.warning(self, "警告", "不合法输入：未选择层的类型")
            send_data = False
        else:
            data['type'] = self.layertype.currentIndex()#层的种类
        if self.layerinput.text() == "" and self.layertype.currentIndex() not in [1, 12]:
            QMessageBox.warning(self, "警告", "不合法输入：未指定层的输入")
            send_data = False
        elif self.layertype.currentIndex() not in [9, 10, 11, 12] \
                and len(self.layerinput.text().split(";")) > 1:
            QMessageBox.warning(self, "警告", "不合法输入：输入多于一个")
            send_data = False
        else:
            data['input'] = self.layerinput.text()#层的输入（内容为名字）
        data['isoutput'] = self.layeroutput.isChecked()
        data['para'] = dict()#层的参数
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
        return 0



if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    myshow = ModelWindow()
    myshow.show()
    sys.exit(app.exec_())
