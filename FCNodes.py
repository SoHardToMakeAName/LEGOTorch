from pyqtgraph.flowchart import Flowchart, Node
import pyqtgraph.flowchart.library as fclib
from pyqtgraph.flowchart.library.common import CtrlNode
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt


class CovNode(Node):
    nodeName = 'Cov2d'

    def __init__(self, name):
        self.view = None
        self.para = None
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
        h_out = (h_in + 2 * self.para['padding'][0] - self.para['dilation'][0] * (self.para['kernel'][0] - 1)\
                 - 1) // self.para['stride'][0] + 1
        w_out = (h_in + 2 * self.para['padding'][1] - self.para['dilation'][1] * (self.para['kernel'][1] - 1)\
                 - 1) // self.para['stride'][1] + 1
        c_out = self.para['outchannels']
        self.para['in_size'] = (c_in, h_in, w_in)
        self.para['out_size'] = (c_out, h_out, w_out)
        output = np.array(self.para['out_size'])
        for k, v in self.para.items():
            child = QTreeWidgetItem()
            child.setText(0, k)
            child.setText(1, str(v))
            self.view.addChild(child)
        return {'dataOut': output}
