
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal
from UI_ModelWindow import Ui_ModelWindow
from UI_AddLayerWindow import Ui_AddLayerWindow
import os
import json

class ModelWindow(QtWidgets.QMainWindow, Ui_ModelWindow):
    def __init__(self):
        super(ModelWindow, self).__init__()
        self.setupUi(self)
        self.global_id = 0
    def add_layer(self):
        self.addlayer_window = AddLayerWindow(self.global_id)
        self.global_id += 1
        self.addlayer_window.show()

class AddLayerWindow(QtWidgets.QDialog, Ui_AddLayerWindow):
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
        if self.layertype.currentIndex() == 2:
            label_inchannels = QLabel("输入宽度:")
            label_outchannels = QLabel("输出宽度:")
            self.inchannels = QLineEdit()
            self.outchannels = QLineEdit()
            label_kernelsize = QLabel("卷积核大小:")
            label_X = QLabel("X")
            self.kernelheight = QLineEdit()
            self.kernelwidth = QLineEdit()
            label_stride = QLabel("stride:")
            self.stride_1 = QLineEdit()
            self.stride_2 = QLineEdit()
            label_padding = QLabel("padding:")
            self.padding_1 = QLineEdit()
            self.padding_2 = QLineEdit()
            self.bias = QCheckBox("bias")
            label_paddingmode = QLabel("padding mode:")
            self.paddingmode = QComboBox()
            self.paddingmode.addItem("zeros")
            self.content.addWidget(label_inchannels, 0, 0)
            self.content.addWidget(self.inchannels, 0, 1, 1, 3)
            self.content.addWidget(label_outchannels, 1, 0)
            self.content.addWidget(self.outchannels, 1, 1, 1, 3)
            self.content.addWidget(label_kernelsize, 2, 0)
            self.content.addWidget(self.kernelheight, 2, 1)
            self.content.addWidget(QLabel("X"), 2, 2)
            self.content.addWidget(self.kernelwidth, 2, 3)
            self.content.addWidget(label_stride, 3, 0)
            self.content.addWidget(self.stride_1, 3, 1)
            self.content.addWidget(QLabel("X"), 3, 2)
            self.content.addWidget(self.stride_2, 3, 3)
            self.content.addWidget(label_padding, 4, 0)
            self.content.addWidget(self.padding_1, 4, 1)
            self.content.addWidget(QLabel("X"), 4, 2)
            self.content.addWidget(self.padding_2, 4, 3)
            self.content.addWidget(label_paddingmode, 5, 0)
            self.content.addWidget(self.paddingmode, 5, 1)
            self.content.addWidget(self.bias, 5, 3)
    def gen_layer(self):
        data = dict()
        datasignal = pyqtSignal(dict)
        data['ID'] = self.id
        if self.layername.text() == "":
            QMessageBox.warning(self, "警告", "不合法输入：未指定层的名字")
        else:
            data['name'] = self.layername.text()
        if self.layertype.currentIndex() == 0:
            QMessageBox.warning(self, "警告", "不合法输入：未选择层的类型")
        else:
            data['type'] = self.layertype.currentIndex()
        if self.layerinput.text() == "":
            QMessageBox.warning(self, "警告", "不合法输入：未指定层的输入")
        else:
            data['input'] = self.layerinput.text()
        if self.layeroutput.text() == "":
            QMessageBox.warning(self, "警告", "不合法输入：未指定层的输出")
        else:
            data['output'] = self.layeroutput.text()
        if self.layertype.currentIndex() == 2:
            data['para'] = dict()
            try:
                data['para']['inchannels'] = int(self.inchannels.text())
            except:
                QMessageBox.warning(self, "警告", "不合法输入：输入宽度应为正整数")
            try:
                data['para']['outchannels'] = int(self.outchannels.text())
            except:
                QMessageBox.warning(self, "警告", "不合法输入：输出宽度应为正整数")
            try:
                data['para']['kernel'] = (int(self.kernelheight.text()), int(self.kernelwidth.text()))
            except:
                QMessageBox.warning(self, "警告", "不合法输入：卷积核大小均应为正整数")
            try:
                data['para']['stride'] = (int(self.stride_1.text()), int(self.stride_2.text()))
            except:
                QMessageBox.warning(self, "警告", "不合法输入：stride参数均应为正整数")
            try:
                data['para']['kernel'] = (int(self.padding_1.text()), int(self.padding_2.text()))
            except:
                QMessageBox.warning(self, "警告", "不合法输入：padding参数均应为正整数")
            data['para']['bias'] = self.bias.isChecked()
            data['para']['paddingmode'] = self.paddingmode.currentText()



if __name__=="__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    myshow = ModelWindow()
    myshow.show()
    sys.exit(app.exec_())