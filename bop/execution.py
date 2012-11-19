# -*- coding: utf-8 -*-
'''
Created on 19/11/2012

@author: frieder.czeschla

These classes define the 'execution' module which draws and controls an individual execution progress into the Activity Manager.
'''
from PyQt4 import QtGui

        
        
        
class BOp_Execution_UI(QtGui.QFrame):
    
    def __init__(self, parent):
        
        super(BOp_Execution_UI, self).__init__()
        
        self.parent = parent
        
        self.initUI()
        
        
    def initUI(self):
        
        self.setStyleSheet("background: #333")
        self.GL = QtGui.QGridLayout()
        # size
        self.setMinimumSize(320, 240)
    
    
    
class BOp_Execution_CTR(BOp_Execution_UI):
    
    def __init__(self, parent):
        
        self.parent = parent
        
        super(BOp_Execution_CTR, self).__init__(self.parent)