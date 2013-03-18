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
import config
import json
import os
import sqlite3
import thread

class BOp_Prep_UI(QtGui.QDialog):
    
    def __init__(self):
        
        super(BOp_Prep_UI, self).__init__()
        
        self.initUI()
        
        
    def initUI(self):
        
        # layout
        self.GL = QtGui.QGridLayout(self)
        self.setStyleSheet("background: orange")
        
        # nest widgets: sources, targets, tree
        self.GL.BOp_Prep_Sources = BOp_Prep_Sources_CTR(self._setId)
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
        
        self.GL.sourceWidgets = []
        
        # contents: list sources
        self.updateSources()
        



class BOp_Prep_Sources_CTR(BOp_Prep_Sources_UI):
    
    def __init__(self, setId):
        
        self._setId = setId
        
        super(BOp_Prep_Sources_CTR, self).__init__()
        
        
    def updateSources(self):
        
        global config
        
        # get sources, filters, targets data
        conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
        cursor = sqlite3.Cursor(conn)
        resSets = cursor.execute("SELECT `sources`, `filters`, `targets` FROM `sets` WHERE `setId` = ? AND `userId` = ?", (self._setId, config.USERID)).fetchone()
        resSources = cursor.execute("SELECT * FROM `sources` WHERE `userId` = ?", (config.USERID,)).fetchall()
        sources = json.loads(resSets[0])
        filters = json.loads(resSets[1])
        targets = json.loads(resSets[2])
        
        # get FS data
        
        # clear existing source-list-widgets
        for i in range(self.GL.count()-1):
            self.GL.sourceWidgets[i-1] = None
        # (re-)draw sources from db
        i = 0
        for source in sources:
            sourceURL = ''
            # get corresponding path/name for id
            for setDataset in resSources:
                if (setDataset[0] == source):
                    sourceURL = setDataset[2]
            sourceWidget = QtGui.QLabel(sourceURL+" ("+str(thread.start_new_thread(self.getDirSize, (sourceURL,)))+")")
            self.GL.sourceWidgets.append(sourceWidget)
            self.GL.addWidget(self.GL.sourceWidgets[-1], i+1, 0, 1, 1)
            
#            signal = QtCore.pyqtSignal()
#            signal.triggered.connect(lambda: self.loadDirSize(sourceWidget.text))
            i += 1
        cursor.close()
        conn.close()
        
        
    def loadDirSize(self, target):
        pass
        
    
    
    def getDirSize(self, start_path = u'.'):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(start_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
            
        return self.formatDirSize(total_size)
        
    
    def formatDirSize(self, size):
        
        # format byte-size
        units = ["Byte", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"]
        i = len(units)-1
        for unit in units:
            threshold = pow(1024, i)
            if size > threshold:
                size = str(round(int(size)/float(threshold), 2)) + " " + units[i]
                break
            i -= 1
        
        

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