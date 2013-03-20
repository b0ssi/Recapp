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
#        # Enable mouse hover on_click tracking
#        self.setMouseTracking(True)
# 
#    def mouseMoveEvent(self, on_click):
#        # This is a QWidget provided on_click
#        # that fires for every mouse move on_click
#        # (In our case the move is also the hover)
#        print "Mouse Pointer is currently hovering at: ", on_click.pos()
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


#from PyQt4 import QtGui, QtCore
#import sys
#
#
#
#class MyWidget(QtGui.QWidget):
#    
#    def __init__(self):
#        
#        super(MyWidget, self).__init__()
#        
#        self.initUI()
#        
#        
#    def initUI(self):
#        
#        # setting up window
#        self.setMinimumSize(256, 256)
#        self.setMaximumSize(256, 256)
#        self.GL = QtGui.QGridLayout(self)
#        self.GL.setMargin(0)
#        
#        self.GL.myWidget2 = QtGui.QFrame()
#        self.GL.myWidget2.setMinimumSize(128, 128)
#        self.GL.myWidget2.setMaximumSize(128, 128)
#        self.GL.myWidget2.setStyleSheet("background: orange")
#        
#        self.GL.addWidget(self.GL.myWidget2)
#        self.GL.myWidget2.show()
#        self.GL.myWidget2.update()
#        self.GL.update()
#        self.update()
#        
#        
#        timer = QtCore.QTimer()
#        timer.singleShot(10, self.updatePosition)
#            
#        def updatePosition(self):
#            
#            self.GL.myWidget2.setGeometry(QtCore.QRect(0, 128, self.width(), self.height()))
#        
#
#
#if __name__ == '__main__':
#    app = QtGui.QApplication(sys.argv)
#    widget = MyWidget()
#    widget.show()
#    app.exec_()


#def getSize(start_path = '.'):
#    total_size = 0
#    for dirpath, dirnames, filenames in os.walk(start_path):
#        for f in filenames:
#            fp = os.path.join(dirpath, f)
#            total_size += os.path.getsize(fp)
#    # format byte-size
#    units = ["Byte", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"]
#    i = len(units)-1
#    for unit in units:
#        threshold = pow(1024, i)
#        if total_size > threshold:
#            total_size = str(round(int(total_size)/float(threshold), 2)) + " " + units[i]
#            break
#        i -= 1
#        
#    return total_size
#
#print getSize(os.path.realpath("Y:/_backup/0/2008-02-27 lifelike insect/03Textures"))

#def intToAlpha(number):
#    
#    base = 26
#    
#    
#    print "-------------------------------"
#    
#    while number > 1:
#        
#        rest = number%base
#        
#        print number
#        print rest
#    
#        number = (number-rest)/base
#    
#intToAlpha(27)

#def getDirSize(start_path = u'C:/'):
#    total_size = 0
#    for dirpath, dirnames, filenames in os.walk(start_path):
#        for f in filenames:
#            fp = os.path.join(dirpath, f)
#            total_size += os.path.getsize(fp)
#        
#    return total_size
##    return self.formatDirSize(total_size)
#
##print getDirSize()
#import win32file
#print win32file.GetDiskFreeSpaceEx(os.path.realpath(r"S:"))

#x = [
#     '"NAME_NOT_UNIQUE": "01467777700",',
#     '"ROOT_NODE_MUST_BE_RES": "014600",',
#     '"BAD_NAME_PARENT_OF_SHAPE_0": "145000",',
#     '"ARBITRARY_TRANSFORMS_GROUPS": "014400",',
#     '"BAD_NAME_SHAPE": "01430",',
#     '"ILLEGAL_DISPLAY_LAYER": "001420",',
#     '"MISSING_REF_TO_BASE_MOD_FOR_PUB_DEPENDANCY": "014100",',
#     '"FILE_NODE_DEAD_POINTER": "015100",',
#     '"FILE_NODE_INVALID_EXTENSION": "001370",',
#     '"ROOT_NODE_HAS_NO_CHILDREN": "013500",',
#     '"TRANSFORM_MULTIPLE_SHAPES_MIXED_CHILDREN": "136000",',
#     '"TRANSFORM_NO_CHILDREN": "013400",',
#     '"SHAPE_NO_CHILDREN": "001330",',
#     '"ILLEGAL_NODE_TYPE_IN_CONTEXT": "013200",',
#     '"ROOT_NODE_HAS_NO_CHILDREN_1": "001310",',
#     '"SINGLE_NODE_SUFFIX_MUST_BE_0": "001270",',
#     '"FIRST_NODE_IN_SEQUENCE_MUST_BE_1": "126000",',
#     '"OUT_OF_SEQUENCE_SUFFIX_NUMBER": "FF0012500",',
#     '"NAME_NOT_UNIQUE_1": "012400",',
#     '"NAME_RESERVED_FOR_SINGLE_JOINT_RIGS": "001230",',
#     '"ROOT_NODE_MUST_BE_RES_1": "0122100",',
#     '"BAD_NAME_PARENT_OF_SHAPE": "001210",',
#     '"BAD_NAME_TRANSFORM_OR_GROUP": "011700",',
#     '"BAD_NAME_FOR_SHAPE": "011600",',
#     '"NON_ZERO_TRANSFORM_FOR_PARENT_OF_SHAPE": "115000",',
#     '"NON_ZERO_ROTATE_FOR_PARENT_OF_SHAPE": "011400",',
#     '"SCALE_FOR_PARENT_OF_SHAPE_MUST_BE_1.0": "011300",',
#     '"NON_ZERO_SHEAR_FOR_PARENT_OF_SHAPE": "001120",',
#     '"NON_ZERO_ROTATE_AXIS_FOR_PARENT_OF_SHAPE": "111000",',
#     '"NON_ZERO_LOCAL_SCALE_PIVOT": "00180",',
#     '"NON_ZERO_LOCAL_ROTATE_PIVOT": "00170",',
#     '"SCALE_FOR_GROUPS_MUST_BE_1.0": "00160",',
#     '"NON_ZERO_SHEAR_FOR_GROUP": "00150",',
#     '"NON_ZERO_ROTATE_AXIS_FOR_GRO14UP": "000",',
#     '"NON_ZERO_LOCAL_SCALE_PIVOT13": "000",',
#     '"NON_ZERO_LOCAL_ROTATE_PIVOT12": "000",',
#     '"ATTR_MUST_BE_ENABLED": "00011",',
#     '"ATTR_MUST_BE_DISABLED": "0009",',
#     '"SMOOTH_MESH_PREVIEW_MUST_BE_DISABLED": "000",8',
#     '"SHAPE_CONTAINS_N_NGONS": "000"7,',
#     '"NAME_NOT_UNIQUE_2": "000"6,',
#     '"ROOT_NODE_MUST_BE_NAMED_X": "000"5,',
#     '"FIRST_CHILD_MUST_BE_GROUPS": "000"4,',
#     '"SECOND_CHILD_MUST_BE_GROUPS": "000"3,',
#     '"THIRD_CHILD_MUST_BE_GROUPS": "000",2',
#     '"BAD_NODE_NAME_FOR_SHAPE": "000"1'
#     ]
#
#x = sorted(x)
#for n in x:
#    print n

#class Bananen(object):
#    def __init__(self):
#        super(Bananen, self).__init__()
#
#    def __repr__(self):
#        name = "Bananen!!!"
#        return name
#bananen = Bananen()
#print bananen


#print(messages.databasex.access_denied("x", "doodle"))

#class Event(object):
#    def __init__(self):
#        self.handlers = set()
#
#    def add_event(self, handler):
#        self.handlers.add(handler)
#        return self
#
#    def remove_event(self, handler):
#        try:
#            self.handlers.remove(handler)
#        except:
#            raise ValueError("Handler is not handling this on_click, so can not "\
#                             "unhandle it.")
#        return self
#
#    def fire(self, *args, **kwargs):
#        for handler in self.handlers:
#            handler(*args, **kwargs)
#
#    def get_handler_count(self):
#        return len(self.handlers)
#
#    __iadd__ = add_event
#    __isub__ = remove_event
#    __call__ = fire
#    __len__ = get_handler_count
#
#
#class MyTrigger(object):
#    def __init__(self):
#        self.on_click = Event()
#
#    def click(self):
#        self.on_click("doodoo")
#
#
#def testination(x):
#    print(x)
#
#my_trigger = MyTrigger()
#my_trigger.on_click += testination
#my_trigger.click()


#class Event(object):
#    def __init__(self):
#        self.handlers = set()
#
#    def add_handler(self, handler):
#        self.handlers.add(handler)
#        print("'%s' successfully added to handlers." % (handler,))
#        return self
#
#    def remove_handler(self, handler):
#        try:
#            self.handlers.remove(handler)
#            print("'%s' successfully removed from handlers." % (handler,))
#        except:
#            print("This handler is not currently registered with the event "\
#                  "and can therefore not be detached.")
#        return self
#
#    def fire_handlers(self, *args, **kwargs):
#        for handler in self.handlers:
#            handler(*args, **kwargs)
#
#    def num_handlers(self):
#        return len(self.handlers)
#
#    def __repr__(self):
#        return str(self.handlers)
#
#    __iadd__ = add_handler
#    __isub__ = remove_handler
#    __call__ = fire_handlers
#    __len__ = num_handlers
#
#
#class MyTrigger(object):
#    def __init__(self):
#        self.event = Event()
#
#    def click(self, arg):
#        self.event(arg)
#
#
#def testionation(msg):
#    print("This is the message: '%s'" % (msg,))
#
#
## install event listener on object
#my_trigger = MyTrigger()
## add event(s)
#my_trigger.event += print
#my_trigger.event += testionation
## fire the trigger
#my_trigger.click("boooo!!!")

###############################################################################
#
#conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
#try:
#    conn.execute("DROP TABLE users")
#except:
#    pass
#conn.commit()
#conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, password TEXT UNIQUE, username TEXT UNIQUE, username2 TEXT UNIQUE, x7 TEXT UNIQUE)")
##conn.execute("CREATE TABLE users (password TEXT, username TEXT, username2 TEXT, x7 BOOL)")
#conn.commit()
#start = time.clock()
#for i in range(100000):
#    conn.execute("INSERT INTO users "\
#                    "(password, username, username2, x7) "\
#                    "VALUES (?, ?, ?, ?)",
#                    (random.randint(1000000000000000, 9999999999999999), random.randint(1000000000000000, 9999999999999999), random.randint(1000000000000000, 9999999999999999), random.randint(1000000000000000, 9999999999999999))
#                )
##    conn.commit()
#conn.commit()
#print("Time elapsed: %s" % (time.clock() - start,))
#conn.close()
###############################################################################
#
##conn = sqlite3.connect(":memory:")
##conn.execute("CREATE TABLE test (data INTEGER)")
#l = []
#for path in os.walk(os.path.realpath("C:/")):
#    l.append(path[0])
#    for file in path[2]:
#        l.append(file)
##    conn.execute("INSERT INTO test VALUES (?)", (str(random.randint(1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000, 9999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999)), ))
##conn.commit()
#print("start")
#print(len(l))
#for i in range(30):
#    print(l[i])
#time.sleep(10)
###############################################################################


#x = re.search("^([\_a-zA-Z]){1}([\_a-zA-Z0-9]){3,}$", "_a12")
#
#print(x.group(0))
#print(x.group(1))
#print(x.group(2))

###############################################################################

import importlib
import inspect

try:
    x = importlib.import_module(str("bs.tests.unitTestModule"))
except SyntaxError as e:
    print("shit! %s" % (e, ))

###############################################################################
