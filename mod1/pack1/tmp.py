# -*- encoding: utf-8 -*-

#from PyQt4.QtGui import *
#from PyQt4.QtCore import *
# 
#import sys
# 
#class MyWidget(QWidget):
# 
#    def __init__(self, parent=None):
#        super(MyWidget, self).__init__(parent)
# 
#        # Enable mouse hover event tracking
#        self.setMouseTracking(True)
# 
#    def mouseMoveEvent(self, event):
#        # This is a QWidget provided event
#        # that fires for every mouse move event
#        # (In our case the move is also the hover)
#        print "Mouse Pointer is currently hovering at: ", event.pos()
# 
#if __name__=='__main__':
#    app = QApplication(sys.argv)
#    widget = MyWidget()
#    widget.show()
#    app.exec_()


#from PyQt4.QtGui import *
#from PyQt4.QtCore import *
#
#import sys
#
#class MyWidget(QWidget):
#    
#    simpleSig = pyqtSignal()
#    
#    def __init__(self):
#        
#        super(MyWidget, self).__init__()
#        
#        self.connect(self, SIGNAL("simpleSig"), self.broadcast)
#        
#        self.initUI()
#        
#    
#    def initUI(self):
#        
#        self.GL = QGridLayout(self)
#        self.GL.btn1 = QPushButton("Emit!")
#        self.GL.addWidget(self.GL.btn1, 0, 0, 1, 1)
##        self.GL.btn1.clicked.connect(self.emitSignal)
#        self.GL.btn1.clicked.connect(self.emitSignal)
#        
#    
#    def broadcast(self, n):
#        
#        print("I'm receiving an emitted signal!!!! Yabbadabbadooo "+str(n))
#        
#    def emitSignal(self):
#        
#        self.simpleSig.emit()
##        self.emit(SIGNAL("simpleSig"), 10)
#    
#    
#if __name__=='__main__':
#    app = QApplication(sys.argv)
#    widget = MyWidget()
#    widget.show()
#    app.exec_()


from PyQt4 import QtGui, QtCore
import sys



class MyWidget(QtGui.QWidget):
    
    def __init__(self):
        
        super(MyWidget, self).__init__()
        
        self.initUI()
        
        
    def initUI(self):
        
        # setting up window
        self.setMinimumSize(256, 256)
        self.setMaximumSize(256, 256)
        self.GL = QtGui.QGridLayout(self)
        self.GL.setMargin(0)
        
        self.GL.myWidget2 = QtGui.QFrame()
        self.GL.myWidget2.setMinimumSize(128, 128)
        self.GL.myWidget2.setMaximumSize(128, 128)
        self.GL.myWidget2.setStyleSheet("background: orange")
        
        self.GL.addWidget(self.GL.myWidget2)
        self.GL.myWidget2.show()
        self.GL.myWidget2.update()
        self.GL.update()
        self.update()
        
        
            timer = QtCore.QTimer()
            timer.singleShot(10, self.updatePosition)
            
        def updatePosition(self):
            
            self.GL.myWidget2.setGeometry(QtCore.QRect(0, 128, self.width(), self.height()))
        


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    app.exec_()