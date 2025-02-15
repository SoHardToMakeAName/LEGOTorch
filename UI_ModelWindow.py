# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI_ModelWindow.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ModelWindow(object):
    def setupUi(self, ModelWindow):
        ModelWindow.setObjectName("ModelWindow")
        ModelWindow.resize(640, 480)
        self.centralwidget = QtWidgets.QWidget(ModelWindow)
        self.centralwidget.setObjectName("centralwidget")
        ModelWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(ModelWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 640, 26))
        self.menubar.setObjectName("menubar")
        self.Function = QtWidgets.QMenu(self.menubar)
        self.Function.setObjectName("Function")
        self.FileSet = QtWidgets.QMenu(self.menubar)
        self.FileSet.setObjectName("FileSet")
        self.Add = QtWidgets.QMenu(self.menubar)
        self.Add.setObjectName("Add")
        ModelWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(ModelWindow)
        self.statusbar.setObjectName("statusbar")
        ModelWindow.setStatusBar(self.statusbar)
        self.ToTest = QtWidgets.QAction(ModelWindow)
        self.ToTest.setObjectName("ToTest")
        self.ToTrain = QtWidgets.QAction(ModelWindow)
        self.ToTrain.setObjectName("ToTrain")
        self.InportFile = QtWidgets.QAction(ModelWindow)
        self.InportFile.setObjectName("InportFile")
        self.ExportFile = QtWidgets.QAction(ModelWindow)
        self.ExportFile.setObjectName("ExportFile")
        self.AddLayer = QtWidgets.QAction(ModelWindow)
        self.AddLayer.setObjectName("AddLayer")
        self.AddModel = QtWidgets.QAction(ModelWindow)
        self.AddModel.setObjectName("AddModel")
        self.action = QtWidgets.QAction(ModelWindow)
        self.action.setObjectName("action")
        self.ExportWithoutCheck = QtWidgets.QAction(ModelWindow)
        self.ExportWithoutCheck.setObjectName("ExportWithoutCheck")
        self.DeleteLayer = QtWidgets.QAction(ModelWindow)
        self.DeleteLayer.setObjectName("DeleteLayer")
        self.Clear = QtWidgets.QAction(ModelWindow)
        self.Clear.setObjectName("Clear")
        self.Function.addAction(self.ToTest)
        self.Function.addAction(self.ToTrain)
        self.FileSet.addAction(self.InportFile)
        self.FileSet.addAction(self.ExportFile)
        self.Add.addAction(self.AddLayer)
        self.Add.addAction(self.AddModel)
        self.Add.addAction(self.Clear)
        self.menubar.addAction(self.Function.menuAction())
        self.menubar.addAction(self.FileSet.menuAction())
        self.menubar.addAction(self.Add.menuAction())

        self.retranslateUi(ModelWindow)
        self.AddLayer.triggered.connect(ModelWindow.add_layer)
        self.ExportFile.triggered.connect(ModelWindow.export_file)
        self.InportFile.triggered.connect(ModelWindow.import_file)
        self.ToTrain.triggered.connect(ModelWindow.to_train)
        self.AddModel.triggered.connect(ModelWindow.modifiey_layer)
        self.ToTest.triggered.connect(ModelWindow.to_test)
        self.Clear.triggered.connect(ModelWindow.clear)
        QtCore.QMetaObject.connectSlotsByName(ModelWindow)

    def retranslateUi(self, ModelWindow):
        _translate = QtCore.QCoreApplication.translate
        ModelWindow.setWindowTitle(_translate("ModelWindow", "模型"))
        self.Function.setTitle(_translate("ModelWindow", "功能"))
        self.FileSet.setTitle(_translate("ModelWindow", "脚本"))
        self.Add.setTitle(_translate("ModelWindow", "层"))
        self.ToTest.setText(_translate("ModelWindow", "测试"))
        self.ToTrain.setText(_translate("ModelWindow", "训练"))
        self.InportFile.setText(_translate("ModelWindow", "导入"))
        self.ExportFile.setText(_translate("ModelWindow", "导出"))
        self.AddLayer.setText(_translate("ModelWindow", "新建"))
        self.AddModel.setText(_translate("ModelWindow", "更改"))
        self.action.setText(_translate("ModelWindow", "删除"))
        self.ExportWithoutCheck.setText(_translate("ModelWindow", "导出但不检查"))
        self.DeleteLayer.setText(_translate("ModelWindow", "删除"))
        self.Clear.setText(_translate("ModelWindow", "清空"))

