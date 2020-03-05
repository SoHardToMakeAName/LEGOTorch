
from PyQt5 import QtWidgets
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

class ModelWindow(QtWidgets.QMainWindow, Ui_ModelWindow):
    def __init__(self):
        super(ModelWindow, self).__init__()
        self.setupUi(self)
        self.global_id = 0
        self.nodes = list()
        self.id_name = dict()
        self.name_id = dict()
        self.net = nx.Graph()
    def add_layer(self):
        self.addlayer_window = AddLayerWindow(self.global_id)
        self.global_id += 1
        self.addlayer_window.datasignal.connect(self.accept_layer)
        self.addlayer_window.show()
    def accept_layer(self, data):
        if not data['type'] == 1:
            inputs = data['input'].split(";")
            data['input'] = list()
            for i in range(len(inputs)):
                try:
                    layer = self.name_id[inputs[i]]
                    data['input'].append(layer)
                except:
                    QMessageBox.warning(self, "错误", "输入来自未生成的层：{}".format(inputs[i]))
        self.id_name[data['ID']] = data['name']
        self.name_id[data['name']] = data['ID']
        self.nodes.append(data)

        

class AddLayerWindow(QtWidgets.QDialog, Ui_AddLayerWindow):
    datasignal = pyqtSignal(dict)
    def __init__(self, global_id):
        super(AddLayerWindow, self).__init__()
        self.setupUi(self)
        self.id = global_id
        self.setWindowTitle("ID:{}".format(str(self.id)))
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
            self.activate.addItem("log_sigmoid")
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
            self.power.setValidator(pValidator)
            self.content.addWidget(label_power, 4, 0)
            self.content.addWidget(self.power, 4, 1)


    def gen_layer(self):
        send_data = True
        data = dict()
        data['ID'] = self.id
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
        else:
            data['input'] = self.layerinput.text()
        if self.layeroutput.text() == "":
            QMessageBox.warning(self, "警告", "不合法输入：未指定层的输出")
            send_data = False
        else:
            data['output'] = self.layeroutput.text()
        if self.layertype.currentIndex() == 1:
            try:
                data['para'] = dict()
                data['para']['size'] = (int(self.sizec.text()), int(self.sizeh.text()), int(self.sizew.text()))
            except:
                QMessageBox.warning(self, "警告", "不合法输入：输入维度均应为正整数")
                send_data = False
        elif self.layertype.currentIndex() == 2:
            data['para'] = dict()
            # try:
            #     data['para']['inchannels'] = int(self.inchannels.text())
            # except:
            #     QMessageBox.warning(self, "警告", "不合法输入：输入宽度应为正整数")
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
                data['para']['kernel'] = (int(self.padding_1.text()), int(self.padding_2.text()))
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
        elif self.layertype.currentIndex() == 3:
            data['para'] = dict()
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
                data['para']['kernel'] = (int(self.padding_1.text()), int(self.padding_2.text()))
            except:
                QMessageBox.warning(self, "警告", "不合法输入：padding参数均应为正整数")
                send_data = False
            else:
                data['para']['dilation'] = None
        if send_data:
            self.datasignal.emit(data)
            self.destroy()


if __name__=="__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    myshow = ModelWindow()
    myshow.show()
    sys.exit(app.exec_())