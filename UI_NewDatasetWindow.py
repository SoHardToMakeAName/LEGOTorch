# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI_NewDatasetWindow.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_NewDatasetWindow(object):
    def setupUi(self, NewDatasetWindow):
        NewDatasetWindow.setObjectName("NewDatasetWindow")
        NewDatasetWindow.resize(698, 524)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(NewDatasetWindow)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.codefield = QtWidgets.QTextEdit(NewDatasetWindow)
        self.codefield.setObjectName("codefield")
        self.verticalLayout.addWidget(self.codefield)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(NewDatasetWindow)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(NewDatasetWindow)
        self.buttonBox.accepted.connect(NewDatasetWindow.accept)
        self.buttonBox.rejected.connect(NewDatasetWindow.reject)
        QtCore.QMetaObject.connectSlotsByName(NewDatasetWindow)

    def retranslateUi(self, NewDatasetWindow):
        _translate = QtCore.QCoreApplication.translate
        NewDatasetWindow.setWindowTitle(_translate("NewDatasetWindow", "自定义数据集"))

