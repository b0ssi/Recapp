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
#        self.simpleSig.connect(self.broadcast)
#        
#        self.initUI()
#        
#    
#    def initUI(self):
#        
#        self.GL = QGridLayout(self)
#        self.GL.btn1 = QPushButton("Emit!")
#        self.GL.addWidget(self.GL.btn1, 0, 0, 1, 1)
#        self.GL.btn1.clicked.connect(self.emitSignal)
#        
#    
#    def broadcast(self):
#        
#        print("I'm receiving an emitted signal!!!! Yabbadabbadooo")
#        
#    def emitSignal(self):
#        
#        self.simpleSig.emit()
#    
#    
#if __name__=='__main__':
#    app = QApplication(sys.argv)
#    widget = MyWidget()
#    widget.show()
#    app.exec_()

list = ['ascii', 'big5', 'big5hkscs', 'cp037', 'cp424', 'cp437', 'cp500', 'cp720', 'cp737', 'cp775', 'cp850', 'cp852', 'cp855', 'cp856', 'cp857', 'cp858', 'cp860', 'cp861', 'cp862', 'cp863', 'cp864', 'cp865', 'cp866', 'cp869', 'cp874', 'cp875', 'cp932', 'cp949', 'cp950', 'cp1006', 'cp1026', 'cp1140', 'cp1250', 'cp1251', 'cp1252', 'cp1253', 'cp1254', 'cp1255', 'cp1256', 'cp1257', 'cp1258', 'euc_jp', 'euc_jis_2004', 'euc_jisx0213', 'euc_kr', 'gb2312', 'gbk', 'gb18030', 'hz', 'iso2022_jp', 'iso2022_jp_1', 'iso2022_jp_2', 'iso2022_jp_2004', 'iso2022_jp_3', 'iso2022_jp_ext', 'iso2022_kr', 'latin_1', 'iso8859_2', 'iso8859_3', 'iso8859_4', 'iso8859_5', 'iso8859_6', 'iso8859_7', 'iso8859_8', 'iso8859_9', 'iso8859_10', 'iso8859_13', 'iso8859_14', 'iso8859_15', 'iso8859_16', 'johab', 'koi8_r', 'koi8_u', 'mac_cyrillic', 'mac_greek', 'mac_iceland', 'mac_latin2', 'mac_roman', 'mac_turkish', 'ptcp154', 'shift_jis', 'shift_jis_2004', 'shift_jisx0213', 'utf_32', 'utf_32_be', 'utf_32_le', 'utf_16', 'utf_16_be', 'utf_16_le', 'utf_7', 'utf_8', 'utf_8_sig']

s = "Mount Doom - Ft. Ren閑 Fleming"


print s.encode("gbk").decode("latin_1")

#for codepage in list:
#    for codepage2 in list:
#        try:
#            print s.encode(codepage).decode(codepage2)+"\t\t"+codepage+" "+codepage2
#        except: pass

# source: http://docs.python.org/2/library/codecs.html#standard-encodings


from PyQt4 import QtCore, QtGui
import sys

class MainWindow_UI(QtGui.QWidget):
    
    def __init__(self):
        
        super(MainWindow_UI, self).__init__()
        
        self.initUI()
        
        
    def initUI(self):
        
        self.GL = QtGui.QGridLayout(self)
        self.GL.input1 = QtGui.QLineEdit()
        self.GL.btn1 = QtGui.QPushButton()
        self.GL.btn1.clicked.connect(self.convert)
        self.GL.input2 = QtGui.QLineEdit()
        self.GL.addWidget(self.GL.input1, 0, 0, 1, 1)
        self.GL.addWidget(self.GL.btn1, 0, 1, 1, 1)
        self.GL.addWidget(self.GL.input2, 0, 2, 1, 1)
    
    
    
class MainWindow_CTR(MainWindow_UI):
    
    def __init__(self):
        
        super(MainWindow_CTR, self).__init__()
        
        self.show()
        
        
    def convert(self):
        
        a = "gbk"
        b = "Latin-1"
        text = str(self.GL.input1.text()).encode(a).decode(b)
        self.GL.input2.setText(text)
        self.GL.input2.copy()


def main():
    app = QtGui.QApplication(sys.argv)
    ex = MainWindow_CTR()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()