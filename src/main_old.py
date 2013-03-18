# -*- coding: utf-8 -*-
'''
Created on 19/11/2012

@author: frieder.czeschla
'''
from PyQt4 import QtCore, QtGui
from bop.jobs import BOp_Jobs_CTR
from mod1.pack1 import nsOs
import config
import hashlib
import json
import logging
import os
import re
import sqlite3
import sys
import time

# imports
#import shutil, datetime, random, win32file, win32api

print(sys.version)
# current error code: EC0003
# set up logging
# create config dir
#CONFIG_PATH = os.path.normcase(os.path.join(str(QtCore.QDir.homePath()), ".backupshizzle"))
#
#LOGFILE_PATH = os.path.join(CONFIG_PATH, "log.log")
#CONFIGDB_PATH = os.path.join(CONFIG_PATH, "globalConfig.sqlite")
#BT_BASEDIR_PATH = "backupshizzle"
#BT_METAFILE_NAME = "config.conf"
#USERID = int(-1)
#LOGFILE = os.path.join(CONFIG_PATH, 'log.log')



class MainWindow_UI(QtGui.QMainWindow):

    sizeXMin = 640
    sizeXMax = 1024
    sizeYMin = 480
    sizeYMax = 768

    def __init__(self):

        super(MainWindow_UI, self).__init__()
        
        self.initUI()

    def initUI(self):
        
        # set window properties
        self.setMinimumSize(self.sizeXMin, self.sizeYMin)
        self.setMaximumSize(self.sizeXMax, self.sizeYMax)
        self.setWindowTitle("Login - BackupShizzle")
        self.setWindowIcon(QtGui.QIcon(QtGui.QPixmap("img/favicon.png")))
        
        # menu: File: actions
        self.actionExit = QtGui.QAction(QtGui.QIcon('img/favicon.png'), '&Exit', self)
        self.actionExit.setStatusTip("Exit")
        self.actionExit.setShortcut('Ctrl+Q')
        
        self.actionLogout = QtGui.QAction(QtGui.QIcon(), '&Logout', self)
        self.actionLogout.setStatusTip("Logout")
        self.actionLogout.setShortcut('Ctrl+L')
        self.actionLogout.setEnabled(False)
        # menu: File
        self.menuFile = QtGui.QMenu("&File", self)
        self.menuFile.addAction(self.actionLogout)
        self.menuFile.addAction(self.actionExit)
        # menu: Backup: actions
        self.actionOpenBOp_Activity = QtGui.QAction(QtGui.QIcon('img/favicon.png'), '&Activity Window', self)
        self.actionOpenBOp_Activity.setStatusTip("Open Backup Activity Window")
        self.actionOpenBOp_Activity.setShortcut('Ctrl+1')
        # menu: Backup
        self.menuBackup = QtGui.QMenu("&Backup", self)
        self.menuBackup.addAction(self.actionOpenBOp_Activity)
        # menu
        self.menuBar = QtGui.QMenuBar(self)
        self.menuBar.addMenu(self.menuFile)
        self.menuBar.addMenu(self.menuBackup)
        self.setMenuBar(self.menuBar)
        # status-bar
        self.statusBar = QtGui.QStatusBar()
        self.setStatusBar(self.statusBar)



class MainWindow_CTR(MainWindow_UI):
    
    def __init__(self):
        
        super(MainWindow_CTR, self).__init__()

        # set-up config
        self.createConfig()
        
        # set-up logging
        logging.basicConfig(filename=config.LOGFILE, format='[%(asctime)s] %(levelname)s:%(filename)s:%(funcName)s:%(msg)s', level=logging.INFO)
        
        # init login UI
        self.updateCentralWidget(Login_CTR(self))

        # init job wrangler
        self.BOp_Jobs_CTR = BOp_Jobs_CTR(self)
        
        # connect signals
        self.actionExit.triggered.connect(self.close)
        self.actionLogout.triggered.connect(lambda: self.updateCentralWidget(Login_CTR(self.window())))
        self.actionOpenBOp_Activity.triggered.connect(self.BOp_Jobs_CTR.open_BOp_Activity)
        
        self.show()
        
        
    def closeEvent(self, e):
        
        # disabled for faster workflow
#        msg = self.showNotification(title = "Exit", message = "Exit Application", description = "Do you wish to exit the application?", mode = 1)
        msg = QtGui.QMessageBox.Ok
        
        
        if msg == QtGui.QMessageBox.Ok:
            
            # close Backup Activity window
            try: self.BOp_Jobs_CTR.BOp_Activity.close()
            except: pass
            
            e.accept()
        else:
            e.ignore()
        
        
    def createConfig(self):
        '''
        Creates config/config-db and sets-up the structure
        '''
        # if config path does not exist
        if not os.path.isdir(config.CONFIG_PATH):
            try:
                os.makedirs(config.CONFIG_PATH, 755)
            except:
                self.showNotification()
            
        # if db file does not exist
        if not os.path.isfile(bs.config.CONFIGDB_PATH):


            conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
            cursor = sqlite3.Cursor(conn)
            cursor.execute("CREATE TABLE `users` (username TEXT, password TEXT)")
            cursor.execute("CREATE TABLE `sources` (id TEXT, userId INTEGER, sourcePath TEXT)")
            cursor.execute("CREATE TABLE `sets` (setId INTEGER, userId INTEGER, title TEXT, sources TEXT, filters TEXT, targets TEXT)")
            cursor.execute("CREATE TABLE `filters` (id TEXT, userId INTEGER)")
            cursor.execute("CREATE TABLE `targets` (userId INTEGER, targetTitle INTEGER, targetId INTEGER)")
            conn.commit()
            cursor.close()
            conn.close()


    def showNotification(self, **kwargs):
        '''
        showNotification(title string, message string, description string, mode int)
            Opens a pop-up dialog with passed message
        '''
        try: title = kwargs["title"]
        except: title = "Insert title here"
        try: message = kwargs["message"]
        except: message = "Insert message here"
        try: description = kwargs["description"]
        except: description = "Insert description here"
            # 0: notification: shows OK button only
            # 1: confirmation: shows OK and CANCEL buttons
        try: mode = kwargs["mode"]
        except: mode = 0
        
        msgBox = QtGui.QMessageBox()
        msgBox.setIcon(QtGui.QMessageBox.Information)
        msgBox.setWindowTitle(title)
        msgBox.setText(message)
        msgBox.setInformativeText(description)
        if mode is 0:
            msgBox.setStandardButtons(msgBox.Ok)
        if mode is 1:
            msgBox.setStandardButtons(msgBox.Cancel | msgBox.Ok)
            msgBox.setDefaultButton(msgBox.Cancel)
        msgBox.open()
        msgBox.move(self.x()+(self.width()/2)-(msgBox.width()/2), self.y()+(self.height()/2)-(msgBox.height()/2))
        return msgBox.exec_()    



    def updateCentralWidget(self, widget):
        '''
        MainWindow_UI.setCentralWidget()
            Accepts a widget class that it sets as its active central widget.
        '''
        self.setCentralWidget(widget)
    
    
    
    def updateStatusBarMsg(self, msg):
        # set message
        self.statusBar.showMessage(msg, 3000)



class Login_UI(QtGui.QWidget):
    
    def __init__(self, parent):
        
        super(Login_UI, self).__init__(parent)
        
        self.parent = parent
        
        self.initUI()
        
        
    def initUI(self):
        
        # GL1
        self.GL1 = QtGui.QGridLayout(self)

        # GL1.GL1
        self.GL1.WG1 = QtGui.QWidget(self)
        self.GL1.WG1.setMaximumSize(300, 200)
        self.GL1.addWidget(self.GL1.WG1)
        
        self.GL1.WG1.GL1 = QtGui.QGridLayout(self.GL1.WG1)
        self.GL1.WG1.GL1.setSpacing(10)

        self.GL1.WG1.GL1.usernameLabel = QtGui.QLabel("Username: ")
        self.GL1.WG1.GL1.addWidget(self.GL1.WG1.GL1.usernameLabel, 0, 0, 1, 2)
        self.GL1.WG1.GL1.usernameInput = QtGui.QLineEdit()
        self.GL1.WG1.GL1.addWidget(self.GL1.WG1.GL1.usernameInput, 0, 2, 1, 8)
        
        
        self.GL1.WG1.GL1.passwordLabel = QtGui.QLabel("Password: ")
        self.GL1.WG1.GL1.addWidget(self.GL1.WG1.GL1.passwordLabel, 1, 0, 1, 2)
        self.GL1.WG1.GL1.passwordInput = QtGui.QLineEdit()
        self.GL1.WG1.GL1.passwordInput.setEchoMode(2)
        self.GL1.WG1.GL1.addWidget(self.GL1.WG1.GL1.passwordInput, 1, 2, 1, 8)
        
        self.GL1.WG1.GL1.submitBtn = QtGui.QPushButton("Login")
        self.GL1.WG1.GL1.addWidget(self.GL1.WG1.GL1.submitBtn, 2, 0, 1, 5)
        self.GL1.WG1.GL1.submitBtn.clicked.connect(self.validateCredentials)
        self.GL1.WG1.GL1.exitBtn = QtGui.QPushButton("Exit")
        self.GL1.WG1.GL1.addWidget(self.GL1.WG1.GL1.exitBtn, 2, 5, 1, 5)
        self.GL1.WG1.GL1.exitBtn.clicked.connect(self.parent.close)
        self.GL1.WG1.GL1.userManagementBtn = QtGui.QPushButton("User Management")
        self.GL1.WG1.GL1.addWidget(self.GL1.WG1.GL1.userManagementBtn, 3, 0, 1, 10)
        self.GL1.WG1.GL1.userManagementBtn.clicked.connect(self.openAccountManagementWindow)
            
            
            
class Login_CTR(Login_UI):
    
    def __init__(self, parent):
        
        super(Login_CTR, self).__init__(parent)
        
        self.parent = parent
        
        # check if user account(s) exist and open Accounts_CTR if False
        if self.userAccountExists() == False:
            self.openAccountManagementWindow()
            
            
    def keyPressEvent(self, e):

        if e.key() == QtCore.Qt.Key_Enter or e.key() == QtCore.Qt.Key_Return:
            self.validateCredentials()
        
    
    def openAccountManagementWindow(self):
        
        self.accountManagementWindow = Accounts_CTR()
        self.accountManagementWindow.exec_()
       
        
    def userAccountExists(self):
        '''
        Checks if at least one user exists in the DB.
        '''
        
        conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
        cursor = sqlite3.Cursor(conn)
        res = cursor.execute("SELECT * FROM `users`").fetchall()
        cursor.close()
        conn.close()
        
        if len(res) >= 1:
            return True
        else:
            return False
        

    def validateCredentials(self):
        
#        global USERID
        
        username = self.GL1.WG1.GL1.usernameInput.text()
        password = self.GL1.WG1.GL1.passwordInput.text()
        passwordHash = hashlib.sha512()
        passwordHash.update(str(password))
        passwordHash = passwordHash.hexdigest()
        
        conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
        cursor = sqlite3.Cursor(conn)
        res = cursor.execute("SELECT `rowid`, * FROM `users` WHERE `username` = ? AND `password` = ?", (str(username), str(passwordHash), )).fetchone()
        
        if res != None:
            config.USERID = res[0]
            self.parent.updateCentralWidget(BBase_CTR(self.parent))
        else:
            self.parent.showNotification(title = "Login Error", message = "Invalid credentials", description = "The username/password combination you entered is invalid. Please try again.")
        
        



class Accounts_UI(QtGui.QDialog):
    
    def __init__(self):
        
        super(Accounts_UI, self).__init__()
        
        self.initUI()
        
    def initUI(self):
        
        pass
    
    
    
class Accounts_CTR(Accounts_UI):
    
    def __init__(self):
        
        super(Accounts_CTR, self).__init__()
        
        self.KILLME_createDefaultAccounts()
        
        
    def KILLME_createDefaultAccounts(self):
        '''
        Create default accounts for testing purposes
        '''
        conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
        cursor = sqlite3.Cursor(conn)
        cursor.execute("INSERT INTO `users` (`username`, `password`) VALUES ('1', '4dff4ea340f0a823f15d3f4f01ab62eae0e5da579ccb851f8db9dfe84c58b2b37b89903a740e1ee172da793a6e79d560e5f7f9bd058a12a280433ed6fa46510a')")
        cursor.execute("INSERT INTO `users` (`username`, `password`) VALUES ('2', '40b244112641dd78dd4f93b6c9190dd46e0099194d5a44257b7efad6ef9ff4683da1eda0244448cb343aa688f5d3efd7314dafe580ac0bcbf115aeca9e8dc114')")
        conn.commit()
        cursor.close()
        conn.close()
    

class BBase_UI(QtGui.QWidget):
    
    def __init__(self, parent):
        
        super(BBase_UI, self).__init__()
        
        self.parent = parent
        
        self.initUI()
    
    def initUI(self):

        self.TW1 = QtGui.QTabWidget()
        
        self.TW1.tabSources = Sources_Tab_CTR()
        self.TW1.addTab(self.TW1.tabSources, "Sou&rces")
        
        self.TW1.tabTargets = Targets_Tab_CTR()
        self.TW1.addTab(self.TW1.tabTargets, "Tar&gets")
        
        self.TW1.tabFilters = Filters_Tab_CTR()
        self.TW1.addTab(self.TW1.tabFilters, "F&ilters")
        
        self.TW1.tabBackupSets = Sets_Tab_CTR()
        self.TW1.addTab(self.TW1.tabBackupSets, "Backup &Sets")
        
        self.HL1 = QtGui.QHBoxLayout(self)
        self.HL1.addWidget(self.TW1)
        
        
        
class BBase_CTR(BBase_UI):
    
    def __init__(self, parent):
        
        super(BBase_CTR, self).__init__(parent)

        self.parent = parent
        
        # set-up menu
        self.parent.actionLogout.setDisabled(0)
        



class Filters_Tab_UI(QtGui.QWidget):
    
    def __init__(self):
        
        super(Filters_Tab_UI, self).__init__()



class Filters_Tab_CTR(Filters_Tab_UI):
    
    def __init__(self):
        
        super(Filters_Tab_CTR, self).__init__()
        
        
        
class Filters_Manip_UI(QtGui.QDialog):
    
    def __init__(self):
        
        super(Filters_Manip_UI, self).__init__()
        
        self.initUI()
        
    
    def initUI(self):
        
        pass



class Sets_Tab_UI(QtGui.QWidget):
    
    @property
    def _dbData(self):
        pass
    @_dbData.getter
    def _dbData(self):
        conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
        cursor = sqlite3.Cursor(conn)
        data = cursor.execute("SELECT * FROM `sets` WHERE `userId` = ?", (config.USERID,)).fetchall()
        cursor.close()
        conn.close()
        return data
        
    
    def __init__(self):
        
        super(Sets_Tab_UI, self).__init__()
        
        self.initUI()
        
    def initUI(self):
        
        self.GL1 = QtGui.QGridLayout(self)
        
        # list
        self.TW1 = QtGui.QTreeWidget()
        self.TW1.setHeaderLabels(("Name", "ID"))
        self.TW1.setRootIsDecorated(False)
        self.GL1.addWidget(self.TW1, 1, 0, 1, 1)
        
        # top bar
        self.TB1 = QtGui.QToolBar("setsToolBar")
        
        self.TB1.addBackupSet = QtGui.QAction(QtGui.QIcon("img/icons_add.png"), "Add Backup-Set", self)
        self.TB1.addBackupSet.triggered.connect(self.addBackupSet)
        self.TB1.addAction(self.TB1.addBackupSet)
        
        self.TB1.editBackupSet = QtGui.QAction(QtGui.QIcon("img/icons_edit.png"), "Edit Backup-Set", self)
        self.TB1.editBackupSet.triggered.connect(self.editBackupSet)
        self.TB1.addAction(self.TB1.editBackupSet)
        
        self.TB1.forgetBackupSet = QtGui.QAction(QtGui.QIcon("img/icons_forget.png"), "Forget Backup-Set", self)
        self.TB1.forgetBackupSet.triggered.connect(self.forgetBackupSet)
        self.TB1.addAction(self.TB1.forgetBackupSet)
        
        self.TB1.reloadList = QtGui.QAction(QtGui.QIcon("img/icons_refresh.png"), "Refresh", self)
        self.TB1.reloadList.triggered.connect(self.refreshList)
        self.TB1.addAction(self.TB1.reloadList)
        
        self.TB1.runBackup = QtGui.QAction(QtGui.QIcon("img/icons_run.png"), "Run Backup", self)
        self.TB1.runBackup.triggered.connect(self.submitJobToPrep)
        self.TB1.addAction(self.TB1.runBackup)
        
        self.GL1.addWidget(self.TB1, 0, 0, 1, 1)
        
        self.refreshList()
        
        
        
    def addBackupSet(self):
        
        self.winAddBS = Sets_Manip_UI(self, "new")
        self.winAddBS.acceptBtnTitle = "&Add"
        
        # process return data
        if self.winAddBS.exec_():
            setId, setTitle, setSources, setFilters, setTargets = self.winAddBS.returnData()
            
#            # commit new data to db
            conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
            cursor = sqlite3.Cursor(conn)
            res = cursor.execute("INSERT INTO `sets` (`title`, `sources`, `filters`, `targets`, `setId`, `userId`) VALUES (?, ?, ?, ?, ?, ?)", (setTitle, setSources, setFilters, setTargets, setId, config.USERID))
            conn.commit()
            cursor.close()
            conn.close()
            # reload sets list
            self.refreshList()
    
    
            
    def editBackupSet(self):

        # only if SOMETHING is selected
        if self.TW1.currentItem() != None:
            setId = int(self.TW1.currentItem().text(1))
            
            self.winAddBS = Sets_Manip_UI(self, setId)
            self.winAddBS.acceptBtnTitle = "&OK"
            
            # process return data
            if self.winAddBS.exec_():
                setId, setTitle, setSources, setFilters, setTargets = self.winAddBS.returnData()
                
                # commit new data to db
                conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
                cursor = sqlite3.Cursor(conn)
                res = cursor.execute("UPDATE `sets` SET `title` = ?, `sources` = ?, `filters` = ?, `targets` = ? WHERE `setId` = ? AND `userId` = ?", (setTitle, setSources, setFilters, setTargets, setId, config.USERID))
                conn.commit()
                cursor.close()
                conn.close()
                # reload sets list
                self.refreshList()
        else:
            self.window().updateStatusBarMsg("Please select a Backup Set to edit.")
    
    
    
    def forgetBackupSet(self):

        # only if SOMETHING is selected
        if self.TW1.currentItem() != None:
            setId = int(self.TW1.currentItem().text(1))
            
            msg = self.window().showNotification(title = "Confirm", message = "Confirm forget", description = "Forgetting this Backup-Set will forget all settings and configurations made. The actual backup-data on Targets will not be deleted.", mode = 1)
            if msg == QtGui.QMessageBox.Ok:
                # delete data set from db
                conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
                cursor = sqlite3.Cursor(conn)
                res = cursor.execute("DELETE FROM `sets` WHERE `setId` = ? AND `userId` = ?", (int(setId), int(config.USERID)))
                conn.commit()
                cursor.close()
                conn.close()
                
                self.refreshList()
            if msg == QtGui.QMessageBox.Cancel:
                pass
        else:
            self.window().updateStatusBarMsg("Please select a Backup Set to forget.")
            
    
    
    def refreshList(self):
        '''
        Re-Reads DB data into list widget
        '''
        # clear list first
        self.TW1.clear()
        for setId, userId, title, sources, filters, targets in self._dbData:
            item = QtGui.QTreeWidgetItem()
            item.setText(0, title)
            item.setText(1, unicode(setId))
            self.TW1.addTopLevelItem(item)
            
        # resize columns
        self.TW1.resizeColumnToContents(0)
        self.TW1.resizeColumnToContents(1)
        self.TW1.resizeColumnToContents(2)



class Sets_Tab_CTR(Sets_Tab_UI):
    
    def __init__(self):
        
        super(Sets_Tab_CTR, self).__init__()
            
            
            
    def submitJobToPrep(self):
        
        # only if SOMETHING is selected
        if self.TW1.currentItem() != None:
            setId = int(self.TW1.currentItem().text(1))
            # submit job to wrangler
#            self.window().BOp_Jobs_CTR.submitJobToPrep(setId, 3)
            # launch activity
            self.window().BOp_Jobs_CTR.open_BOp_Prep(setId)
        else:
            self.window().updateStatusBarMsg("Please select a Backup Set to run.")
        
    
            
            
            
class Sets_Manip_UI(QtGui.QDialog):
    
    _setId = -1
    _setTitle = ""
    # all available data in db
    _dbSourcesData = []
    _dbFiltersData = []
    _dbTargetsData = []
    
    # all currently set data for current set in db
    _setSources = []
    _setFilters = []
    _setTargets = []
    
    # all currently available data
    _availSources = []
    _availFilters = []
    _availTargets = []

    def __init__(self, parent, setId):
        
        super(Sets_Manip_UI, self).__init__()
        
        self.parent = parent
        
        conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
        cursor = sqlite3.Cursor(conn)
        
        # if setId == "new", create a new empty data set
        res = 0
        if setId == "new":
            setId = int(time.time())
            res = ["", "", "New Backup Set", "[]", "[]", "[]"]
        else:
            # get existing BS data from DB
            res = cursor.execute("SELECT * FROM `sets` WHERE `setId` = ? AND `userId` = ?", (setId, config.USERID)).fetchone()
        self._setId = setId
        self._setTitle = res[2]
        
        self._setFilters = json.loads(res[4])
        
        self._dbSourcesData = cursor.execute("SELECT * FROM `sources` WHERE `userId` = ? ORDER BY `sourcePath` ASC", (config.USERID,)).fetchall()
        self._dbFiltersData = cursor.execute("SELECT * FROM `filters` WHERE `userId` = ?", (config.USERID,)).fetchall()
        self._dbTargetsData = cursor.execute("SELECT * FROM `targets` WHERE `userId` = ? ORDER BY `targetTitle`", (config.USERID,)).fetchall()

        # build arrays
        self._setSources = []
        self._availSources = []
        for item in self._dbSourcesData:
            if item[0] in json.loads(res[3]):
                self._setSources.append(item)
            else:
                self._availSources.append(item)
            
        
#        self._availFilters = 
        self._setTargets = []
        self._availTargets = []
        for item in self._dbTargetsData:
            if item[2] in json.loads(res[5]):
                self._setTargets.append(item)
            else:
                self._availTargets.append(item)
        
        
        cursor.close()
        conn.close()
        
        self.initUI()
        
    @property
    def acceptBtnTitle(self):
        pass
    @acceptBtnTitle.setter
    def acceptBtnTitle(self, title):
        self.btnBox.acceptBtn.setText(title)
        
    def initUI(self):
        
        
        # setTitle
        self.HGL = QtGui.QGridLayout()
        self.HGL.HTitleLabel = QtGui.QLabel("Name")
        self.HGL.addWidget(self.HGL.HTitleLabel, 0, 0, 1, 1)
        self.HGL.HTitle = QtGui.QLineEdit()
        self.HGL.HTitle.setMaxLength(20)
        # validate input data
        self.HGL.HTitle.textChanged.connect(self.validateTitleData)
        self.HGL.addWidget(self.HGL.HTitle, 0, 1, 1, 1)
        self.HGL.HTitleSub = QtGui.QLabel()
        self.HGL.addWidget(self.HGL.HTitleSub, 1, 1, 1, 1)
        
        
        # sources GL
        self.SGL = QtGui.QGridLayout()
        # sources title
        self.SGL.STitle = QtGui.QLabel("Backup Sources")
        self.SGL.addWidget(self.SGL.STitle, 0, 0, 1, 2)   
        # sources list
        self.SGL.SList = QtGui.QListWidget()
        self.SGL.addWidget(self.SGL.SList, 1, 0, 1, 2)
        # sources combo box
        self.SGL.SComboBox = QtGui.QComboBox()
        self.SGL.addWidget(self.SGL.SComboBox, 2, 0, 1, 2)
        # add button
        self.SGL.SAddBtn = QtGui.QPushButton("&Add")
        self.SGL.SAddBtn.clicked.connect(self.addSource)
        self.SGL.addWidget(self.SGL.SAddBtn, 3, 0, 1, 1)
        # remove button
        self.SGL.SRemoveBtn = QtGui.QPushButton("&Remove")
        self.SGL.SRemoveBtn.clicked.connect(self.removeSource)
        self.SGL.addWidget(self.SGL.SRemoveBtn, 3, 1, 1, 1)
        
        # filters GL
        self.FGL = QtGui.QGridLayout()
        # filters title
        self.FGL.FTitle = QtGui.QLabel("Backup Source Filters")
        self.FGL.FTitle.setMaximumHeight(13)
        self.FGL.addWidget(self.FGL.FTitle, 0, 0, 1, 2) 
        # filters list
        self.FGL.FList = QtGui.QListWidget()
        self.FGL.addWidget(self.FGL.FList, 1, 0, 1, 2)
        # sources combo box
        self.FGL.FComboBox = QtGui.QComboBox()
        self.FGL.addWidget(self.FGL.FComboBox, 2, 0, 1, 2)
        # add button
        self.FGL.FAddBtn = QtGui.QPushButton("&Add")
        self.FGL.FAddBtn.clicked.connect(self.addFilter)
        self.FGL.addWidget(self.FGL.FAddBtn, 3, 0, 1, 1)
        # forget button
        self.FGL.FForgetBtn = QtGui.QPushButton("&Forget")
        self.FGL.FForgetBtn.clicked.connect(self.removeTarget)
        self.FGL.addWidget(self.FGL.FForgetBtn, 3, 1, 1, 1)
#        
        # preview stage
        self.PSGL = QtGui.QGridLayout()
        # title
        self.PSGL.PTitle = QtGui.QLabel("Preview Stage")
        self.PSGL.PTitle.setMaximumHeight(13)
        self.PSGL.addWidget(self.PSGL.PTitle, 0, 0, 1, 1) 
        # frame
        self.PSGL.frame = QtGui.QFrame()
        self.PSGL.frame.setStyleSheet("border: 1px solid grey")
        self.PSGL.addWidget(self.PSGL.frame, 1, 0, 1, 1)
        # placeholder
        self.PSGL.placeholder = QtGui.QLabel("")
        self.PSGL.addWidget(self.PSGL.placeholder, 1, 0, 1, 1)
#        
        # targets GL
        self.TGL = QtGui.QGridLayout()
        # targets title
        self.TGL.targetsTitle = QtGui.QLabel("Backup Targets")
        self.TGL.addWidget(self.TGL.targetsTitle, 0, 0, 1, 1)
        # targets list
        self.TGL.TList = QtGui.QListWidget()
        self.TGL.addWidget(self.TGL.TList, 1, 0, 1, 2)
        # targets combo box
        self.TGL.TComboBox = QtGui.QComboBox()
        self.TGL.addWidget(self.TGL.TComboBox, 2, 0, 1, 2)
        # add button
        self.TGL.addBtn = QtGui.QPushButton("&Add")
        self.TGL.addBtn.clicked.connect(self.addTarget)
        self.TGL.addWidget(self.TGL.addBtn, 3, 0, 1, 1)
        # remove button
        self.TGL.removeBtn = QtGui.QPushButton("&Remove")
        self.TGL.removeBtn.clicked.connect(self.removeTarget)
        self.TGL.addWidget(self.TGL.removeBtn, 3, 1, 1, 1)
        
        # dialog buttons
        self.btnBox = QtGui.QDialogButtonBox()
        
        self.btnBox.acceptBtn = QtGui.QPushButton()
        self.btnBox.addButton(self.btnBox.acceptBtn, self.btnBox.AcceptRole)
        self.btnBox.accepted.connect(self.accept)
#        self.btnBox.acceptBtn.setEnabled(False)
        
        self.btnBox.rejectBtn = QtGui.QPushButton("&Cancel")
        self.btnBox.addButton(self.btnBox.rejectBtn, self.btnBox.RejectRole)
        self.btnBox.rejected.connect(self.reject)

        self.GL1 = QtGui.QGridLayout(self)
        self.GL1.addLayout(self.HGL, 0, 0, 1, 4)
        self.GL1.addLayout(self.SGL, 1, 0, 1, 1)
        self.GL1.addLayout(self.FGL, 1, 1, 1, 1)
        self.GL1.addLayout(self.PSGL, 1, 2, 1, 1)
        self.GL1.addLayout(self.TGL, 1, 3, 1, 1)
        self.GL1.addWidget(self.btnBox, 5, 0, 1, 4)
        
        # get data
        self.HGL.HTitle.setText(self._setTitle)
        self.loadAvailableSources()
        self.loadActiveSources()
        self.loadAvailableTargets()
        self.loadActiveTargets()
        self.loadAvailableFilters()
        self.loadActiveFilters()
        
        
    @property
    def currentSetSourcesData(self):
        pass
    @currentSetSourcesData.getter
    def currentSetSourcesData(self):
        conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
        cursor = sqlite3.Cursor(conn)
        res = cursor.execute("SELECT `sources` FROM `sets` WHERE `setId` = ?", (self._setId,)).fetchone()[0]
        res = json.loads(res)
        cursor.close()
        conn.close()
        return res
        
        
    def loadAvailableSources(self):
        '''
        Loads all sources into the QComboBox that are available to be used in BS (essentially <all> - <already active>).
        '''
        # clear combobox
        self.SGL.SComboBox.clear()
        for sourceId, userId, sourcePath in self._availSources:
            self.SGL.SComboBox.addItem(sourcePath)
    
    
    def loadActiveSources(self):
        '''
        Loads all active (previously added to BS) sources into list.
        '''
        # clear list
        self.SGL.SList.clear()
        self.SGL.SList.addItems([x[2] for x in self._setSources])
                
                
    def addSource(self):
        '''
        Adds a source from the available list to the active
        '''
        index = self.SGL.SComboBox.currentIndex()
        if len(self._availSources) > 0: # if a source is selected
            # add to set sources
            self._setSources.append(self._availSources[index])
            # remove from avail
            self._availSources.pop(index)
            # re-sort items
            self._setSources.sort()
            self._availSources.sort()
            # reload list, combobox
            self.loadAvailableSources()
            self.loadActiveSources()
            

            
    def removeSource(self):
        '''
        Removes a source from the active and adds it back to the available list
        '''
        index = self.SGL.SList.currentRow()
        # if a source is selected
        if len(self._setSources) > 0:
            # add to avail sources
            self._availSources.append(self._setSources[index])
            # remove from set sources
            self._setSources.pop(index)
            # re-sort items
            self._setSources.sort()
            self._availSources.sort()
            # reload list, combobox
            self.loadAvailableSources()
            self.loadActiveSources()
            
            
            
    def loadAvailableFilters(self):
        pass
    
    
    
    def loadActiveFilters(self):
        pass
    
    
    
    def addFilter(self):
        pass
    
    
    
    def removeFilter(self):
        pass
    
    
    
    def loadAvailableTargets(self):
        '''
        Loads all targets into the QComboBox that are available to be used in BS (essentially <all> - <already active>).
        '''
        # clear combobox
        self.TGL.TComboBox.clear()
        for userId, targetTitle, targetId in self._availTargets:
            self.TGL.TComboBox.addItem(targetTitle)
    
    
    
    def loadActiveTargets(self):
        '''
        Loads all active (previously added to BS) targets into list.
        '''
        # clear list
        self.TGL.TList.clear()
        self.TGL.TList.addItems([x[1] for x in self._setTargets])
    
    
    
    def addTarget(self):
        '''
        Adds a target from the available list to the active
        '''
        index = self.TGL.TComboBox.currentIndex()
        if len(self._availTargets) > 0: # if a target is selected
            # add to set Targets
            self._setTargets.append(self._availTargets[index])
            # remove from avail
            self._availTargets.pop(index)
            # re-sort items
            self._setTargets.sort()
            self._availTargets.sort()
            # reload list, combobox
            self.loadAvailableTargets()
            self.loadActiveTargets()
    
    
    
    def removeTarget(self):
        '''
        Removes a target from the active and adds it back to the available list
        '''
        index = self.TGL.TList.currentRow()
        # if a target is selected
        if len(self._setTargets) > 0:
            # add to avail targets
            self._availTargets.append(self._setTargets[index])
            # remove from set targets
            self._setTargets.pop(index)
            # re-sort items
            self._setTargets.sort()
            self._availTargets.sort()
            # reload list, combobox
            self.loadAvailableTargets()
            self.loadActiveTargets()
    
    
    
    

            
            
    def validateTitleData(self):
        '''
        Validates the data for the title QLineEdit in the "Add Backup  Target" dialog
        and outputs warning if invalid key was entered/undoes last entered (invalid) character.
        '''
        
        pattern = "^([a-zA-Z]+)([a-zA-Z0-9\_\-]*)$"
        text = self.HGL.HTitle.text()
        match = re.match(pattern, text)
        
        try:
            if match.group(0):
                self.HGL.HTitleSub.setText("")
                self.HGL.HTitle.setStyleSheet("background: white")
                self.btnBox.acceptBtn.setEnabled(True)
                # update class var with new text
                self._setTitle = text
        except:
            self.HGL.HTitleSub.setText("Please use Latin/numeric characters only with a leading non-numeric character.")
            self.HGL.HTitle.setStyleSheet("background: grey")
            self.btnBox.acceptBtn.setEnabled(False)
            
        # check for titles already existing in DB
#        for userId, targetTitle, targetSerialNumber in self._dbData:
#            
#            if unicode(self.titleQLE.text()) == targetTitle:
#                
#                self.titleSubQLE.setText("Name already exists. Please choose a different one.")
#                self.titleQLE.setStyleSheet("background: grey")
#                self.btnBox.acceptBtn.setEnabled(False)
            

            
    def returnData(self):
        '''
        Returns specific data entered in this dialog.
        '''
        setId = int(self._setId)
        title = unicode(self._setTitle)
        setSources = json.dumps([x[0] for x in self._setSources])
        setFilters = json.dumps(self._setFilters)
        setTargets = json.dumps([x[2] for x in self._setTargets])
        
        return(setId, title, setSources, setFilters, setTargets)



class Sources_Tab_UI(QtGui.QWidget):
    
    def __init__(self):
        
        super(Sources_Tab_UI, self).__init__()
        self.initUI()
        self.folderIcon = QtGui.QIcon
        
    def initUI(self):
        
        self.GL1 = QtGui.QGridLayout(self)
        
        self.TB1 = QtGui.QToolBar("sourcesToolBar")
        
        self.TB1.addSource = QtGui.QAction(QtGui.QIcon("img/icons_add.png"), "Add Source", self)
        self.TB1.addSource.triggered.connect(self.addSourceOpenBrowser)
        self.TB1.addAction(self.TB1.addSource)
        
        self.TB1.forgetSource = QtGui.QAction(QtGui.QIcon("img/icons_forget.png"), "Forget Source", self)
        self.TB1.forgetSource.triggered.connect(self.forgetSource)
        self.TB1.addAction(self.TB1.forgetSource)
        
        self.TB1.rescanSource = QtGui.QAction(QtGui.QIcon("img/icons_refresh.png"), "Refresh", self)
        self.TB1.rescanSource.triggered.connect(self.rescanSources)
        self.TB1.addAction(self.TB1.rescanSource)
        
        self.GL1.addWidget(self.TB1, 0, 0, 1, 3)
        
        self.TW1 = QtGui.QTreeWidget()
        self.TW1.setHeaderLabels(("Path", "Status",))
#        self.TW1.itemClicked.connect(self.test)
        self.TW1.setSortingEnabled(1)
        self.TW1.sortItems(0, QtCore.Qt.AscendingOrder)
        
#        self.TW1.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
#        self.TW1.customContextMenuRequested.connect(self.test)

        # open db connection
        self.conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
        self.cursor = sqlite3.Cursor(self.conn)
        
        self.rescanSources()
        self.GL1.addWidget(self.TW1, 1, 0, 2, 3)
        
        
    # ABSTRACT 
    # addSourceOpenBrowser
        # self.addSource( returnPath )
    # addSource
        # folder browser
        # verify that not duplicate
        # add to db
        # rescanSources()
    # forgetSource
        # only subpaths and inactive drives
            # msgBox: verify deletion
            # delete from db incl all nested sources
            # rescanSources()
    # rescanSources
        # flush treeWidget
        # add drives
            # add to db if !exists
        # add db entries
            # if !exist: mark disabled
            
    
    # addSourceOpenBrowser
    def addSourceOpenBrowser(self):
        
        # folder browser
        sourceBrowser = QtGui.QFileDialog()
        returnPath = str(sourceBrowser.getExistingDirectory( self, "Open Source Path", "C:\\" ))

        if not returnPath == "":

            self.addSource( returnPath )
    
    
    
    # addSource
    def addSource(self, sourcePath):
        
        # verify that not duplicate
        if self.cursor.execute("SELECT `rowid` FROM `sources` WHERE `id` = ? AND `userId` = ?", ( sourcePath.encode('base64', 'strict')[0:-1], config.USERID )).fetchall() == []:
            
            # add to db
            self.cursor.execute("INSERT INTO `sources` ( `id`, `userId`, `sourcePath` ) VALUES ( ?, ?, ? )", ( sourcePath.encode('base64', 'strict')[0:-1], config.USERID, unicode(sourcePath) ))
            
        # rescanSources()
        self.rescanSources()
            
            
            
    # forgetSource
    def forgetSource(self):
        
        currentItem = self.TW1.currentItem()
        # only if *something* is selected
        if not currentItem == None:
            
            currentItemText = str(currentItem.text(0))
            # if nested, look up root and append root string to currentItemText
            try:
                currentItemText = str(currentItem.parent().text(0))+currentItemText
            except:
                pass
            # only subpaths and inactive drives
            if len(currentItemText) > 3 or not os.path.isdir(currentItemText):
                
                # msgBox: verify deletion
                msg = self.window().showNotification(title = "Confirm", message = "Confirm forget", description = "Forgetting this Backup-Set will forget all settings and configurations made. The actual backup-data on Targets will not be deleted.", mode = 1)
                if msg == QtGui.QMessageBox.Ok:
                    # delete from db
                    # select all from current user
                    self.cursor.execute("DELETE FROM `sources` WHERE `id` = ? AND `userId` = ?", (currentItemText.encode('base64', 'strict')[0:-1], config.USERID))
                else:
                    pass
                # rescan
                self.rescanSources()
        else:
            self.window().updateStatusBarMsg("Please select a Backup Source to forget.")
            
            
            
    # rescanSources
    def rescanSources(self):

        # flush treeWidget
        self.TW1.clear()
        # add drives
        for drivePath in nsOs.getDrives():

            # add to db if !exists
            if (self.cursor.execute("SELECT `sourcePath` FROM `sources` WHERE `id` = ? AND `userId` = ?", ( drivePath.encode('base64', 'strict')[0:-1], config.USERID )).fetchall() == []):
                self.cursor.execute("INSERT INTO `sources` ( `id`, `userId`, `sourcePath` ) VALUES ( ?, ?, ? )", ( drivePath.encode('base64', 'strict')[0:-1], config.USERID, drivePath ))
        self.conn.commit()
        # add db entries
        for sourcePath in self.cursor.execute("SELECT `sourcePath` FROM `sources` WHERE `userId` = ? ORDER BY `sourcePath` ASC", (config.USERID,)).fetchall():

            sourcePath = sourcePath[0]
            if len(sourcePath) == 3:
                
                currentItem = QtGui.QTreeWidgetItem((sourcePath,))
                self.TW1.addTopLevelItem(currentItem)
                
                # if !exist: mark disabled
                if not os.path.isdir(sourcePath):
                    
                    currentItem.setTextColor(0, QtGui.QColor(150, 150, 150, 255))
                    currentItem.setTextColor(1, QtGui.QColor(150, 150, 150, 255))
                    currentItem.setText(1, "<Source currently unavailable>")
                    
            else:
                
                sourcePathRootOnly = sourcePath[0:3]
                sourcePathNoRoot = sourcePath[3:len(sourcePath)]
                currentItem = QtGui.QTreeWidgetItem((sourcePathNoRoot,))
                parentItem = self.TW1.findItems( sourcePathRootOnly, QtCore.Qt.MatchExactly )[0]
                parentItem.addChild(currentItem)
                # if !exists: mark disabled
                if not os.path.isdir(sourcePath):
                    
                    currentItem.setTextColor(0, QtGui.QColor(150, 150, 150, 255))
                    currentItem.setTextColor(1, QtGui.QColor(150, 150, 150, 255))
                    currentItem.setText(1, "<Source currently unavailable>")
                    
                # expand
                self.TW1.expandAll()
                self.TW1.resizeColumnToContents(0)



class Sources_Tab_CTR(Sources_Tab_UI):
    
    def __init__(self):
        
        super(Sources_Tab_CTR, self).__init__()
        


class Targets_Tab_UI(QtGui.QWidget):
    
    def __init__(self):
        
        super(Targets_Tab_UI, self).__init__()
        self.initUI()
        
    def initUI(self):
        
        self.GL1 = QtGui.QGridLayout(self)
        
        self.TB1 = QtGui.QToolBar("targetsToolBar")
        
        self.TB1.addTarget = QtGui.QAction(QtGui.QIcon("img/icons_add.png"), "Add Target", self)
        self.TB1.addTarget.triggered.connect(self.addBT)
        self.TB1.addAction(self.TB1.addTarget)
        
        self.TB1.editTarget = QtGui.QAction(QtGui.QIcon("img/icons_edit.png"), "Edit Target", self)
        self.TB1.editTarget.triggered.connect(self.editBT)
        self.TB1.addAction(self.TB1.editTarget)
        
        self.TB1.forgetTarget = QtGui.QAction(QtGui.QIcon("img/icons_forget.png"), "Forget Target", self)
        self.TB1.forgetTarget.triggered.connect(self.forgetBT)
        self.TB1.addAction(self.TB1.forgetTarget)
        
        self.TB1.refreshList = QtGui.QAction(QtGui.QIcon("img/icons_refresh.png"), "Refresh", self)
        self.TB1.refreshList.triggered.connect(self.refreshList)
        self.TB1.addAction(self.TB1.refreshList)
        
        self.GL1.addWidget(self.TB1, 0, 0, 1, 3)
        
        self.TW1 = QtGui.QTreeWidget()
        self.TW1.setHeaderLabels(("Name", "Drive Letter", "ID"))
        self.TW1.setSortingEnabled(1)
        self.TW1.setRootIsDecorated(False)
        self.TW1.sortItems(0, QtCore.Qt.AscendingOrder)
        
        self.GL1.addWidget(self.TW1, 1, 0, 2, 3)
        
        # refresh data in list
        self.refreshList()
        
        
    def addBT(self):
        '''
        Opens a dialog to add a new Backup Target to the set
        '''
        # open add-target dialog
        self.winAddTarget = Targets_Manip_UI(self)
        # set-up window
        self.winAddTarget.setWindowTitle("Add Backup Target")
        self.winAddTarget.acceptBtnTitle = "&Add"
        self.winAddTarget.setDrivesInList(drivesFilter = "free")
        # process return data
        if self.winAddTarget.exec_():
            # gather data
            newTargetTitle, newTargetDriveLetter = self.winAddTarget.returnData()
            # generate arbitrary ID based on timestamp
            newTargetId = int(time.time())
            # initialize new drive + commit data to db
            # create backup base dir+meta file
            if not os.path.isdir(os.path.join(newTargetDriveLetter, config.BT_BASEDIR_PATH)):
                try: # set-up data in FS
                    os.mkdir(os.path.join(newTargetDriveLetter, config.BT_BASEDIR_PATH))
                    try: # set-up data in DB
                        # create config file
                        f = open(os.path.join(newTargetDriveLetter, config.BT_BASEDIR_PATH, config.BT_METAFILE_NAME), "w")
                        jsonData = {"id": newTargetId}
                        json.dump(jsonData, f)
                        f.close()
                        # add to db
                        conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
                        cursor = conn.cursor()
                        res = cursor.execute("INSERT INTO `targets` (`userId`, `targetId`, `targetTitle`) VALUES (?, ?, ?)", (config.USERID, newTargetId, newTargetTitle))
                        conn.commit()
                        cursor.close()
                        conn.close()
                    except:
                        self.window().showNotification(title = "Database Failure", message = "Database access failed.", description = "An error has occurred when accessing the database. Please make sure you have sufficient write permissions to the config file and folder ("+unicode(bs.config.CONFIGDB_PATH)+") and try again.")
                except:
                    self.window().showNotification(title = "Access Failure", message = "Permission denied.", description = "An access error occurred when setting-up the Backup-Target. Please make sure you have appropriate access-permissions on this volume and try again.")
            else:
                self.window().showNotification(title = "Integrity Failure", message = "Previous data found.", description = "Previous backup-data has been found on this volume. It has to be restored before re-integrating it as a backup-target. Please run a recovery check and try again.")
            
        # refresh data in list
        self.refreshList()
        
    def forgetBT(self):
        
        currentItem = self.TW1.currentItem()
        # only if SOMETHING is selected
        if not currentItem == None:
            targetTitle = currentItem.text(0)
            targetId = currentItem.text(2)
            
            msg = self.window().showNotification(title = "Confirm", message = "Confirm forget", description = "Forgetting this Backup-Target will forget all associations to it within backupshizzle. Data on associated volume(s) will NOT be deleted. However, if you wish to access the backup-data again at a later point you will have to re-integrate/restore the volume into the system.", mode = 1)
            if msg == QtGui.QMessageBox.Ok:
                # delete data set from db
                conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
                cursor = sqlite3.Cursor(conn)
                res = cursor.execute("DELETE FROM `targets` WHERE `targetId` = ? AND `userId` = ? AND `targetTitle` = ?", (int(targetId), int(config.USERID), unicode(targetTitle)))
                conn.commit()
                cursor.close()
                conn.close()
                
                self.refreshList()
            if msg == QtGui.QMessageBox.Cancel:
                pass
        else:
            self.window().updateStatusBarMsg("Please select a Backup Target to forget.")
        
            
    def editBT(self):
        
        currentItem = self.TW1.currentItem()
        # only if SOMETHING is selected
        if not currentItem == None:
            if currentItem.text(1) in nsOs.getDrives(): # making sure BT is currently available
                oldTargetTitle = currentItem.text(0)
                # instantiate window
                self.winEditTarget = Targets_Manip_UI(self)
                # set-up window
                self.winEditTarget.setWindowTitle("Edit Backup Target")
                self.winEditTarget.acceptBtnTitle = "&Edit"
                self.winEditTarget.setDrivesInList()
                self.winEditTarget.BTTitle = currentItem.text(0)
                self.winEditTarget.BTDriveLetter = nsOs.getDrives().index(currentItem.text(1))
                self.winEditTarget.driveSelectionDisabled = True
            
                if self.winEditTarget.exec_():
                    # get new data
                    newTargetTitle, newTargetDriveLetter = self.winEditTarget.returnData()
                    # update data in db
                    conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
                    cursor = sqlite3.Cursor(conn)
                    res = cursor.execute("UPDATE `targets` SET `targetTitle` = ? WHERE `userId` = ? AND `targetTitle` = ?", (unicode(newTargetTitle), unicode(config.USERID), unicode(oldTargetTitle)))
                    conn.commit()
                    conn.close()
                    # refresh list
                    self.refreshList()
        else:
            self.window().updateStatusBarMsg("Please select a Backup Target to edit.")
    
        
        
    def refreshList(self):
        
        conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
        cursor = conn.cursor()
        # clear list
        self.TW1.clear()
        # db: get data
        res = cursor.execute("SELECT * FROM `targets`")
        
        # run through all targets in db
        for userId, targetTitle, targetId in res:
            # run through all available drives matching them (targetId) to data sets in db
            disabledFlag = True
            targetDriveLetter = ""
            for driveLetter in nsOs.getDrives():
                # if drive has backupshizzle config file
                if os.path.isfile(os.path.join(driveLetter, config.BT_BASEDIR_PATH, config.BT_METAFILE_NAME)):
                    # match id on drive (config.conf) to id in db
                    f = open(os.path.join(driveLetter, config.BT_BASEDIR_PATH, config.BT_METAFILE_NAME))
                    jsonData = json.get(f)
                    f.close()
                    if (int(jsonData["id"]) == targetId):
                        targetDriveLetter = driveLetter
                        disabledFlag = False
                        break
                
            if targetDriveLetter == "":
                targetDriveLetter = "<Backup-Target currently unavailable>"      
                disabledFlag = False          
            # if data set has different userId
            if userId != config.USERID:
                # set disabled, mask title
                disabledFlag = True
                targetTitle = "<In use by a different user-account>"
                
                    
            
            item = QtGui.QTreeWidgetItem()
            item.setText(0, QtCore.QString(unicode(targetTitle)))
            item.setText(1, QtCore.QString(targetDriveLetter))
            item.setText(2, unicode(targetId))
            if disabledFlag == True: item.setDisabled(True)
            
            self.TW1.addTopLevelItem(item)
        self.TW1.resizeColumnToContents(0)
        self.TW1.resizeColumnToContents(1)
        self.TW1.resizeColumnToContents(2)



class Targets_Tab_CTR(Targets_Tab_UI):
    
    def __init__(self):
        
        super(Targets_Tab_CTR, self).__init__()
        


class Targets_Manip_UI(QtGui.QDialog):
    
    _dbData = []
    
    def __init__(self, parent):
        
        super(Targets_Manip_UI, self).__init__()
        
        self.parent = parent
        
        # get existing dbData
        conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
        cursor = sqlite3.Cursor(conn)
        self._dbData = cursor.execute("SELECT * FROM `targets` WHERE `userId` = ?", (config.USERID,)).fetchall()
        cursor.close()
        
        self.initUI()
        
    @property
    def driveSelectionDisabled(self):
        self.driveSelectionQCB.setDisabled()
    @driveSelectionDisabled.setter
    def driveSelectionDisabled(self, data):
        self.driveSelectionQCB.setDisabled(data)
        self.driveSelectionTitleStr.setDisabled(data)
        
        
    @property
    def acceptBtnTitle(self):
        self.btnBox.acceptBtn.text()
    @acceptBtnTitle.setter
    def acceptBtnTitle(self, data):
        self.btnBox.acceptBtn.setText(data)
        
    @property
    def BTTitle(self):
        pass
    @BTTitle.setter
    def BTTitle(self, data):
        self.titleQLE.setText(data)
        
    @property
    def BTDriveLetter(self):
        pass
    @BTDriveLetter.setter
    def BTDriveLetter(self, data):
        '''
        Sets the item in the combo box to the passed drive letter in data
        '''
        self.driveSelectionQCB.setCurrentIndex(data)



    def initUI(self):
        
        # layout
        self.GL1 = QtGui.QGridLayout(self)
        
        # title: label
        self.titleStr = QtGui.QLabel("Name")
        self.GL1.addWidget(self.titleStr, 0, 0, 1, 1)
        # title: QLineEdit
        self.titleQLE = QtGui.QLineEdit()
        self.titleQLE.setMinimumWidth(380)
        self.titleQLE.setMaxLength(20)
        self.titleQLE.textChanged.connect(self.validateData)
        self.GL1.addWidget(self.titleQLE, 0, 1, 1, 2)
        # titleSubtitle: QLabel (displays warning for invalid keys entered etc.)
        self.titleSubQLE = QtGui.QLabel()
        self.titleSubQLE.setStyleSheet("color: #F00")
        self.GL1.addWidget(self.titleSubQLE, 1, 1, 1, 2)
        
        # dropdown: driveSelection
        self.driveSelectionTitleStr = QtGui.QLabel()
        self.driveSelectionTitleStr.setText("Drive:")
        self.GL1.addWidget(self.driveSelectionTitleStr, 2, 0, 1, 1)
        self.driveSelectionQCB = QtGui.QComboBox()
        self.GL1.addWidget(self.driveSelectionQCB, 2, 1, 1, 2)
        
        # buttons: Add, Cancel
        #self.btnBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Close | QtGui.QDialogButtonBox.Save)
        self.btnBox = QtGui.QDialogButtonBox()
        
        self.btnBox.acceptBtn = QtGui.QPushButton()
        self.btnBox.addButton(self.btnBox.acceptBtn, self.btnBox.AcceptRole)
        self.btnBox.accepted.connect(self.accept)
        self.btnBox.acceptBtn.setEnabled(False)
        
        self.btnBox.rejectBtn = QtGui.QPushButton("&Cancel")
        self.btnBox.addButton(self.btnBox.rejectBtn, self.btnBox.RejectRole)
        self.btnBox.rejected.connect(self.reject)
        
        self.GL1.addWidget(self.btnBox, 3, 1, 1, 2)
        
        # center window
        self.setMinimumSize(450, 130)
        self.setMaximumSize(450, 130)
        
        offsetX = self.parent.window().x() + self.parent.window().width()/2 - self.width()/2
        offsetY = self.parent.window().y() + self.parent.window().height()/2 - self.height()/2
        self.move(offsetX, offsetY)
        


    def setDrivesInList(self, **kwargs):
        
        try: drivesFilter = kwargs["drivesFilter"]
        except: drivesFilter = ""
        
        self.driveSelectionQCB.clear()
        # all available
        driveLetters = nsOs.getDrives()
        
        driveLettersNew = []
        if drivesFilter == "free": # display all *free* drives
            for driveLetter in driveLetters:
                if not os.path.isdir(os.path.join(driveLetter, config.BT_BASEDIR_PATH)):
                    driveLettersNew.append(driveLetter)
        else: # display all *available* drives
            driveLettersNew = driveLetters
        self.driveSelectionQCB.addItems(driveLettersNew)
        
        # set focus
        
        #set enabled/disabled
        
        
        
    def validateData(self):
        '''
        Validates the data for the title QLineEdit in the "Add Backup  Target" dialog
        and outputs warning if invalid key was entered/undoes last entered (invalid) character.
        '''
        
        pattern = "^([a-zA-Z]+)([a-zA-Z0-9\_\-]*)$"
        text = self.titleQLE.text()
        match = re.match(pattern, text)
        
        try:
            if match.group(0):
                self.titleSubQLE.setText("")
                self.titleQLE.setStyleSheet("background: white")
                self.btnBox.acceptBtn.setEnabled(True)
        except:
            self.titleSubQLE.setText("Please use Latin/numeric characters only with a leading non-numeric character.")
            self.titleQLE.setStyleSheet("background: grey")
            self.btnBox.acceptBtn.setEnabled(False)
            
        # check for titles already existing in DB
        for userId, targetTitle, targetSerialNumber in self._dbData:
            
            if unicode(self.titleQLE.text()) == targetTitle:
                
                self.titleSubQLE.setText("Name already exists. Please choose a different one.")
                self.titleQLE.setStyleSheet("background: grey")
                self.btnBox.acceptBtn.setEnabled(False)
                
        
        
    def returnData(self):
        
        title = unicode(str(self.titleQLE.text()))
        drive = unicode(str(self.driveSelectionQCB.currentText()))
        return(title, drive)
        


class WinBackupExecManager(QtGui.QDialog):
    
    _setId = -1
    _dbSetData = []
    
    def __init__(self, setId):
        
        super(WinBackupExecManager, self).__init__()
        
        self._setId = setId
        
        # get set data
        conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
        cursor = sqlite3.Cursor(conn)
        self._dbSetData = cursor.execute("SELECT * FROM `sets` WHERE `setId` = ? AND `userId` = ?", (self._setId, config.USERID)).fetchone()
        cursor.close()
        conn.close()
        
        # launch UI
        self.initUI()
        
    
    def initUI(self):
        
        # set title
        title = "Backup - "+str(self._dbSetData[2])+" ("+str(self._setId)+")"
        self.setWindowTitle(title)



def main():
    app = QtGui.QApplication(sys.argv)
    ex = MainWindow_CTR()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()