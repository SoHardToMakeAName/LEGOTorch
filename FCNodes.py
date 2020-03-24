from pyqtgraph.flowchart import Flowchart, Node
import pyqtgraph.flowchart.library as fclib
from pyqtgraph.flowchart.library.common import CtrlNode
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import numpy as np


class CovNode(Node):
    nodeName = 'Cov2d'

    def __init__(self, name):
        self.view = None
        self.para = None
        self.thisname = name
        terminals = {'dataIn': dict(io='in'), 'dataOut': dict(io='out')}
        Node.__init__(self, name, terminals=terminals)

    def setView(self, view):
        self.view = view

    def setPara(self, para):
        self.para = para

    def process(self, dataIn):
        c_in = dataIn[0]
        h_in = dataIn[1]
        w_in = dataIn[2]
        kernel_h, kernel_w = self.para['kernel']
        padding_h, padding_w = self.para['padding']
        if self.para['dilation'] is not None:
            dilation_h, dilation_w = self.para['dilation']
        else:
            dilation_h, dilation_w = 1, 1
        stride_h, stride_w = self.para['stride']
        h_out = (h_in + 2 * padding_h - dilation_h * (kernel_h - 1) - 1) // stride_h + 1
        w_out = (h_in + 2 * padding_w - dilation_w * (kernel_w - 1) - 1) // stride_w + 1
        c_out = self.para['outchannels']
        self.para['in_size'] = (c_in, h_in, w_in)
        self.para['out_size'] = (c_out, h_out, w_out)
        output = np.array(self.para['out_size'])
        self.child = QTreeWidgetItem()
        self.child.setText(0, self.thisname)
        self.view.addChild(self.child)
        for k, v in self.para.items():
            attr = QTreeWidgetItem()
            attr.setText(0, k)
            attr.setText(1, str(v))
            self.child.addChild(attr)
        return {'dataOut': output}


class PoolNode(Node):
    nodeName = 'Pool2d'

    def __init__(self, name):
        self.view = None
        self.para = None
        self.thisname = name
        terminals = {'dataIn': dict(io='in'), 'dataOut': dict(io='out')}
        Node.__init__(self, name, terminals=terminals)

    def setView(self, view):
        self.view = view

    def setPara(self, para):
        self.para = para

    def process(self, dataIn):
        c_in = dataIn[0]
        h_in = dataIn[1]
        w_in = dataIn[2]
        kernel_h, kernel_w = self.para['kernel']
        padding_h, padding_w = self.para['padding']
        if self.para['dilation'] is not None:
            dilation_h, dilation_w = self.para['dilation']
        else:
            dilation_h, dilation_w = 1, 1
        stride_h, stride_w = self.para['stride']
        h_out = (h_in + 2 * padding_h - dilation_h * (kernel_h - 1) - 1) // stride_h + 1
        w_out = (h_in + 2 * padding_w - dilation_w * (kernel_w - 1) - 1) // stride_w + 1
        c_out = self.para['outchannels']
        self.para['in_size'] = (c_in, h_in, w_in)
        self.para['out_size'] = (c_out, h_out, w_out)
        output = np.array(self.para['out_size'])
        self.child = QTreeWidgetItem()
        self.child.setText(0, self.thisname)
        self.view.addChild(self.child)
        for k, v in self.para.items():
            attr = QTreeWidgetItem()
            attr.setText(0, k)
            attr.setText(1, str(v))
            self.child.addChild(attr)
        return {'dataOut': output}


class LinearNode(Node):
    nodeName = 'Linear'

    def __init__(self, name):
        self.view = None
        self.para = None
        self.thisname = name
        terminals = {'dataIn': dict(io='in'), 'dataOut': dict(io='out')}
        Node.__init__(self, name, terminals=terminals)

    def setView(self, view):
        self.view = view

    def setPara(self, para):
        self.para = para

    def process(self, dataIn):
        size_in = 1
        for i in range(dataIn.shape[0]):
            size_in = size_in * dataIn[i]
        size_out = self.para['out_features']
        self.para['in_size'] = size_in
        self.para['out_size'] = size_out
        output = np.array(size_out)
        self.child = QTreeWidgetItem()
        self.child.setText(0, self.thisname)
        self.view.addChild(self.child)
        for k, v in self.para.items():
            attr = QTreeWidgetItem()
            attr.setText(0, k)
            attr.setText(1, str(v))
            self.child.addChild(attr)
        return {'dataOut': output}


class ConcatNode(Node):
    nodeName = 'Concat2d'

    def __init__(self, name):
        self.view = None
        self.para = None
        self.thisname = name
        terminals = {'dataOut': dict(io='out')}
        Node.__init__(self, name, terminals=terminals, allowAddInput=True)

    def setView(self, view):
        self.view = view

    def setPara(self, para):
        self.para = para

    def process(self, **kargs):
        c, max_h, max_w = 0, 0, 0
        for k, v in kargs.items():
            c += v[0]
            if max_h < v[1]:
                max_h = v[1]
            if max_w < v[2]:
                max_w = v[2]
        self.para['out_size'] = (c, max_h, max_w)
        output = np.array(self.para['out_size'])
        self.child = QTreeWidgetItem()
        self.child.setText(0, self.thisname)
        self.view.addChild(self.child)
        for k, v in self.para.items():
            attr = QTreeWidgetItem()
            attr.setText(0, k)
            attr.setText(1, str(v))
            self.child.addChild(attr)
        return {'dataOut': output}


class Concat1dNode(Node):
    nodeName = 'Concat1d'

    def __init__(self, name):
        self.view = None
        self.para = None
        self.thisname = name
        terminals = {'dataOut': dict(io='out')}
        Node.__init__(self, name, terminals=terminals, allowAddInput=True)

    def setView(self, view):
        self.view = view

    def setPara(self, para):
        self.para = para

    def process(self, **kargs):
        size = 0
        for k, v in kargs.items():
            size += v[0]
        self.para['out_size'] = size
        output = np.array(size)
        self.child = QTreeWidgetItem()
        self.child.setText(0, self.thisname)
        self.view.addChild(self.child)
        for k, v in self.para.items():
            attr = QTreeWidgetItem()
            attr.setText(0, k)
            attr.setText(1, str(v))
            self.child.addChild(attr)
        return {'dataOut': output}


class SoftmaxNode(Node):
    nodeName = 'Softmax'

    def __init__(self, name):
        self.view = None
        self.para = None
        self.thisname = name
        terminals = {'dataIn': dict(io='in'), 'dataOut': dict(io='out')}
        Node.__init__(self, name, terminals=terminals)

    def setView(self, view):
        self.view = view

    def setPara(self, para):
        self.para = para

    def process(self, dataIn):
        size_in = dataIn[0]
        self.para['in_size'] = size_in
        self.para['out_size'] = size_in
        output = np.array(size_in)
        self.child = QTreeWidgetItem()
        self.child.setText(0, self.thisname)
        self.view.addChild(self.child)
        for k, v in self.para.items():
            attr = QTreeWidgetItem()
            attr.setText(0, k)
            attr.setText(1, str(v))
            self.child.addChild(attr)
        return {'dataOut': output}


class LogSoftmaxNode(Node):
    nodeName = 'LogSoftmax'

    def __init__(self, name):
        self.view = None
        self.para = None
        self.thisname = name
        terminals = {'dataIn': dict(io='in'), 'dataOut': dict(io='out')}
        Node.__init__(self, name, terminals=terminals)

    def setView(self, view):
        self.view = view

    def setPara(self, para):
        self.para = para

    def process(self, dataIn):
        size_in = dataIn[0]
        self.para['in_size'] = size_in
        self.para['out_size'] = size_in
        output = np.array(size_in)
        self.child = QTreeWidgetItem()
        self.child.setText(0, self.thisname)
        self.view.addChild(self.child)
        for k, v in self.para.items():
            attr = QTreeWidgetItem()
            attr.setText(0, k)
            attr.setText(1, str(v))
            self.child.addChild(attr)
        return {'dataOut': output}


class BachNorm1dNode(Node):
    nodeName = 'BachNorm1d'

    def __init__(self, name):
        self.view = None
        self.para = None
        self.thisname = name
        terminals = {'dataIn': dict(io='in'), 'dataOut': dict(io='out')}
        Node.__init__(self, name, terminals=terminals)

    def setView(self, view):
        self.view = view

    def setPara(self, para):
        self.para = para

    def process(self, dataIn):
        size_in = dataIn[0]
        self.para['in_size'] = size_in
        self.para['out_size'] = size_in
        output = np.array(size_in)
        self.child = QTreeWidgetItem()
        self.child.setText(0, self.thisname)
        self.view.addChild(self.child)
        for k, v in self.para.items():
            attr = QTreeWidgetItem()
            attr.setText(0, k)
            attr.setText(1, str(v))
            self.child.addChild(attr)
        return {'dataOut': output}


class BachNorm2dNode(Node):
    nodeName = 'BachNorm2d'

    def __init__(self, name):
        self.view = None
        self.para = None
        self.thisname = name
        terminals = {'dataIn': dict(io='in'), 'dataOut': dict(io='out')}
        Node.__init__(self, name, terminals=terminals)

    def setView(self, view):
        self.view = view

    def setPara(self, para):
        self.para = para

    def process(self, dataIn):
        size_in = dataIn[0]
        self.para['in_size'] = size_in
        self.para['out_size'] = size_in
        output = np.array(size_in)
        self.child = QTreeWidgetItem()
        self.child.setText(0, self.thisname)
        self.view.addChild(self.child)
        for k, v in self.para.items():
            attr = QTreeWidgetItem()
            attr.setText(0, k)
            attr.setText(1, str(v))
            self.child.addChild(attr)
        return {'dataOut': output}


class AddNode(Node):
    nodeName = 'Add'

    def __init__(self, name):
        self.view = None
        self.para = None
        self.thisname = name
        terminals = {'dataOut': dict(io='out')}
        Node.__init__(self, name, terminals=terminals, allowAddInput=True)

    def setView(self, view):
        self.view = view

    def setPara(self, para):
        self.para = para

    def process(self, **kargs):
        c, h, w = kargs.items()[0][1]
        self.para['out_size'] = (c, h, w)
        output = np.array(self.para['out_size'])
        self.child = QTreeWidgetItem()
        self.child.setText(0, self.thisname)
        self.view.addChild(self.child)
        for k, v in self.para.items():
            attr = QTreeWidgetItem()
            attr.setText(0, k)
            attr.setText(1, str(v))
            self.child.addChild(attr)
        return {'dataOut': output}