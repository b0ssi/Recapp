# -*- encoding: utf-8 -*-
from genericpath import exists
import Crypto.Cipher.AES
import Crypto.Random
import Crypto.Util.Counter
import bs.utils
import gzip
import hashlib
import hashlib
import logging
import lzma
import math
import multiprocessing
import os
import random
import re
import sqlite3
import tempfile
import threading
import time
import time
import win32api
import win32api
import win32file
import zipfile
import zlib

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
#conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, password_hash TEXT UNIQUE, username TEXT UNIQUE, username2 TEXT UNIQUE, x7 TEXT UNIQUE)")
##conn.execute("CREATE TABLE users (password_hash TEXT, username TEXT, username2 TEXT, x7 BOOL)")
#conn.commit()
#start = time.clock()
#for i in range(100000):
#    conn.execute("INSERT INTO users "\
#                    "(password_hash, username, username2, x7) "\
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

#import importlib
#import inspect
#
#try:
#    x = importlib.import_module(str("bs.tests.unitTestModule"))
#except SyntaxError as e:
#    print("shit! %s" % (e, ))

###############################################################################

#start = time.clock()
#for n in range(10000):
#    conn = sqlite3.connect("Z:\\test.sqlite")
##    conn.execute("CREATE TABLE benchmark (id INTEGER PRIMARY KEY, name TEXT)")
#    res = conn.execute("SELECT * FROM benchmark").fetchall()
##    res = conn.execute("INSERT INTO benchmark (name) VALUES (?)", (str(random.randint(1000000, 9999999)), ))
#    conn.commit()
##    conn.execute("DROP TABLE test")
#    conn.close()
#end = time.clock()
#print("Finished in %ss" % (end - start))

###############################################################################

#pattern = "^([^\_0-9][a-zA-Z0-9\_]{2,32}[^\_])(\,\ [^\_0-9][a-zA-Z0-9\_]{2,32}[^\_])*$"
#text = "dfgh234, as_43df_"
#res = re.search(pattern, text)
#if res:
#    if res.group(1):
#        print("Group1: %s" % res.group(1))
#    if res.group(2):
#        print("Group2: %s" % res.group(2))

###############################################################################

#c = "*"
#
#if not 2 == 2 or\
#    not 2 == 3 and\
#    not c == "*.":
#    print("Booooo")
#else:
#    print("BAAAHAHAHAH!")

###############################################################################

#import bs.utils
#s = bs.utils.BSString("Whoohoo")
#print(s.endswith("", "hoo", "x", "sldfk", "sdf", "w849"))

###############################################################################

#import win32wnet
#
#ass = "cdefghijklmnopqrstuvwxyz"
#for a in ass:
#    try:
#        drive_letter = a+":\\"
#        size = win32api.GetDiskFreeSpaceEx(drive_letter)
#        if os.path.isdir(drive_letter):
#            print(win32api.GetVolumeInformation(drive_letter))
#            print("%s: %s" % (drive_letter, size[1]))
#    except:
#        pass

###############################################################################

#import win32com.client
#WMIS = win32com.client.GetObject(r"winmgmts:root\cimv2")
#objs = WMIS.ExecQuery("select * from Win32_PhysicalMedia")
#for obj in objs:
#    print("--------------------------------")
#    print(dir(obj))
#    print(obj.SerialNumber)
#    print(obj.Tag)

###############################################################################

#import win32con
#file_path = "Z:\\x.FVA"
##handle = win32file.CreateFile(file_path, win32con.GENERIC_READ|win32con.GENERIC_WRITE,win32con.FILE_SHARE_READ|win32con.FILE_SHARE_WRITE,None,win32con.OPEN_EXISTING,0,0)
#handle = win32file.CreateFile(file_path, win32con.GENERIC_READ, win32con.FILE_SHARE_READ, None, win32con.OPEN_EXISTING, 0, 0)
#xs = win32file.GetFileInformationByHandleEx(handle, 18)
#print(xs)
#for x in xs:
#    print("%s: %s" % (x, xs[x],))

###############################################################################


class Backup(object):
    """
    *
    """
    _backup_set = None
    _sources = None
    _targets = None
    _db_path = None
    _tmp_dir = None

    def __init__(self, set, sources, targets, db_path):
        """
        *
        """
        self._backup_set = set
        self._sources = sources
        self._targets = targets
        self._db_path = db_path
        self._tmp_dir = tempfile.TemporaryDirectory()

    def _update_db(self, db_path):
        """
        *
        Returns the name of the new (session-)column
        """
        conn = sqlite3.connect(db_path)
        # create tables
        conn.execute("CREATE TABLE IF NOT EXISTS lookup (id INTEGER PRIMARY KEY, "\
                                                        "path TEXT UNIQUE, "\
                                                        "ctime REAL, "\
                                                        "mtime REAL, "\
                                                        "atime REAL, "\
                                                        "inode INTEGER, "\
                                                        "size INTEGER, "\
                                                        "sha512 TEXT)")
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS lookup_path ON lookup (path)")
        # a hash index table with all hashes (data-streams) in backup-set.
        conn.execute("CREATE TABLE IF NOT EXISTS sha512_index (sha512 TEXT PRIMARY KEY)")
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS sha512_index_sha512 ON sha512_index (sha512)")

        conn.execute("CREATE TABLE IF NOT EXISTS path (id INTEGER PRIMARY KEY)")
        conn.execute("CREATE TABLE IF NOT EXISTS ctime (id INTEGER PRIMARY KEY)")
        conn.execute("CREATE TABLE IF NOT EXISTS mtime (id INTEGER PRIMARY KEY)")
        conn.execute("CREATE TABLE IF NOT EXISTS atime (id INTEGER PRIMARY KEY)")
        conn.execute("CREATE TABLE IF NOT EXISTS inode (id INTEGER PRIMARY KEY)")
        conn.execute("CREATE TABLE IF NOT EXISTS size (id INTEGER PRIMARY KEY)")
        conn.execute("CREATE TABLE IF NOT EXISTS sha512 (id INTEGER PRIMARY KEY)")
        conn.commit()
        # create new columns for current run
        # on fast successive attempts same name might be produced (based on unix
        # timestamp) so, cycle through and update timestamp string in name until
        # success
        new_columns_created = False
        while not new_columns_created:
            new_column_name = "snapshot_%s" % (int(time.time()), )
            try:
                conn.execute("ALTER TABLE path ADD COLUMN %s TEXT"
                             % (new_column_name, ))
                conn.execute("ALTER TABLE ctime ADD COLUMN %s REAL"
                             % (new_column_name, ))
                conn.execute("ALTER TABLE mtime ADD COLUMN %s REAL"
                             % (new_column_name, ))
                conn.execute("ALTER TABLE atime ADD COLUMN %s REAL"
                             % (new_column_name, ))
                conn.execute("ALTER TABLE inode ADD COLUMN %s INTEGER"
                             % (new_column_name, ))
                conn.execute("ALTER TABLE size ADD COLUMN %s INTEGER"
                             % (new_column_name, ))
                conn.execute("ALTER TABLE sha512 ADD COLUMN %s TEXT"
                             % (new_column_name, ))
                new_columns_created = True
            except:
                time.sleep(0.5)
        conn.close()
        return new_column_name

    def _update_data_in_db(self, new_column_name, **kwargs):
        """
        *
        """
        columns_to_update = []
        columns_to_update_data = []
        try:
            entity_id = kwargs["entity_id"]
            columns_to_update.append("id")
            columns_to_update_data.append(entity_id)
        except: pass
        try:
            file_path = kwargs["file_path"]
            columns_to_update.append("path")
            columns_to_update_data.append(file_path)
        except: pass
        try:
            file_ctime = kwargs["file_ctime"]
            columns_to_update.append("ctime")
            columns_to_update_data.append(file_ctime)
        except: pass
        try:
            file_mtime = kwargs["file_mtime"]
            columns_to_update.append("mtime")
            columns_to_update_data.append(file_mtime)
        except: pass
        try:
            file_atime = kwargs["file_atime"]
            columns_to_update.append("atime")
            columns_to_update_data.append(file_atime)
        except: pass
        try:
            file_inode = kwargs["file_inode"]
            columns_to_update.append("inode")
            columns_to_update_data.append(file_inode)
        except: pass
        try:
            file_size = kwargs["file_size"]
            columns_to_update.append("size")
            columns_to_update_data.append(file_size)
        except: pass
        try:
            file_sha512 = kwargs["file_sha512"]
            columns_to_update.append("sha512")
            columns_to_update_data.append(file_sha512)
        except: pass

        try:
            conn = sqlite3.connect(self._db_path)
            # check if entity already exists
            res = conn.execute("SELECT id FROM lookup WHERE id = ?", (entity_id, )).fetchall()
            # new entity
            if len(res) == 0:
                # write data to database
                conn.execute("INSERT INTO lookup (id, path, ctime, mtime, atime, inode, size, sha512) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (entity_id, file_path, file_ctime, file_mtime, file_atime, file_inode, file_size, file_sha512 ))

                conn.execute("INSERT INTO path (id, %s) VALUES (?, ?)" % (new_column_name, ), (entity_id, file_path, ))
                conn.execute("INSERT INTO ctime (id, %s) VALUES (?, ?)" % (new_column_name, ), (entity_id, file_ctime, ))
                conn.execute("INSERT INTO mtime (id, %s) VALUES (?, ?)" % (new_column_name, ), (entity_id, file_mtime, ))
                conn.execute("INSERT INTO atime (id, %s) VALUES (?, ?)" % (new_column_name, ), (entity_id, file_atime, ))
                conn.execute("INSERT INTO inode (id, %s) VALUES (?, ?)" % (new_column_name, ), (entity_id, file_inode, ))
                conn.execute("INSERT INTO size (id, %s) VALUES (?, ?)" % (new_column_name, ), (entity_id, file_size, ))
                conn.execute("INSERT INTO sha512 (id, %s) VALUES (?, ?)" % (new_column_name, ), (entity_id, file_sha512, ))
                logging.debug("New Entity added: %s" % (entity_id, ))
            # existing entity
            else:
                # update lookup
                if len(columns_to_update) > 0:
                    # generate SQL code
                    setters = ""
                    for column in columns_to_update:
                        setters += "%s = ?, " % (column, )
                    setters = setters[:-2] + " WHERE id = " + str(entity_id)
                    conn.execute("UPDATE lookup SET %s" % (setters, ), list(columns_to_update_data))
                    logging.debug("lookup updated: %s" % (entity_id, ))
                # update path
                try:
                    conn.execute("UPDATE path SET %s = ? WHERE id = ?" % (new_column_name, ), (file_path, entity_id, ))
                    logging.debug("path updated: %s" % (entity_id, ))
                except: pass
                # update ctime
                try:
                    conn.execute("UPDATE ctime SET %s = ? WHERE id = ?" % (new_column_name, ), (file_ctime, entity_id, ))
                    logging.debug("ctime updated: %s" % (entity_id, ))
                except: pass
                # update mtime
                try:
                    conn.execute("UPDATE mtime SET %s = ? WHERE id = ?" % (new_column_name, ), (file_mtime, entity_id, ))
                    logging.debug("mtime updated: %s" % (entity_id, ))
                except: pass
                # update atime
                try:
                    conn.execute("UPDATE atime SET %s = ? WHERE id = ?" % (new_column_name, ), (file_atime, entity_id, ))
                    logging.debug("atime updated: %s" % (entity_id, ))
                except: pass
                # update inode
                try:
                    conn.execute("UPDATE inode SET %s = ? WHERE id = ?" % (new_column_name, ), (file_inode, entity_id, ))
                    logging.debug("inode updated: %s" % (entity_id, ))
                except: pass
                # update size
                try:
                    conn.execute("UPDATE size SET %s = ? WHERE id = ?" % (new_column_name, ), (file_size, entity_id, ))
                    logging.debug("size updated: %s" % (entity_id, ))
                except: pass
                # update sha512
                # update sha512_index
                try:
                    conn.execute("UPDATE sha512 SET %s = ? WHERE id = ?" % (new_column_name, ), (file_sha512, entity_id, ))
                    logging.debug("sha512 updated: %s" % (entity_id, ))
                except: pass

            # add hash to db and stream to targets
            try:
                if len(conn.execute("SELECT sha512 FROM sha512_index WHERE sha512 = ?", (file_sha512, )).fetchall()) == 0:
                    conn.execute("INSERT INTO sha512_index (sha512) VALUES (?)", (file_sha512, ))
                    logging.debug("sha512_index updated: %s" % (entity_id, ))
            except: pass

            conn.commit()
            conn.close()
        except:
            raise

    def backup_exec(self):
        # update database
        new_column_name = self._update_db(self._db_path)

        conn = sqlite3.connect(self._db_path)
        bytes_processed = [0, 0]
        files_processed = 0

        time_start = time.time()
        i = 0
        for source in self._sources:
            for folder_path, folders, files in os.walk(source):
                for file in files:
                    # create file object
                    file_obj = BackupFile(self._backup_set,
                                          os.path.join(folder_path, file),
                                          self._targets,
                                          self._tmp_dir,
                                          "my_ultrasecure_password")

                    entity_datas = conn.execute("SELECT id, path, ctime, mtime, atime, inode, size, sha512 FROM lookup WHERE path = ?", (file_obj.path, )).fetchall()
                    # new path
                    if len(entity_datas) == 0:
                        # create new entity
                        # AQUIRE NEW ID
                        entity_id = conn.execute("SELECT MAX(rowid) AS rowid FROM lookup").fetchone()[0]
                        if not entity_id:
                            entity_id = 1
                        else:
                            entity_id += 1
                        logging.info("Entity %s is new: %s"
                                     % (entity_id, file_obj.path, ))
                        # this might still be an identic data-stream that existed
                        # under a different path/entity before, so only back-up
                        # if hash is unique
                        if len(conn.execute("SELECT sha512 FROM sha512_index WHERE sha512 = ?",
                                            (file_obj.sha512, )).fetchall()) == 0:
                            # BACKUP
                            file_obj.backup()
                        # UPDATE DB
                        self._update_data_in_db(new_column_name,
                                          entity_id=entity_id,
                                          file_path=file_obj.path,
                                          file_ctime=file_obj.ctime,
                                          file_mtime=file_obj.mtime,
                                          file_atime=file_obj.atime,
                                          file_inode=file_obj.inode,
                                          file_size=file_obj.size,
                                          file_sha512=file_obj.sha512)
                    # existing path
                    elif len(entity_datas) == 1:
                        entity_id = entity_datas[0][0]
                        entity_path = entity_datas[0][1]
                        entity_ctime = entity_datas[0][2]
                        entity_mtime = entity_datas[0][3]
                        entity_atime = entity_datas[0][4]
                        entity_inode = entity_datas[0][5]
                        entity_size = entity_datas[0][6]
                        entity_sha512 = entity_datas[0][7]

                        if file_obj.path == entity_path: path = 1
                        else: path = 0
                        if file_obj.ctime == entity_ctime: ctime = 1
                        else: ctime = 0
                        if file_obj.mtime == entity_mtime: mtime = 1
                        else: mtime = 0
                        if file_obj.atime == entity_atime: atime = 1
                        else: atime = 0
                        if file_obj.size == entity_size: size = 1
                        else: size = 0

                        combinations = "%s%s%s%s%s" % (path, ctime, mtime, atime, size, )

                        if combinations == "00000":
                            # ERROR: inode same but ctime changed
                            logging.warning("Unhandled combination: %s: %s" % (combinations, file_obj.path, ))
                        if combinations == "00001":
                            # ERROR: inode same but ctime changed
                            logging.warning("Unhandled combination: %s: %s" % (combinations, file_obj.path, ))
                        if combinations == "00010":
                            # ERROR: inode same but ctime changed
                            logging.warning("Unhandled combination: %s: %s" % (combinations, file_obj.path, ))
                        if combinations == "00011":
                            # ERROR: inode same but ctime changed
                            logging.warning("Unhandled combination: %s: %s" % (combinations, file_obj.path, ))
                        if combinations == "00100":
                            # ERROR: inode same but ctime changed
                            logging.warning("Unhandled combination: %s: %s" % (combinations, file_obj.path, ))
                        if combinations == "00101":
                            # ERROR: inode same but ctime changed
                            logging.warning("Unhandled combination: %s: %s" % (combinations, file_obj.path, ))
                        if combinations == "00110":
                            # ERROR: inode same but ctime changed
                            logging.warning("Unhandled combination: %s: %s" % (combinations, file_obj.path, ))
                        if combinations == "00111":
                            # ERROR: inode same but ctime changed
                            logging.warning("Unhandled combination: %s: %s" % (combinations, file_obj.path, ))
                        if combinations == "01000":
                            # OK: simple move and change in mtime, size and recent access
                            logging.warning("Unhandled combination: %s: %s" % (combinations, file_obj.path, ))
                        if combinations == "01001":
                            # OK: simple move and change in mtime, size same and recent access
                            logging.warning("Unhandled combination: %s: %s" % (combinations, file_obj.path, ))
                        if combinations == "01010":
                            # OK: simple move and change in mtime, size
                            logging.warning("Unhandled combination: %s: %s" % (combinations, file_obj.path, ))
                        if combinations == "01011":
                            # OK: simple move and change in mtime, size same
                            logging.warning("Unhandled combination: %s: %s" % (combinations, file_obj.path, ))
                        if combinations == "01100":
                            # ERROR: mtime same but size changed
                            logging.warning("Unhandled combination: %s: %s" % (combinations, file_obj.path, ))
                        if combinations == "01101":
                            # OK: simple move plus recent access
                            logging.warning("Unhandled combination: %s: %s" % (combinations, file_obj.path, ))
                        if combinations == "01110":
                            # ERROR: mtime same but size changed
                            logging.warning("Unhandled combination: %s: %s" % (combinations, file_obj.path, ))
                        if combinations == "01111":
                            # OK: simple move
                            logging.warning("Unhandled combination: %s: %s" % (combinations, file_obj.path, ))
                        if combinations == "10000":
                            # ERROR: inode same but ctime changed
                            logging.warning("Unhandled combination: %s: %s" % (combinations, file_obj.path, ))
                        if combinations == "10001":
                            # ERROR: inode same but ctime changed
                            logging.warning("Unhandled combination: %s: %s" % (combinations, file_obj.path, ))
                        if combinations == "10010":
                            # ERROR: inode same but ctime changed
                            logging.warning("Unhandled combination: %s: %s" % (combinations, file_obj.path, ))
                        if combinations == "10011":
                            # ERROR: inode same but ctime changed
                            logging.warning("Unhandled combination: %s: %s" % (combinations, file_obj.path, ))
                        if combinations == "10100":
                            # ERROR: inode same but ctime changed
                            logging.warning("Unhandled combination: %s: %s" % (combinations, file_obj.path, ))
                        if combinations == "10101":
                            # ERROR: ctime, atime changed
                            logging.warning("Unhandled combination: %s: %s" % (combinations, file_obj.path, ))
                        if combinations == "10110":
                            # ERROR: inode same but ctime changed
                            logging.warning("Unhandled combination: %s: %s" % (combinations, file_obj.path, ))
                        if combinations == "10111":
                            # ERROR: inode same but ctime changed
                            logging.warning("Unhandled combination: %s: %s" % (combinations, file_obj.path, ))
                        if combinations == "11000":
                            # OK: mtime, atime, size changed, rest same
                            logging.info("OK: %s: %s" % (combinations, file_obj.path, ))
                            self._update_data_in_db(new_column_name,
                                                    entity_id=entity_id,
                                                    file_mtime=file_obj.mtime,
                                                    file_atime=file_obj.atime,
                                                    file_size=file_obj.size,
                                                    file_sha512=file_obj.sha512)
                            # BACKUP
                            if len(conn.execute("SELECT sha512 FROM sha512_index WHERE sha512 = ?",
                                                (file_obj.sha512, )).fetchall()) == 0:
                                file_obj.backup()
                        if combinations == "11001":
                            # OK: mtime and atime changed, rest same
                            logging.info("OK: %s: %s" % (combinations, file_obj.path, ))
                            self._update_data_in_db(
                                                    new_column_name,
                                                    entity_id=entity_id,
                                                    file_mtime=file_obj.mtime,
                                                    file_atime=file_obj.atime)
                            # BACKUP
                            if len(conn.execute("SELECT sha512 FROM sha512_index WHERE sha512 = ?",
                                                (file_obj.sha512, )).fetchall()) == 0:
                                file_obj.backup()
                        if combinations == "11010":
                            # OK: regular edit, mtime, size changed, rest same
                            logging.info("OK: %s: %s" % (combinations, file_obj.path, ))
                            self._update_data_in_db(new_column_name,
                                                    entity_id=entity_id,
                                                    file_mtime=file_obj.mtime,
                                                    file_size=file_obj.size,
                                                    file_sha512=file_obj.sha512)
                            # BACKUP
                            if len(conn.execute("SELECT sha512 FROM sha512_index WHERE sha512 = ?",
                                                (file_obj.sha512, )).fetchall()) == 0:
                                file_obj.backup()
                        if combinations == "11011":
                            # OK: only mtime changed. size same
                            logging.info("OK: %s: %s" % (combinations, file_obj.path, ))
                            self._update_data_in_db(new_column_name,
                                                    entity_id=entity_id,
                                                    file_mtime=file_obj.mtime)
                            # BACKUP
                            if len(conn.execute("SELECT sha512 FROM sha512_index WHERE sha512 = ?",
                                                (file_obj.sha512, )).fetchall()) == 0:
                                file_obj.backup()
                        if combinations == "11100":
                            # ERROR: size and only atime have changed
                            logging.warning("Unhandled combination: %s: %s" % (combinations, file_obj.path, ))
                        if combinations == "11101":
                            # OK: no change but has been accessed recently
                            logging.info("OK: %s: %s" % (combinations, file_obj.path, ))
                        if combinations == "11110":
                            # ERROR: size has changed but rest is unchanged
                            logging.warning("Unhandled combination: %s: %s" % (combinations, file_obj.path, ))
                        if combinations == "11111":
                            # OK: no change at all
                            pass

                    if i % 1 == 0:
                            print("%i files/s" % (i / (time.time() - time_start - 0.001), ))
                    i += 1
                conn.commit()
        return True


class BackupFile(object):
    """
    *
    """
    _backup_set = None
    _path = None
    _targets = None
    _target_archive_max_size = 1024 * 1024 * 12
    _sha512 = None
    _ctime = None
    _mtime = None
    _atime = None
    _inode = None
    _size = None
    _compression_level = 6
    _buffer_size = 1024 * 1024
    _password_hash = None
    _tmp_dir = None
    _tmp_file_path = None

    def __init__(self, backup_set, file_path, targets, tmp_dir, password):
        """
        *
        """
        self._backup_set = backup_set
        self._path = os.path.realpath(file_path)
        self._targets = targets
        # get file stats
        stat = os.stat(self._path)
        self._ctime = stat.st_ctime
        self._mtime = stat.st_mtime
        self._atime = stat.st_atime
        self._inode = stat.st_ino
        self._size = stat.st_size
        self._tmp_dir = tmp_dir
        # set password
        self.password_hash = password

    def __del__(self):
        self.remove_tmp_file()

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self):
        return None

    @property
    def ctime(self):
        return self._ctime

    @ctime.setter
    def ctime(self):
        return None

    @property
    def mtime(self):
        return self._mtime

    @mtime.setter
    def mtime(self):
        return None

    @property
    def atime(self):
        return self._atime

    @atime.setter
    def atime(self):
        return None

    @property
    def inode(self):
        return self._inode

    @inode.setter
    def inode(self):
        return None

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self):
        return None

    @property
    def sha512(self):
        if self._sha512:
            return self._sha512
        else:
            self._sha512 = bs.utils.HashFile(self._path).start()
            return self._sha512

    @sha512.setter
    def sha512(self):
        return None

    @property
    def password_hash(self):
        if not self._password_hash:
            logging.critical("%s: Password not set." % (self.__class__.__name__))
            raise SystemExit()
        else:
            return self._password_hash

    @password_hash.setter
    def password_hash(self, arg):
        self._password_hash = hashlib.sha256(arg.encode()).digest()

    def backup(self):
        """
        *
        """
        self.compress_zlib_encrypt_aes()

    def remove_tmp_file(self):
        """
        *
        """
        try:
            os.unlink(self._tmp_file_path)
            return True
        except:
            return False

    def compress_zlib_encrypt_aes(self):
        """
        *
        """
        time_start = time.time()
        logging.debug("%s: Compressing (zlib)/encrypting (AES) file: %s" % (self.__class__.__name__, self._path, ))

        f_in = open(self._path, "rb")
        f_out = tempfile.NamedTemporaryFile(dir=self._tmp_dir.name, mode="a+b", delete=False)

        compression_obj = zlib.compressobj(level=self._compression_level)

        iv = Crypto.Random.new().read(Crypto.Cipher.AES.block_size)
        counter = Crypto.Util.Counter.new(128)
        aes = Crypto.Cipher.AES.new(self.password_hash, Crypto.Cipher.AES.MODE_CTR, iv, counter)

        f_out.write(iv)
        data_processed = 0
        while True:
            data = f_in.read(self._buffer_size)
            if not data:
                break
            data_compressed = compression_obj.compress(data)
            data_compressed += compression_obj.flush(zlib.Z_SYNC_FLUSH)
            data_compressed_encrypted = aes.encrypt(data_compressed)
            f_out.write(data_compressed_encrypted)

#            data_processed += self._buffer_size
#            print("%s: Data compressed/encrypted: %s (%s/s)"
#                  % (self.__class__.__name__,
#                     bs.utils.format_data_size(data_processed),
#                     bs.utils.format_data_size(data_processed / (time.time() - time_start))))
        data_compressed = compression_obj.flush(zlib.Z_FINISH)
        data_compressed_encrypted = aes.encrypt(data_compressed)
        f_out.write(data_compressed_encrypted)

        f_in.close()
        f_out.close()
        self.remove_tmp_file()
        self._tmp_file_path = f_out.name

        time_elapsed = time.time() - time_start
        logging.debug("%s: Compression/Encryption done (%.2fs)." % (self.__class__.__name__, time_elapsed))
        # add to target(s)
        self.add_to_targets()

    def compress_bz2(self):
        """
        *
        """
        pass

    def compress_lzma(self):
        """
        *
        """
        pass

    def add_to_targets(self):
        """
        *
        """
        backup_archive_name = self.get_current_backup_archive_name()

        time_start = time.time()
        logging.debug("%s: Adding to target archive(s): %s" % (self.__class__.__name__, backup_archive_name, ))

        for target in self._targets:
            backup_archive_path = os.path.join(target, self._backup_set, backup_archive_name)
            f_archive = zipfile.ZipFile(backup_archive_path, "a", allowZip64=True)
            # only add if not already exist
            members = f_archive.namelist()
            if self.sha512 not in members:
                f_archive.write(self._tmp_file_path, arcname=self.sha512)
                f_archive.close()

                time_elapsed = time.time() - time_start
                logging.debug("%s: Successfully added to target archive(s) (%.2fs)." % (self.__class__.__name__, time_elapsed))
            else:
                logging.warning("%s: The backup file already exists in the current archive file: %s" % (self.__class__.__name__, self.sha512))


    def get_current_backup_archive_name(self):
        """
        *
        """
        # ABSTRACT
        # scan all targets, select latest archive name of all of them
        # construct path for latest backup archive, if found
        # if latest archive found and size below threshold, use this latest archive
            # on all targets:
                # create archive on all targets/check for valid file if exists
                # on fail: SystemExit
        # if no archive found at all or latest found archive exceeds size threshold:
            # create new archive name
            # for all targets
                # create set path, archive
                # on fail: SystemExit
        # return latest/new archive name

        latest_archive_name = None
        # scan all targets, select latest archive name of all of them
        for target_path in self._targets:
            # create set dir
            backup_set_path = os.path.join(target_path, self._backup_set)
            if not os.path.isdir(backup_set_path):
                os.makedirs(backup_set_path)
            for folder_path, folders, files in os.walk(backup_set_path):
                folders = []
                for file in sorted(files, reverse=True):
                    try:
                        file_path = os.path.join(folder_path, file)
                        # if found latest archive (name) is "newer" than
                        # current latest_archive_name, replace with current
                        if not latest_archive_name or\
                            int(os.path.splitext(file)[0]) > int(os.path.splitext(latest_archive_name)[0]):
                            latest_archive_name = file
                        break
                    except:
                        pass
        # construct path for latest backup archive, if found
        backup_archive_path = None
        try:
            backup_archive_path = os.path.join(backup_set_path, latest_archive_name)
        except: pass
        # if latest archive found and size below threshold, use this latest archive
        if latest_archive_name and\
            backup_archive_path and\
            os.path.getsize(backup_archive_path) < self._target_archive_max_size:
            # on all targets:
            for target_path in self._targets:
                backup_set_path = os.path.join(target_path, self._backup_set)
                # create archive on all targets/check for valid file if exists
                if not os.path.isfile(backup_archive_path):
                    try:
                        f = zipfile.ZipFile(backup_archive_path, "w")
                        f.close()
                    # on fail: SystemExit
                    except Exception as e:
                        raise SystemExit(e)
        # if no archive found at all or latest found archive exceeds size threshold:
        else:
            # create new archive name
            new_archive_name = str(int(time.time())) + ".zip"
            # for all targets
            for target_path in self._targets:
                new_archive_path = os.path.join(target_path,
                                                self._backup_set,
                                                new_archive_name)
                # create set path, archive
                try:
                    f = zipfile.ZipFile(new_archive_path, "w")
                    f.close()
                    latest_archive_name = new_archive_name
                # on fail: SystemExit
                except Exception as e:
                    raise SystemExit(e)
        return latest_archive_name


class BackupRestore(object):
    _backup_archive_path = None
    _target_path = None
    _tmp_dir = None
    _tmp_file_path = None
    _password_hash = None
    _buffer_size = 32768

    def __init__(self, backup_archive_path, target_path):
        self._backup_archive_path = backup_archive_path
        self._target_path = target_path
        self._tmp_dir = tempfile.TemporaryDirectory()
        self._password_hash = "passwordpassword"

        self.unzip_file("a62b6e53efffb48eba0efa0aafdeb8cb8ad28df10c948f27c0dd846056dc3ba41c692a400ad92a2c19876f3447b973abb3eac24f169798f04521f2bd3633f83b")
        self.decrypt_file()
        self.unzlib_file()

    def remove_tmp_file(self):
        try:
            os.unlink(self._tmp_file_path)
            return True
        except:
            raise
#            return False

    def unzip_file(self, file_to_extract_name):
        time_start = time.time()
        logging.debug("%s: Unzipping file: %s" % (self.__class__.__name__, file_to_extract_name, ))

        f_zip = zipfile.ZipFile(self._backup_archive_path, mode="r")

#        self.remove_tmp_file()
        self._tmp_file_path = f_zip.extract(file_to_extract_name, path=self._tmp_dir.name)

        time_elapsed = time.time() - time_start
        logging.debug("%s: File successfully unzipped (%.2fs)." % (self.__class__.__name__, time_elapsed))

    def decrypt_file(self):
        time_start = time.time()
        logging.debug("%s: Decrypting (AES) file..." % (self.__class__.__name__, ))

        f_in = open(self._tmp_file_path, "rb")
        f_tmp = tempfile.NamedTemporaryFile(dir=self._tmp_dir.name, mode="a+b", delete=False)
        iv = f_in.read(Crypto.Cipher.AES.block_size)
        counter = Crypto.Util.Counter.new(128)
        aes = Crypto.Cipher.AES.new(self._password_hash, Crypto.Cipher.AES.MODE_CTR, iv, counter)
        while True:
            data = f_in.read(self._buffer_size)
            if not data:
                break
            data_decrypted = aes.decrypt(data)
            f_tmp.write(data_decrypted)
        f_tmp.close()
        f_in.close()

        self.remove_tmp_file()
        self._tmp_file_path = f_tmp.name

        time_elapsed = time.time() - time_start
        logging.debug("%s: File successfully decrypted (%.2fs)." % (self.__class__.__name__, time_elapsed))

    def unzlib_file(self):
        time_start = time.time()
        logging.debug("%s: Decompressing (zlib) file: %s" % (self.__class__.__name__, self._target_path, ))

        decompression_obj = zlib.decompressobj()
        f_in = open(self._tmp_file_path, "rb")
        f_out = open(os.path.join(self._target_path, "out"), "a+b")
        while True:
            data = f_in.read(self._buffer_size)
            if not data:
                break
            data_decompressed = decompression_obj.decompress(data)
            f_out.write(data_decompressed)
            f_out.write(decompression_obj.flush(zlib.Z_SYNC_FLUSH))
        f_out.write(decompression_obj.flush(zlib.Z_FINISH))
#        for line in f_in:
#            f_out.write(line)
        f_in.close()
        f_out.close()

        self.remove_tmp_file()
        self._tmp_file_path = None

        time_elapsed = time.time() - time_start
        logging.debug("%s: Compression done (%.2fs)." % (self.__class__.__name__, time_elapsed))

# logging
#logger = logging.Logger('root')
logging.basicConfig(format="--------------- "\
                           "%(module)s: %(lineno)s "\
                           "(%(funcName)s)\r"\
                           "%(levelname)s      \t"\
                           "%(message)s",
                    level=logging.CRITICAL)

time_start = time.time()

my_backup = Backup(
                   "backup_test",
                   ["Y:\\_TMP\\bsTest\\sx2"],
                   ["Y:\\_TMP\\bsTest\\t1",
                    "Y:\\_TMP\\bsTest\\t2"
                    ],
                   "Z:\\test.sqlite"
                   )
my_backup.backup_exec()

#my_backup_restore = BackupRestore(r"Y:\_TMP\bsTest\t1\backup_test\1365492971.zip",
#                                  r"Y:\_TMP\bsTest\t1\backup_test")

print("Time elapsed: %s" % (time.time() - time_start))

###############################################################################
