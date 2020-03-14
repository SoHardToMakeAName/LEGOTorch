# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI_AddLayerWindow.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator


class Ui_AddLayerWindow(object):
    def setupUi(self, AddLayerWindow):
        reg1 = QRegExp('^[a-z_]+[a-z0-9_]+$')
        pValidator1 = QRegExpValidator(self)
        pValidator1.setRegExp(reg1)
        reg2 = QRegExp('^[a-z_]+[a-z0-9_;]+$')
        pValidator2 = QRegExpValidator(self)
        pValidator2.setRegExp(reg2)
        AddLayerWindow.setObjectName("AddLayerWindow")
        AddLayerWindow.resize(433, 374)
        self.gridLayoutWidget = QtWidgets.QWidget(AddLayerWindow)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 0, 401, 117))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.profile = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.profile.setContentsMargins(0, 0, 0, 0)
        self.profile.setObjectName("profile")
        self.type = QtWidgets.QLabel(self.gridLayoutWidget)
        self.type.setObjectName("type")
        self.profile.addWidget(self.type, 0, 3, 1, 1)
        self.label = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label.setObjectName("label")
        self.profile.addWidget(self.label, 1, 1, 1, 1)
        self.layertype = QtWidgets.QComboBox(self.gridLayoutWidget)
        self.layertype.setObjectName("layertype")
        self.layertype.addItem("")
        self.layertype.addItem("")
        self.layertype.addItem("")
        self.layertype.addItem("")
        self.layertype.addItem("")
        self.layertype.addItem("")
        self.layertype.addItem("")
        self.layertype.addItem("")
        self.layertype.addItem("")
        self.profile.addWidget(self.layertype, 0, 4, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.profile.addWidget(self.label_2, 1, 3, 1, 1)
        self.layerinput = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.layerinput.setObjectName("layerinput")
        self.layerinput.setValidator(pValidator2)
        self.profile.addWidget(self.layerinput, 1, 2, 1, 1)
        self.layeroutput = QtWidgets.QCheckBox(self.gridLayoutWidget)
        self.layeroutput.setObjectName("layeroutput")
        self.layeroutput.setText("输出层")
        self.profile.addWidget(self.layeroutput, 1, 4, 1, 1)
        self.name = QtWidgets.QLabel(self.gridLayoutWidget)
        self.name.setObjectName("name")
        self.profile.addWidget(self.name, 0, 1, 1, 1)
        self.layername = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.layername.setObjectName("layername")
        self.layername.setValidator(pValidator1)
        self.profile.addWidget(self.layername, 0, 2, 1, 1)
        self.gridLayoutWidget_2 = QtWidgets.QWidget(AddLayerWindow)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(10, 120, 401, 211))
        self.gridLayoutWidget_2.setObjectName("gridLayoutWidget_2")
        self.content = QtWidgets.QGridLayout(self.gridLayoutWidget_2)
        self.content.setContentsMargins(0, 0, 0, 0)
        self.content.setObjectName("content")
        self.asurebtn = QtWidgets.QPushButton(AddLayerWindow)
        self.asurebtn.setGeometry(QtCore.QRect(320, 340, 93, 28))
        self.asurebtn.setObjectName("asurebtn")

        self.retranslateUi(AddLayerWindow)
        self.layertype.activated['QString'].connect(AddLayerWindow.fill_content)
        self.asurebtn.clicked.connect(AddLayerWindow.gen_layer)
        QtCore.QMetaObject.connectSlotsByName(AddLayerWindow)

    def retranslateUi(self, AddLayerWindow):
        _translate = QtCore.QCoreApplication.translate
        AddLayerWindow.setWindowTitle(_translate("AddLayerWindow", "新建一个层"))
        self.type.setText(_translate("AddLayerWindow", "类型："))
        self.label.setText(_translate("AddLayerWindow", "输入："))
        self.layertype.setItemText(0, _translate("AddLayerWindow", "<选择一种层>"))
        self.layertype.setItemText(1, _translate("AddLayerWindow", "输入层(Input)"))
        self.layertype.setItemText(2, _translate("AddLayerWindow", "卷积层(Conv2d)"))
        self.layertype.setItemText(3, _translate("AddLayerWindow", "池化层(Pooling)"))
        self.layertype.setItemText(4, _translate("AddLayerWindow", "线性层(Linear)"))
        self.layertype.setItemText(5, _translate("AddLayerWindow", "Softmax层"))
        self.layertype.setItemText(6, _translate("AddLayerWindow", "Logsoftmax层"))
        self.layertype.setItemText(7, _translate("AddLayerWindow", "Batch Norm(1d)层"))
        self.layertype.setItemText(8, _translate("AddLayerWindow", "Batch Norm(2d)层"))
        self.layertype.setItemText(9, _translate("AddLayerWindow", "加和层(Add)"))
        self.layertype.setItemText(10, _translate("AddLayerWindow", "集总层(Concat)"))
        self.label_2.setText(_translate("AddLayerWindow", "输出："))
        self.name.setText(_translate("AddLayerWindow", "层名："))
        self.asurebtn.setText(_translate("AddLayerWindow", "添加"))
