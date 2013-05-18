# -*- coding: utf-8 -*-
'''
Created on 19/11/2012

@author: frieder.czeschla

These classes define the Activity Manager's View and Control and host the modules 'execution', 'queue', 'report'
'''
from PyQt4 import QtGui
from bop.execution import BOp_Execution_CTR
from bop.queue import BOp_Queue_CTR
from bop.report import BOp_Report_CTR




class BOp_Activity_UI(QtGui.QWidget):
    
    def __init__(self, session_gui):
        
        self.parent = session_gui
        
        super(BOp_Activity_UI, self).__init__()
        
        self.initUI()
    
    
    def initUI(self):
        
        self.setWindowTitle("Backup Activity - BackupShizzle")
        self.setWindowIcon(QtGui.QIcon(QtGui.QPixmap("img/favicon.png")))
        
        
        self.GL = QtGui.QGridLayout(self)
        self.GL.setSpacing(0)
        self.GL.setMargin(0)
        # add Queue
        self.GL.addWidget(BOp_Queue_CTR(self), 0, 0, 1, 2)
        # add Exec
        self.GL.addWidget(BOp_Execution_CTR(self), 1, 0, 1, 1)
        # add Report
        self.GL.addWidget(BOp_Report_CTR(self), 1, 1, 1, 1)
        
        
        
class BOp_Activity_CTR(BOp_Activity_UI):
    
    def __init__(self, session_gui):
        
        self.parent = session_gui
        
        super(BOp_Activity_CTR, self).__init__(self.parent)
        
        self.show()