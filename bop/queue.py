# -*- coding: utf-8 -*-
'''
Created on 19/11/2012

@author: frieder.czeschla

These classes define the 'queue' module which draws and controls an individual stack/slot of submitted backup-jobs.
'''
from PyQt4 import QtGui, QtCore
import time



class BOp_Queue_UI(QtGui.QFrame):
    
    def __init__(self, parent):
        
        self.parent = parent
        
        super(BOp_Queue_UI, self).__init__(self.parent)
        
        self.initUI()
        
        
    def initUI(self):
        
        # bg
        self.bg_pm = QtGui.QPixmap("img/BOp_Queue_bg.png")
        self.setMinimumSize(self.bg_pm.width(), self.bg_pm.height())
        self.setMaximumSize(self.bg_pm.width(), self.bg_pm.height())
        # size
        # layout
        self.GL = QtGui.QGridLayout(self)
        self.GL.setMargin(2)
        self.GL.setSpacing(3)
        # slots
        self.slots = []
        for i in range(6):
            self.slots.append(BOp_Queue_Slot_CTR(self, i))
            self.GL.addWidget(self.slots[-1], 0, i, 1, 1)
            
#        self.slots[3].update()
#        self.slots[3].timer = QtCore.QTimer(self.slots[3])
#        self.slots[3].timer.singleShot(10, self.slots[3].update)
    
    
    def paintEvent(self, e):
        
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawPixmap(e.rect(), self.bg_pm)
        qp.end()



class BOp_Queue_CTR(BOp_Queue_UI):
    
    def __init__(self, parent):
        
        self.parent = parent
        
        super(BOp_Queue_CTR, self).__init__(self.parent)
        
        
        
class BOp_Queue_Slot_UI(QtGui.QFrame):
    
    def __init__(self, parent):
        
        self.parent = parent
        
        super(BOp_Queue_Slot_UI, self).__init__(self.parent)
        
        self.initUI()
        
        
    def initUI(self):
        
        self.setStyleSheet("background: orange")
        
        # layout
        self.setMaximumHeight(0)
        self.GL = QtGui.QGridLayout(self)
        self.GL.setMargin(0)
        self.GL.setSpacing(0)
        
        # TEST ##################################################
        self.BOp_Queue_Job = []
#        for i in range(20):
#            self.btns.append(QtGui.QPushButton(str(20-i)))
#            self.GL.addWidget(self.btns[-1], i, 0, 1, 1)
#        self.setMinimumHeight(self.GL.count()*40)
        # /TEST ##################################################
        
        
        
class BOp_Queue_Slot_CTR(BOp_Queue_Slot_UI):
    
    slotNo = -1
    
    def __init__(self, parent, slotNo):
        
        self.parent = parent
        self.slotNo = slotNo
        
        super(BOp_Queue_Slot_CTR, self).__init__(self.parent)
        
        # connect update signal from BOp_Jobs...
        self.parent.parent.parent.BOp_update.connect(self.addJob)
        
        # fill slot with existing jobs in BOp_Jobs_CTR
        for job in self.parent.parent.parent.getJobs():
            if job[1] == self.slotNo:
                self.addJob(job[0], job[1])
        
        
    def wheelEvent(self, e):
        '''
        Enable scroll in the slot widget
        '''
        # calc scroll distance, multiply if shift is pressed
        delta = e.delta()/8
        if QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier:
            delta *= 4
        # parent margin for offset
        parentMargin = self.parent.GL.margin()
        # buffer own geometry
        x = self.x()
        y = self.y()
        w = self.width()
        h = self.height()
        # set new scroll pos
        if self.y()+delta > 0: # if top is reached
            self.setGeometry(QtCore.QRect(x, 0+parentMargin, w, h))
        elif self.y()+delta < self.parent.height()-h: # if bottom is reached
            self.setGeometry(QtCore.QRect(x, self.parent.height()-h-parentMargin, w, h))
        else:
            self.setGeometry(QtCore.QRect(x, y+delta, w, h))


    def addJob(self, id, slotNo):
        
        # if it's me
        if (slotNo == self.slotNo):
            self.BOp_Queue_Job.append(BOp_Queue_Job_CTR())
            self.GL.addWidget(self.BOp_Queue_Job[-1], self.GL.count()+1, 0, 1, 1)
            
            self.updateQueue()
    
    
    def removeJob(self):
        
        pass
    
    
    def updateQueue(self):
        
        # update height of container (depending on # of items/backup job widgets in it
        # get job widget's height
        height = self.BOp_Queue_Job[0].height()
        self.setMinimumHeight(self.GL.count()*height)
        self.setMaximumHeight(self.GL.count()*height)
        # move into pos
        y = self.parent.height() - self.height() - self.parent.GL.margin()
        self.setGeometry(QtCore.QRect(self.x(), y, self.width(), self.height()))
        
        
        
class BOp_Queue_Job_UI(QtGui.QWidget):
    
    def __init__(self):
        
        super(BOp_Queue_Job_UI, self).__init__()
        
        self.bg_pm = QtGui.QPixmap("img/BOp_Queue_Job.png")
        
        self.setMinimumSize(self.bg_pm.width(), self.bg_pm.height())
        self.setMaximumSize(self.bg_pm.width(), self.bg_pm.height())
        
        self.initUI()
        
    
    def initUI(self):
        
        pass
                
    
    def paintEvent(self, e):
        
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawPixmap(e.rect(), self.bg_pm)
        qp.end()
        
        
        
class BOp_Queue_Job_CTR(BOp_Queue_Job_UI):
    
    def __init__(self):
        
        super(BOp_Queue_Job_CTR, self).__init__()


#class BOp_Queue_UI(QtGui.QFrame):
#    
#    def __init__(self, parent):
#        
#        super(BOp_Queue_UI, self).__init__()
#        
#        self.parent = parent
#        
#        self.initUI()
#        
#        
#    def initUI(self):
#        
##        self.setMinimumSize(512, 256)
#        
#        self.setStyleSheet("background: yellow")
#        self.GL = QtGui.QGridLayout(self)
#        self.GL.setContentsMargins(0, 0, 0, 0)
#        self.GL.W = QtGui.QWidget(self)
#        self.GL.W.setStyleSheet("background: blue")
#        self.GL.W.setMaximumWidth(72)
#        self.GL.setSpacing(0)
#        self.GL.addWidget(self.GL.W, 0, 0, 1, 1)
#        self.GL.W.GL = QtGui.QGridLayout(self.GL.W)
#        
#        self.btn1 = QtGui.QPushButton("re-paint 1!")
#        self.btn2 = QtGui.QPushButton("re-paint 2!")
#        self.btn2.clicked.connect(self.test)
#        
#        self.GL.W.GL.addWidget(self.btn1, 0, 0, 1, 1)
#        self.btn1.setHidden(True)
#        self.GL.W.GL.addWidget(self.btn2, 0, 0, 1, 1)
##        self.GL.addWidget(self.btn3, 0, 0, 1, 1)
##        self.btn1.setGeometry(QtCore.QRect(100,100,50,50))
#                                        
#        
#        self.pmBg = QtGui.QPixmap("img/BOp_queue_bg.png")
#        
##        self.anim = QtCore.QPropertyAnimation(self.btn1, "geometry")
##        self.anim.setDuration(500)
##        self.anim.setEasingCurve(QtCore.QEasingCurve.InOutCubic)
#
#    def test(self):
#        self.btn1.setHidden(False)
#        self.btn1.setGeometry(QtCore.QRect(10, 10, 50, 50))
##        self.GL.W.setGeometry(QtCore.QRect(-5, -10, 640, 240))
##    def uupdate(self):
##        self.update()
##        print self.btn1.x()
##        
##    def btnClick(self):
##        
##        # start re-draw
##        timer = QtCore.QTimer(self)
##        timer.timeout.connect(self.uupdate)
##        timer.start(1)
##        timer2 = QtCore.QTimer(self)
##        timer2.singleShot(600, timer.stop)
##        
##        self.anim.setKeyValueAt(0, QtCore.QRect(self.btn1.x(), self.btn1.y(),20,50))
###        self.anim.setKeyValueAt(0.1, QtCore.QRectF(150,80,20,50))
##        self.anim.setKeyValueAt(1, QtCore.QRect(self.btn1.x()+50,self.btn1.y(),20,50))
##        self.anim.start()
#        
#    def paintEvent(self, e):
#        
#        qp = QtGui.QPainter()
#        qp.begin(self)
#        
#        # draw UI
#        # bg
#        qp.drawPixmap(e.rect(), self.pmBg)
#        self.setMinimumSize(self.pmBg.size())
#        self.setMaximumSize(self.pmBg.size())
#        
#        qp.end()
#    
#    
#    
#class BOp_Queue_CTR(BOp_Queue_UI):
#    
#    whatKeysDown = -1
#    
#    def __init__(self, parent):
#        
#        self.parent = parent
#        
#        super(BOp_Queue_CTR, self).__init__(self.parent)
#        
##        timer = QtCore.QTimer(self)
##        timer.timeout.connect(self.printWhatKeysDown)
##        timer.start(100)
#        
#    def printWhatKeysDown(self):
#        
#        print self.whatKeysDown
#        
#    
#    def keyReleaseEvent(self, e):
#        
##        self.whatKeysDown = -1
#        pass
#    
#    def keyPressEvent(self, e):
#        
##        self.whatKeysDown = e.key()
#        pass
#    
#    def wheelEvent(self, e):
#        
#        QtCore.Qt.Key
#        
#        print e.delta()
#        x = self.GL.W.x()
#        y = self.GL.W.y()
#        w = self.GL.W.width()
#        h = self.GL.W.height()
#        speed = e.delta()/5
##        if self.whatKeysDown == 16777248:
#        modifiers = QtGui.QApplication.keyboardModifiers()
#        if modifiers == QtCore.Qt.ShiftModifier:
#            speed *= 3
#        # if shift key is pressed
#        
#        if y+speed >= 0:
#            self.GL.W.setGeometry(QtCore.QRect(x, y+speed, w, h))
#        else:
#            self.GL.W.setGeometry(QtCore.QRect(x, 0, w, h))
#        self.update()