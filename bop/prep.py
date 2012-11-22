# -*- coding: utf-8 -*-

##################################################################################################
##    prep                                                                                      ##
##################################################################################################
##################################################################################################
##    Author:         Frieder Czeschla                                                          ##
##                    © 2012 All rights reserved                                                ##
##                    www.isotoxin.de                                                           ##
##                    frieder.czeschla@isotoxin.de                                              ##
##    Creation Date:  Nov 22, 2012                                                              ##
##    Version:        0.0.000000                                                                ##
##                                                                                              ##
##    Usage:          These classes create the pre-backup prep check window and control with    ##
##                    all its widgets.                                                          ##
##                                                                                              ##
##################################################################################################


from PyQt4 import QtCore, QtGui

class BOp_Prep_UI(QtGui.QDialog):
    
    def __init__(self):
        
        super(BOp_Prep_UI, self).__init__()
        
        self.initUI()
        
        
    def initUI(self):
        
        # layout
        self.GL = QtGui.QGridLayout(self)
        self.setStyleSheet("background: orange")
        
        # nest widgets: sources, targets, tree
        self.GL.BOp_Prep_Sources = BOp_Prep_Sources_CTR()
        self.GL.addWidget(self.GL.BOp_Prep_Sources, 0, 0, 1, 1)
        
        self.GL.BOp_Prep_Targets = BOp_Prep_Targets_CTR()
        self.GL.addWidget(self.GL.BOp_Prep_Targets, 1, 0, 1, 1)
        
        self.GL.BOp_Prep_Tree = BOp_Prep_Tree_CTR()
        self.GL.addWidget(self.GL.BOp_Prep_Tree, 0, 1, 2, 1)
        
        self.exec_()



class BOp_Prep_CTR(BOp_Prep_UI):
    
    def __init__(self, parent, setId):
        
        self.parent = parent
        self._setId = setId
        
        super(BOp_Prep_CTR, self).__init__()
        
        

class BOp_Prep_Sources_UI(QtGui.QFrame):
    
    def __init__(self):
        
        super(BOp_Prep_Sources_UI, self).__init__()
        
        self.initUI()
        
        
    def initUI(self):
        
        # layout
        self.GL = QtGui.QGridLayout(self)
        self.setStyleSheet("background: blue")
        
        # contents
        self.GL.label = QtGui.QLabel("Sources")
        self.GL.addWidget(self.GL.label, 0, 0, 1, 2)
        
        # contents: list sources
        



class BOp_Prep_Sources_CTR(BOp_Prep_Sources_UI):
    
    def __init__(self):
        
        super(BOp_Prep_Sources_CTR, self).__init__()
        
        

class BOp_Prep_Targets_UI(QtGui.QFrame):
    
    def __init__(self):
        
        super(BOp_Prep_Targets_UI, self).__init__()
        
        self.initUI()
        
        
    def initUI(self):
        
        # layout
        self.GL = QtGui.QGridLayout(self)
        self.setStyleSheet("background: yellow")
        
        # contents
        self.GL.label = QtGui.QLabel("Targets")
        self.GL.addWidget(self.GL.label)



class BOp_Prep_Targets_CTR(BOp_Prep_Targets_UI):
    
    def __init__(self):
        
        super(BOp_Prep_Targets_CTR, self).__init__()
        
        

class BOp_Prep_Tree_UI(QtGui.QFrame):
    
    def __init__(self):
        
        super(BOp_Prep_Tree_UI, self).__init__()
        
        self.initUI()
        
        
    def initUI(self):
        
        # layout
        self.GL = QtGui.QGridLayout(self)
        self.setStyleSheet("background: green")
        
        # contents
        self.GL.label = QtGui.QLabel("Tree")
        self.GL.addWidget(self.GL.label)



class BOp_Prep_Tree_CTR(BOp_Prep_Tree_UI):
    
    def __init__(self):
        
        super(BOp_Prep_Tree_CTR, self).__init__()