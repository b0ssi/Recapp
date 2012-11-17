# -*- coding: utf-8 -*-
'''
Created on 28/04/2012

@author: Bossi
'''

import sqlite3, os, re, hashlib, shutil, datetime, time, sys, logging, nsOs, json, random
from PyQt4 import QtGui, QtCore

try:
    import win32file, win32api
except:
    pass
        
print sys.version
# current error code: EC0003
# set up logging
# create config dir
CONFIG_PATH = os.path.normcase(os.path.join(str(QtCore.QDir.homePath()), ".backupshizzle"))

LOGFILE_PATH = os.path.join(CONFIG_PATH, "log.log")
CONFIGDB_PATH = os.path.join(CONFIG_PATH, "globalConfig.sqlite")
BT_BASEDIR_PATH = "backupshizzle"
BT_METAFILE_NAME = "config.conf"
USERID = int(999)
INSTANCES = {}
LOGFILE = os.path.join(CONFIG_PATH, 'log.log')

if not os.path.isdir(CONFIG_PATH):
    os.makedirs(CONFIG_PATH, 755)
logging.basicConfig(filename=LOGFILE, format='[%(asctime)s] %(levelname)s:%(filename)s:%(funcName)s:%(msg)s', level=logging.INFO)


"""
class backupSet(object):
    '''
    backupSet
        Manages the backup process
    '''
    _name = ""
    _dbPath = ""
    _sourcePaths = []
    _sourceDirectoryPaths = []
    _sourceFilePaths = []
    _targetPaths = []
    _hashAlg = "sha512"
    _maxFilePathLength = 255
    _exactMTimeMatch = 0
    _currentTimestamp = ""

    def __init__(self, name):
        '''
        Constructor
        '''
        # set class vars
        self.name = name
        self._dbPath = os.path.join(os.path.dirname(os.path.abspath(__file__)),"db", name+".sqlite")
        
        # initialize object
        if os.path.isfile(self.dbPath):
            self.initializeExistingDb()
        else:
            self.initializeNewDb()
            
        # update currentDateTime
        self.updateCurrentTimestamp()
        
        # initialize objects
        INSTANCES[self.name+"_fsData"] = fsData(self.sourcePaths, self.dbPath)
        INSTANCES[self.name+"_dbFiles"] = dbFiles(self.dbPath)
            
        # LAST INIT CALLS
        self.updateDb()

    @property
    def name(self):
        '''
        backupSet.name
            Returns the object's name.
        '''
        return(self._name)
    
    @name.setter
    def name(self, name):
        '''
        backupSet.name
            Sets the object's name.
        '''
        if re.match(r"[a-zA-Z][a-zA-Z0-9\\_\\-\\(\\)]*", name):
            self._name = name
            return 1
        else:
            print("Error: Please use standard characters for the name only.")
            return 0
    
    @property
    def dbPath(self):
        '''
        backupSet.dbPath
            Returns the absolute path for the database on the current system.
        '''
        return(self._dbPath)
    
    @property
    def hashAlg(self):
        return self._hashAlg
        
    def initializeExistingDb(self):
        '''
        backupSet.initializeExistingDb()
            Opens database in 'db/<self._name>.sqlite' and populates object with its backup set data.
        '''
        
        try:
            conn = sqlite3.connect(self.dbPath)
            cursor = conn.cursor()
            # update name, sourcePaths
            cursor.execute("SELECT * FROM `config` WHERE `rowid`=1")
            self.name, self.sourcePaths, self.targetPaths = cursor.fetchone()
            
            conn.close()
        except:
            print("Could not connect to database.")
        
    def initializeNewDb(self):
        '''
        backupSet.initializeNewDb()
            Creates a new database for a new backup set (object) incl. structure, but no data except the name
        '''
        #conn = sqlite3.connect("")
        conn = sqlite3.connect(self.dbPath)
        cursor = conn.cursor()
        
        cursor.execute("CREATE TABLE `config` (name text, sourcePaths text, targetPaths text)")
        cursor.execute("INSERT INTO `config` VALUES ('', '', '')")
        
#        cursor.execute("CREATE TABLE `source` ()")
        
        cursor.execute("CREATE TABLE `directories` (path text, mtime float)")
        
        cursor.execute("CREATE TABLE `files` (path text, hash text, hashAlgorithm text, mtime float, fileSize int, presentIn text, newIn text)")
        
        cursor.execute("CREATE TABLE `filesFailed` (path text)")
        
        conn.commit()
        conn.close()
        
    def updateDb(self):
        '''
        backupSet.updateDb()
            Writes current object classVars to the database
        '''
        conn = sqlite3.connect(self.dbPath)
        cursor = conn.cursor()
        # update into table `config`
        t = (self.name, self.listToSemicolonSeparatedString(self.sourcePaths), self.listToSemicolonSeparatedString(self.targetPaths))
        cursor.execute("UPDATE `config` SET `name`=?, `sourcePaths`=?, `targetPaths`=? WHERE `rowid`=1", t)
        # update into table `files`
        for item in INSTANCES[self.name+"_fsData"].filesUnchangedData:
            #!!! check, if item already exists in db, otherwise insert
            pass
        # update into table `directories`
        for item in INSTANCES[self.name+"_fsData"].filesUnchangedData:
            #!!! check, if item already exists in db, otherwise insert
            pass

        conn.commit()
        conn.close()
        
    @property
    def sourcePaths(self):
        '''
        backupSet.sourcePaths
            Returns all source directories defined for the backup set as a list.
            This computed property will also check all current source directories if they are valid paths on the current system and strip out any that are not.
        '''
        return self._sourcePaths
    
    @sourcePaths.setter
    def sourcePaths(self, sourcePaths):
        '''
        backupSet.sourcePaths
            Sets the list of sources (must be directories on the current system) for the backup set. Accepts a semicolon separated string.
            Warning: This will override any existing source directories.
        '''
        sourcePaths = sourcePaths.split(";")
        # check, that all paths in list are valid paths on the current system
        
        for item in sourcePaths:
            item = os.path.normpath(item)
            if os.path.isdir(item):
                self._sourcePaths.append(item)
            else:
                if not item == "":
                    print("Warning: '"+item+"' was found as a source in the backup set but is not a valid directory on this system. This item has been permanently removed from the backup set.")
    
    def addSourcePath(self, path):
        '''
        backupSet.addSourcePath(path)
            Adds a given path 'path' to the class directory _sourcePaths[].
            'path' must be a valid directory on the system or it will be rejected.
            Back-slashes have to be masked or simply be typed as forward-slashes.
        '''
        path = os.path.normpath(path)
        # check, if path is a valid path on the system
        if os.path.isdir(path):
            # check, if path already in self.sourcePath
            if self.find(path, self.sourcePaths) == []:
                self._sourcePaths.append(path)
                self.updateDb()
                return 1
            else:
                return 0
        else:
            return 0
        
    @property
    def targetPaths(self):
        '''
        backupSet.targetPaths
            Returns all target paths set in self._targetPaths as a list
        '''
        return self._targetPaths
    
    @targetPaths.setter
    def targetPaths(self, targetPaths):
        '''
        backupSet.targetPaths
            Sets the list of targets (must be directories on the current system) for the backup set. Accepts a semicolon separated string.
            Warning: This will override any existing source directories.
        '''
        targetPaths = targetPaths.split(";")
        # check, that all paths in list are valid paths on the current system
        
        for item in targetPaths:
            item = os.path.normpath(item)
            if os.path.isdir(item):
                self._targetPaths.append(item)
            else:
                if not item == "":
                    print("Warning: '"+item+"' was found as a target in the backup set but is not a valid directory on this system. This item has been permanently removed from the backup set. Note: Possibly existing backup files on the system have not been deleted.")

    def addTargetPath(self, path):
        '''
        backupSet.addTargetPath(path)
            Adds a given path 'path' to the class directory _targetPaths[].
            'path' must be a valid directory on the system or it will be rejected.
            Back-slashes have to be masked or simply be typed as forward-slashes.
        '''
        path = os.path.normpath(path)
        # check, if path is a valid path on the system
        if os.path.isdir(path):
            # check, if path already in self.sourcePath
            if self.find(path, self.targetPaths) == []:
                self._targetPaths.append(path)
                self.updateDb()
                return 1
            else:
                return 0
        else:
            return 0
        
    @property
    def currentTimestamp(self):
        return self._currentTimestamp
    
    def updateCurrentTimestamp(self):
        self._currentTimestamp = int(time.time())
        
        
    def formatTimestamp(self):
        timezone = time.timezone/60/60*(-1)
        if timezone>=0:
            timezone = "+"+str(timezone)
        timezone = "(GMT"+timezone+")"
        
        currentDateTime = datetime.datetime.now()
        return str(datetime.datetime.fromtimestamp(self._currentTimestamp).strftime("%Y-%m-%d - %H-%M-%S ")+timezone)
    
        
    def doBackup(self):
        '''
        backupSet.doBackup()
            Executes a backup.
        '''
        conn = sqlite3.connect(self.dbPath)
        cursor = conn.cursor()
        
        # create subdir with timestamp
        self.createCurrentBackupSubdir()
        
        bytesTotal = INSTANCES[self.name+"_fsData"]._filesNewBytes
        if bytesTotal == 0:
            bytesTotal = 1
        bytesCompleted = 0
        percent = 0.0

        # hard-link unchanged data
        print("Creating hard-links for "+str(len(INSTANCES[self.name+"_fsData"].filesUnchangedData))+" files, where possible...")
        for item in INSTANCES[self.name+"_fsData"].filesUnchangedData:
            # prepare data
            currentFilePath = item[0]
            currentFilePathBase, currentFilePathExt =   os.path.splitext(item[0])
            # grab previous data from DB
            previousPresentIn = cursor.execute("SELECT `presentIn` FROM `files` WHERE `path`=?", (currentFilePath,)).fetchone()
            if previousPresentIn == None:
                previousPresentIn = ("",)
            currentPresentIn = previousPresentIn[0]+";"+str(self.currentTimestamp)
            
            # add data to db
            cursor.execute("UPDATE `files` SET `presentIn`=? WHERE `path`=?", (currentPresentIn,currentFilePath,))
            conn.commit()
            # hard-link files
            self.hardlinkFilesToTargets(currentFilePath)
            print currentFilePath+" present"

        print("\nCopying new data...")
        # copy new data
        for item in INSTANCES[self.name+"_fsData"].filesNewData:
            # prepare data
            currentFilePath =   item[0]
            currentHashString = self.doHashFile(currentFilePath, self.hashAlg)
            currentMDate =      item[1]
            bytesCurrent = item[2]
            # grab previous data from DB
            previousNewIn = cursor.execute("SELECT `newIn` FROM `files` WHERE `path`=?", (currentFilePath,)).fetchone()
            if previousNewIn == None:
                previousNewIn = ("",)
            currentNewIn = previousNewIn[0]+";"+str(self.currentTimestamp)
            
            previousPresentIn = cursor.execute("SELECT `presentIn` FROM `files` WHERE `path`=?", (currentFilePath,)).fetchone()
            if previousPresentIn == None:
                previousPresentIn = ("",)
            currentPresentIn = previousPresentIn[0]+";"+str(self.currentTimestamp)
            
            # check if item already exists in db
            if cursor.execute("SELECT `rowid` FROM `files` WHERE `path`=?", (currentFilePath,)).fetchone() == None:
                # add item to DB
                cursor.execute("INSERT INTO `files` VALUES(?,?,?,?,?,?,?)", (currentFilePath, currentHashString, self.hashAlg, currentMDate, bytesCurrent, currentNewIn, currentNewIn))
            else:
                # add to current entry
                cursor.execute("UPDATE `files` SET `presentIn`=?, `newIn`=?, mtime=? WHERE `path`=?", (currentPresentIn, currentNewIn, currentMDate, currentFilePath,))

            conn.commit()
            # add item to fsData obj _filesUnchanged
            INSTANCES[self.name+"_fsData"].filesUnchangedData.append(item)
            # copy item to targets
            self.copyFileToTargets(currentFilePath, currentHashString)
            # report on progress
            bytesCompleted += bytesCurrent
            percent = round(float(bytesCompleted)*100/float(bytesTotal),2)
            print(str(self.doFormatFileSizeUnit(bytesCompleted)[0])+" "+self.doFormatFileSizeUnit(bytesCurrent)[1]+" / "+str(self.doFormatFileSizeUnit(bytesTotal)[0])+" "+self.doFormatFileSizeUnit(bytesTotal)[1])
            print(str(percent)+"%")
            print currentFilePath+" new"
        # delete item from fsData obj _filesNew
        INSTANCES[self.name+"_fsData"].filesNewData = []
        # deal with directories accordingly...
        # copy copy of db to targets
        print("\nBackup complete.")

        conn.close()
        
        return 1
        
    def updateSourceFiles(self):
        '''
        backupSet.updateSourceFiles()
            Recursively reads all file paths in directories that have corresponding entries in self._sourcePaths and:
                - calculates a hash
                - saves the file path
            of each item (file) to the database.
        '''
        # connect to db
        conn = sqlite3.connect(self.dbPath)
        cursor = conn.cursor()
        # gather backup data
        filesBytes = self.countFilesBytesToUpdate(self.sourcePaths)
        totalFileCount = filesBytes[0]
        currentFileCount = 1
        totalBytes = filesBytes[1]
        currentBytes = 0
        
        # update dateTime
        self.updateCurrentDateTime()
        
        # run through sources and write file-, directory-paths to DB
        for root in self.sourcePaths:
            for directory in os.walk(unicode(root)):
                currentDirPath = directory[0]
                currentDirMtime = os.path.getmtime(currentDirPath)
                
                # check, if entry already exists
                cursor.execute("SELECT `rowid` FROM `directories` WHERE `path`=?", (currentDirPath,))
                if not cursor.fetchone():
                    self._sourceDirectoryPaths.append(currentDirPath)
                    cursor.execute("INSERT INTO `directories` VALUES (?,?)", (currentDirPath, currentDirMtime,))
                for currentFileName in directory[2]:
                    currentFilePath = os.path.join(currentDirPath,currentFileName)
                                                   
                    # check, if entry already exists
                    cursor.execute("SELECT `rowid` FROM `files` WHERE `path`=?", (currentFilePath,))
                    if not cursor.fetchone():
                        # Make sure we don't try to touch files with paths that are too long for the tools (hashutil, getsize, etc.) to handle
                        if not len(currentFilePath) > self._maxFilePathLength:
                            currentBytes += os.path.getsize(currentFilePath)
                            print("Hashing: "+currentFilePath)
                            print(str(currentFileCount)+"/"+str(totalFileCount)+"  |  "+str(self.doFormatFileSizeUnit(currentBytes)[0])+" "+str(self.doFormatFileSizeUnit(currentBytes)[1])+"/"+str(self.doFormatFileSizeUnit(totalBytes)[0])+" "+str(self.doFormatFileSizeUnit(totalBytes)[1]))
                            # get hash
                            hashString = self.doHashFile(currentFilePath, "sha512")
                            # get mtime
                            mTime = float(os.path.getmtime(currentFilePath))
                            # copyFile
                            self.copyFileToTargets(currentFilePath, hashString)
                            
                            t2 = (currentFilePath,hashString,"sha512",mTime,)
                            # add to self._sourceFilePaths
                            self._sourceFilePaths.append(t2)
                            # add to database
                            cursor.execute("INSERT INTO `files` VALUES (?,?,?,?)", t2)
                            conn.commit()
                            # output progress
                            percentageDone = int(round((float(currentBytes)/float(totalBytes))*100))
                            bar = "["
                            for n in range(percentageDone):
                                bar += "="
                            bar += "|"
                            for n in range(100-percentageDone):
                                bar += "="
                            bar += "] "+str(percentageDone)+"%"
                            print(bar)

                            currentFileCount += 1
                        else:
                            # add to database
                            cursor.execute("SELECT rowid FROM `filesFailed` WHERE `path`=?", (currentFilePath,))
                            if not cursor.fetchone():
                                cursor.execute("INSERT INTO `filesFailed` VALUES (?)", (currentFilePath,))
        
        # Print warning
        cursor.execute("SELECT * FROM `filesFailed`")
        if cursor.fetchone():
            print("Warning: The following file paths exceed the set limit of "+str(self._maxFilePathLength)+" characters and have been excluded. Please limit their file path lengths to include them.")
            for item in cursor.execute("SELECT * FROM `filesFailed`"):
                filePath = item[0]
                print(unicode(filePath))
        conn.commit()
        conn.close()
        # commit updates to DB
        self.updateDb()
    
    def createCurrentBackupSubdir(self):
        for item in self.targetPaths:
            currentRoot = os.path.join(item, str(self.formatTimestamp()))
            if not os.path.isdir(currentRoot):
                os.makedirs(currentRoot)
            return(currentRoot)
    
    def copyFileToTargets(self, filePath, hashString):
        '''
        backupSet.copyFileToTargets(filePath, hashString)
            Copies the file 'filePath' to all backup directories in self._targetPaths, renames it to its hash string.
        '''
        for item in self.targetPaths:
            currentRoot = os.path.join(item, str(self.formatTimestamp()))
            
            fileName, fileExtension = os.path.splitext(os.path.basename(filePath))
            # calc hashed name
            hashedName = hashlib.sha512()
            hashedName.update(filePath)
            hashedName = hashedName.hexdigest()
            # copy file
            newFilePath = os.path.join(currentRoot,hashedName)+fileExtension
            shutil.copy2(filePath, newFilePath)
            # check hash again after copy and put into filesFailed table if fails
            if not self.doHashFile(newFilePath, self.hashAlg) == hashString:
                conn = sqlite3.connect(self.dbPath)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO `filesFailed` VALUES (?)", (newFilePath,))
                conn.commit()
                conn.close()
                
    def hardlinkFilesToTargets(self, filePath):
        '''
        backupSet.hardlinkFilesToTargets(string filePath)
            Creates a hard-link to source 'filePath' in the current backup folder in all backup destinations where possible (depending on filesystem), otherwise ignores
        '''
        for item in self.targetPaths:
            currentRoot = os.path.join(item, str(self.formatTimestamp()))
            
            fileName, fileExtension = os.path.splitext(os.path.basename(filePath))
            # calc hashed name
            hashedName = hashlib.sha512()
            hashedName.update(filePath)
            hashedName = hashedName.hexdigest()
            # grab last backup dir
            lastBackupDir = ""
            for lastBackupDir in os.walk(item):
                lastBackupDir = lastBackupDir[1][-2]
                break
            lastBackupDir = os.path.join(item,lastBackupDir)
            filePathLastBackup = os.path.join(lastBackupDir,hashedName)+fileExtension
            # copy file
            newFilePath = os.path.join(currentRoot,hashedName)+fileExtension
            self.createHardLink(filePathLastBackup, newFilePath)

    def listToSemicolonSeparatedString(self, args):
        '''
        backupSet.listToSemicolonSeparatedString(list)
            Returns a semicolon-separated string for the given Python list 'list'.
        '''
        string = ""
        for item in args:
            string += str(item)+";"
        # cut off trailing ";"
        string = string[0:-1]
        return string
    
    def find(self, target, source):
        '''
        backupSet.find(target, source)
            Searches for string 'target' in Python list/typle/dictionary 'source' and returns a Python list with corresponding indices of matches, where 'source' is a list, tuple or dictionary
        '''
        hits = []
        for item in source:
            if item == str(target):
                hits.append(item)
        return hits
    
    def doHashFile(self, filePath, alg):
        '''
        backupSet.doHashFile(filePath, alg)
            Calculates hash for file 'filePath' using algorithm alg.
            Any hash algorithm supported by the Python hashlib module is accepted ('md5', 'sha224', 'sha256', 'sha384', 'sha512').
        '''
        # make sure we don't check for files larger than self._maxFilePathLength in path length
        if not len(filePath)>self._maxFilePathLength:
            code = "hashlib."+alg+"()"
            hashString = eval(code)
            with open(filePath,'rb') as f: 
                for chunk in iter(lambda: f.read(128*hashString.block_size), b''): 
                    hashString.update(chunk)
            return hashString.hexdigest()

    def doFormatFileSizeUnit(self, bytesInt):
        '''
        backupSet.doFormatFileSizeUnit(int bytesInt)
            Acceppts an integer (usually a file size) and converts it into the largest possible unit, without going < 1.
            Returns a tuple (<size>, <unit>)
        '''
        units = ("byte", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB")
        convertedBytesInt = float(bytesInt)
        finalUnits = "";
        for i in range(len(units)):
            convertedBytesInt = (convertedBytesInt/1024)
            finalUnits =  units[i+1]
            if convertedBytesInt < 1024:
                break
        return (round(convertedBytesInt, 2), finalUnits)
    
    def createHardLink(self, src, dst):
        try:
            os.link(dst, src)
            return 1
        except:
            try:
                win32file.CreateHardLink(dst, src)
                return 1
            except:
                return 0


class fsData(object):
    '''
    file-data-pool for files in the source filesystem
    '''
    
    _filesUnchangedData = [] # files currently in the system, EXCL. new files [(filePath, hash, mdate, fileSize),...]
    _filesUnchangedBytes = 0
    _filesUnchangedCount = 0
    _filesNewData = [] # files new in fs, not found in db [(filePath, fileSize), ...]
    _filesNewBytes = 0
    _filesNewCount = 0
    
    def __init__(self, sourcePaths, dbPath):
        # read in file data in sourcePaths
        return None
        
    @property
    def filesNewData(self):
        return self._filesNewData
    
    @filesNewData.setter
    def filesNewData(self, data):
        self._filesNewData = data
    
    @property
    def filesUnchangedData(self):
        return self._filesUnchangedData
    
    @filesUnchangedData.setter
    def filesUnchangedData(self):
        def append(self, item):
            self._filesUnchangedData.append(item)
        
    def readFileDirData(self, sourcePaths, dbPath):
        '''
        fsData.readFileDirData(list sourcePaths, string dbPath)
            Reads in file data from the file system with support of database:
                - modification time
                - hashString (from database, if modification time has not changed compared to db mtime and the db has an entry for the corresponding file)
        '''
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()

        self._filesUnchangedData = [] # [(currentFilePath, hashString, mtimeOnFile, fileSize), ...]
        self._filesUnchangedBytes = 0
        self._filesUnchangedCount = 0
        self._filesNewData = [] # [(currentFilePath, mtimeOnFile, fileSize), ...]
        self._filesNewBytes = 0
        self._filesNewCount = 0

        for sourcePath in sourcePaths:
            for r in os.walk(unicode(sourcePath)):
                currentBasePath = r[0]
                # grab directories
                for r2 in r[1]:
                    currentDir = r2
                    currentDirPath = os.path.join(currentBasePath,currentDir)
                    #!!! grab dirs
                # grab files
                for currentFile in r[2]:
                    currentFilePath = os.path.join(currentBasePath,currentFile)
                    # grab modification time
                    mtimeOnFile = os.path.getmtime(currentFilePath)
                    # grab filesize
                    fileSize = os.path.getsize(currentFilePath)
                    # get db file data
                    hashString, mtimeOnDb = "", ""
                    for hashString, mtimeOnDb in cursor.execute("SELECT `hash`, `mtime` FROM `files` WHERE path=?", (currentFilePath,)):
                        pass
                        # push out data set to either of the two class file data dictionaries
                    if mtimeOnFile == mtimeOnDb:
                        self._filesUnchangedData.append((currentFilePath, hashString, mtimeOnFile, fileSize))
                        self._filesUnchangedBytes += fileSize
                        self._filesUnchangedCount += 1
                    else:
                        print(currentFile, mtimeOnFile, mtimeOnDb)
                        self._filesNewData.append((currentFilePath, mtimeOnFile, fileSize))
                        self._filesNewBytes += fileSize
                        self._filesNewCount += 1
        conn.close()
        
        def findAllFileVersions(self, hashString, targetDir):
            '''
            fsData.findAllFileVersions(hashString, targetDir)
                Finds all versions of a given file with the basename 'hashString'(.ext) in a given directory 'targetDir'.
                Returns a list with absolute file paths to all matches
            '''

    
class dbFiles(object):
    '''
    file-data-pool for files in the database
    '''
    
    _oldFilesPaths = [] # directory with all files that were found in the DB but not in the FS [(filePath, hashString, mtime),...]
    _fileData = []      # directories currently in the system [(filePath, hash, mdate),...]

    def __init__(self, dbPath):
        # read in file data in sourcePaths
        self.readFileData(dbPath)

    def readFileData(self, dbPath):
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()
        
        self._fileData = []
        self._oldFilesPaths = []
        
        for item in cursor.execute("SELECT * FROM `files`"):
            currentFilePath = item[0]
            currentHashString = item[1]
            currentHashAlgorithm = item[2]
            currentMtime = item[3]
            currentFileSize = item[4]
            presentIn = item[5]
            newIn = item[6]
            
            if os.path.isfile(currentFilePath):
                self._fileData.append((currentFilePath, currentHashString, currentHashAlgorithm, currentMtime, currentFileSize, presentIn, newIn))
            else:
                self._oldFilesPaths.append((currentFilePath, currentHashString, currentHashAlgorithm, currentMtime, currentFileSize, presentIn, newIn))



"""



###########
### GUI ###
###########


class MainWindow(QtGui.QMainWindow):

    sizeXMin = 0
    sizeXMax = 0
    sizeYMin = 0
    sizeYMax = 0

    def __init__(self):

        super(MainWindow, self).__init__()
        self.sizeXMin = 640
        self.sizeXMax = 1024
        self.sizeYMin = 480
        self.sizeYMax = 768
        
        self.initUI()

    def initUI(self):
        
        self.setMinimumSize(self.sizeXMin, self.sizeYMin)
        self.setMaximumSize(self.sizeXMax, self.sizeYMax)
        self.setWindowTitle("Main Window")
        # actions
        self.actionExit = QtGui.QAction(QtGui.QIcon('img/favicon.png'), '&Exit', self)
        self.actionExit.setStatusTip("Exit")
        self.actionExit.setShortcut('Ctrl+Q')
        self.actionExit.triggered.connect(self.closeWindow)
        
        self.actionLogout = QtGui.QAction(QtGui.QIcon(), '&Logout', self)
        self.actionLogout.setStatusTip("Logout")
        self.actionLogout.setShortcut('Ctrl+L')
        self.actionLogout.triggered.connect(lambda: self.updateCentralWidget("UserLoginWidget"))
        # menu: file
        self.menuFile = QtGui.QMenu("&File", self)
        self.menuFile.addAction(self.actionLogout)
        self.menuFile.addAction(self.actionExit)
        # menu bar
        self.menuBar = QtGui.QMenuBar(self)
        self.menuBar.addMenu(self.menuFile)
        self.setMenuBar(self.menuBar)
        # status bar
        self.statusBar = QtGui.QStatusBar()
        self.setStatusBar(self.statusBar)

        self.updateCentralWidget("UserLoginWidget")
        
        self.show()
        
    def updateCentralWidget(self, widgetClass):
        '''
        MainWindow.setCentralWidget()
            Accepts a widget class that it sets as its active central widget.
        '''
        if widgetClass == "UserLoginWidget":
            self.mainWidget = UserLoginWidget(self)
        elif widgetClass == "BackupOperationsWidget":
            self.mainWidget = BackupOperationsWidget(self)
        self.setCentralWidget(self.mainWidget)


    def showNotification(self, **kwargs):
        '''
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
    
    
    
    def updateStatusBarMsg(self, msg):
        # set message
        self.statusBar.showMessage(msg, 3000)
        

    def forceExit(self, msg):
        '''
        forceExit()
            Forces the application to exit, promting an error message beforehand
        '''
        QtGui.QMessageBox.question(self, 'Error', msg, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
#        if reply == QtGui.QMessageBox.Ok:
        self.close()
        
#    def openMsgWindow(self):
#        '''
#        MainWindow.openMsgBox()
#            Opens a popup alert/message window
#        '''
#        msgWindow = QtGui.QDialog()
##        msgWindow.show()
    
    def closeWindow(self):
        '''
        MainWindow.closeWindow()
            Asks for confirmation and preps/executes shutdown
        '''
        msgBox = QtGui.QMessageBox()
        msgBox.setIcon(QtGui.QMessageBox.Question)
        msgBox.setWindowTitle("Confirmation Required")
        msgBox.setText("Do you want to exit the application?")
#        msgBox.setStandardButtons(QtGui.QMessageBox.Apply | QtGui.QMessageBox.Close)

        msgBox.btnQuit = msgBox.addButton("&Exit", msgBox.AcceptRole)
        msgBox.btnQuit.clicked.connect(self.close)
        
        msgBox.btnCancel = msgBox.addButton("&Cancel", msgBox.RejectRole)
        
        msgBox.setDefaultButton(msgBox.btnCancel)
        
        msgBox.open()
        msgBox.move(self.x()+(self.width()/2-msgBox.width()/2), self.y()+(self.height()/2-msgBox.height()/2))
        msgBox.exec_()



class UserLoginWidget(QtGui.QWidget):
    
    _username = ''
    _passwordHashed = ''
    _dbPath = CONFIGDB_PATH
    
    def __init__(self, parent):
        
        super(UserLoginWidget, self).__init__()
        
        self.parent = parent
        
        # set-up menu
        self.parent.actionLogout.setDisabled(1)
        
        # if db file exists
            # check validity:pass
            # else: exit
        # else
            # attempt creation, set-up, pass


        # if db file exists
        if os.path.isfile(self._dbPath):
            # check validity:pass
            try:
                res = sqlite3.connect(self._dbPath)
                cursor = sqlite3.Cursor(res)
                
                cursor.execute("SELECT `rowid` FROM `users`")
            # else: exit
            except:
                logging.critical("EC0000: globalConfig database exists but does not contain a user table. Application has to quit quit.")
                self.parent.forceExit("EC0000: The main application database exists but seems to contain no useful data. Try deleting\n\n"+str(self._dbPath)+"\n\nmanually and try again. You will have to (re-)create your user account(s).\nApplication has to quit.")
        # if db file does NOT exist
        else:
            # attempt creation, set-up, pass
            # create dir
            if not os.path.isdir(os.path.basename(self._dbPath)):
                try:
                    os.makedirs(os.path.basename(self._dbPath), 755)
                except:
                    logging.critical("EC0001: Folder "+str(os.path.basename(self._dbPath))+" could not be created.")
                    self.parent.forceExit("EC0001: The application could not create the following folder:\n\n"+str(os.path.dirname(self._dbPath))+"\n\nPlease make sure that you have write access to this location.")
            # create db
            try:
                res = sqlite3.connect(self._dbPath)
                cursor = sqlite3.Cursor(res)
                # set-up tables
                cursor.execute("CREATE TABLE `users` (username TEXT, password TEXT)")
                cursor.execute("INSERT INTO `users` (`username`, `password`) VALUES ('1', '4dff4ea340f0a823f15d3f4f01ab62eae0e5da579ccb851f8db9dfe84c58b2b37b89903a740e1ee172da793a6e79d560e5f7f9bd058a12a280433ed6fa46510a')")
                cursor.execute("INSERT INTO `users` (`username`, `password`) VALUES ('2', '40b244112641dd78dd4f93b6c9190dd46e0099194d5a44257b7efad6ef9ff4683da1eda0244448cb343aa688f5d3efd7314dafe580ac0bcbf115aeca9e8dc114')")
                cursor.execute("CREATE TABLE `sources` (id TEXT, userId INTEGER, sourcePath TEXT)")
                cursor.execute("CREATE TABLE `sets` (setId INTEGER, userId INTEGER, title TEXT, sources TEXT, filters TEXT, targets TEXT)")
                cursor.execute("CREATE TABLE `filters` (id TEXT, userId INTEGER)")
                cursor.execute("CREATE TABLE `targets` (userId INTEGER, targetTitle INTEGER, targetId INTEGER)")
            except:
                logging.critical("EC0002: An error occurred trying to access the database.")
                self.parent.forceExit("EC0002: An error occurred trying to access the database. Application must quit.")

            # open account management to add new user
            self.openAccountManagementWindow()

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
#        
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
        self.GL1.WG1.GL1.exitBtn.clicked.connect(self.parent.closeWindow)
        self.GL1.WG1.GL1.userManagementBtn = QtGui.QPushButton("User Management")
        self.GL1.WG1.GL1.addWidget(self.GL1.WG1.GL1.userManagementBtn, 3, 0, 1, 10)
        self.GL1.WG1.GL1.userManagementBtn.clicked.connect(self.openAccountManagementWindow)
        
        
    def openAccountManagementWindow(self):
        
        self.accountManagementWindow = ManageAccountsWindow(self)
        self.accountManagementWindow.exec_()
        

    def validateCredentials(self):
        
        global USERID
        
        username = self.GL1.WG1.GL1.usernameInput.text()
        password = self.GL1.WG1.GL1.passwordInput.text()
        passwordHash = hashlib.sha512()
        passwordHash.update(str(password))
        passwordHash = passwordHash.hexdigest()
        
        conn = sqlite3.connect(self._dbPath)
        cursor = sqlite3.Cursor(conn)
        res = cursor.execute("SELECT `rowid`, * FROM `users` WHERE `username` = ? AND `password` = ?", (str(username), str(passwordHash), )).fetchone()
        
        if res != None:
            USERID = res[0]
            self.parent.updateCentralWidget("BackupOperationsWidget")
        else:
            self.window().showNotification(title = "Login Error", message = "Invalid credentials", description = "The username/password combination you entered is invalid. Please try again.")
            
            
    def keyPressEvent(self, e):

        if e.key() == QtCore.Qt.Key_Enter or e.key() == QtCore.Qt.Key_Return:
            self.validateCredentials()


class ManageAccountsWindow(QtGui.QDialog):
    
    def __init__(self, parent):
        
        super(ManageAccountsWindow, self).__init__()
        
        self.parent = parent
        
        self.initUI()
        
    def initUI(self):
        
        pass
    

class BackupOperationsWidget(QtGui.QWidget):
    
    def __init__(self, parent):
        
        super(BackupOperationsWidget, self).__init__()
        
        self.parent = parent
        
        # set-up menu
        self.parent.actionLogout.setDisabled(0)
        
        self.initUI()
    
    def initUI(self):
        
        self.mainTabWidget = MainTabWidget()
        
        self.HL1 = QtGui.QHBoxLayout(self)
        self.HL1.addWidget(self.mainTabWidget)
        
        # define target(s)
        
        # define source(s) (aka backup set(s))
        
        # schedule/execution stack
        
        # backup set maintenance section
        
        # [restore section]



class MainTabWidget(QtGui.QTabWidget):
    
    def __init__(self):
        
        super(MainTabWidget, self).__init__()
        
        self.tabSources = tabSources()
        self.addTab(self.tabSources, "Sou&rces")
        
        self.tabBackupSets = tabBackupSets()
        self.addTab(self.tabBackupSets, "Backup &Sets")
        
        self.tabTargets = tabTargets()
        self.addTab(self.tabTargets, "Tar&gets")
        
        self.tabFilters = tabFilters()
        self.addTab(self.tabFilters, "Filters")



### TAB: BACKUP SETS ###

class tabBackupSets(QtGui.QWidget):
    
    @property
    def _dbData(self):
        pass
    @_dbData.getter
    def _dbData(self):
        conn = sqlite3.connect(CONFIGDB_PATH)
        cursor = sqlite3.Cursor(conn)
        data = cursor.execute("SELECT * FROM `sets` WHERE `userId` = ?", (USERID,)).fetchall()
        cursor.close()
        conn.close()
        return data
        
    
    def __init__(self):
        
        super(tabBackupSets, self).__init__()
        
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
        self.TB1.runBackup.triggered.connect(self.runBackup)
        self.TB1.addAction(self.TB1.runBackup)
        
        self.GL1.addWidget(self.TB1, 0, 0, 1, 1)
        
        self.refreshList()
        
        
        
    def addBackupSet(self):
        
        self.winAddBS = winManipSet(self, "new")
        self.winAddBS.acceptBtnTitle = "&Add"
        
        # process return data
        if self.winAddBS.exec_():
            setId, setTitle, setSources, setFilters, setTargets = self.winAddBS.returnData()
            
#            # commit new data to db
            conn = sqlite3.connect(CONFIGDB_PATH)
            cursor = sqlite3.Cursor(conn)
            res = cursor.execute("INSERT INTO `sets` (`title`, `sources`, `filters`, `targets`, `setId`, `userId`) VALUES (?, ?, ?, ?, ?, ?)", (setTitle, setSources, setFilters, setTargets, setId, USERID))
            conn.commit()
            cursor.close()
            conn.close()
            # reload sets list
            self.refreshList()
    
    
            
    def editBackupSet(self):

        # only if SOMETHING is selected
        if self.TW1.currentItem() != None:
            setId = int(self.TW1.currentItem().text(1))
            
            self.winAddBS = winManipSet(self, setId)
            self.winAddBS.acceptBtnTitle = "&OK"
            
            # process return data
            if self.winAddBS.exec_():
                setId, setTitle, setSources, setFilters, setTargets = self.winAddBS.returnData()
                
                # commit new data to db
                conn = sqlite3.connect(CONFIGDB_PATH)
                cursor = sqlite3.Cursor(conn)
                res = cursor.execute("UPDATE `sets` SET `title` = ?, `sources` = ?, `filters` = ?, `targets` = ? WHERE `setId` = ? AND `userId` = ?", (setTitle, setSources, setFilters, setTargets, setId, USERID))
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
                conn = sqlite3.connect(CONFIGDB_PATH)
                cursor = sqlite3.Cursor(conn)
                res = cursor.execute("DELETE FROM `sets` WHERE `setId` = ? AND `userId` = ?", (int(setId), int(USERID)))
                conn.commit()
                cursor.close()
                conn.close()
                
                self.refreshList()
            if msg == QtGui.QMessageBox.Cancel:
                pass
        else:
            self.window().updateStatusBarMsg("Please select a Backup Set to forget.")
            
            
            
    def runBackup(self):
        
        # only if SOMETHING is selected
        if self.TW1.currentItem() != None:
            setId = int(self.TW1.currentItem().text(1))
            self.winRunBS = winBackupExecManager(setId)
            if self.winRunBS.exec_():
                print("Done!")
        else:
            self.window().updateStatusBarMsg("Please select a Backup Set to run.")
            
    
    
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
            
            
            
class winManipSet(QtGui.QDialog):
    
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
        
        super(winManipSet, self).__init__()
        
        self.parent = parent
        
        conn = sqlite3.connect(CONFIGDB_PATH)
        cursor = sqlite3.Cursor(conn)
        
        # if setId == "new", create a new empty data set
        res = 0
        if setId == "new":
            setId = int(time.time())
            res = ["", "", "New Backup Set", "[]", "[]", "[]"]
        else:
            # get existing BS data from DB
            res = cursor.execute("SELECT * FROM `sets` WHERE `setId` = ? AND `userId` = ?", (setId, USERID)).fetchone()
        self._setId = setId
        self._setTitle = res[2]
        
        self._setFilters = json.loads(res[4])
        
        self._dbSourcesData = cursor.execute("SELECT * FROM `sources` WHERE `userId` = ? ORDER BY `sourcePath` ASC", (USERID,)).fetchall()
        self._dbFiltersData = cursor.execute("SELECT * FROM `filters` WHERE `userId` = ?", (USERID,)).fetchall()
        self._dbTargetsData = cursor.execute("SELECT * FROM `targets` WHERE `userId` = ? ORDER BY `targetTitle`", (USERID,)).fetchall()

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
        
        # load data
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
        conn = sqlite3.connect(CONFIGDB_PATH)
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
        


class winBackupExecManager(QtGui.QDialog):
    
    _setId = -1
    _dbSetData = []
    
    def __init__(self, setId):
        
        super(winBackupExecManager, self).__init__()
        
        self._setId = setId
        
        # get set data
        conn = sqlite3.connect(CONFIGDB_PATH)
        cursor = sqlite3.Cursor(conn)
        self._dbSetData = cursor.execute("SELECT * FROM `sets` WHERE `setId` = ? AND `userId` = ?", (self._setId, USERID)).fetchone()
        cursor.close()
        conn.close()
        
        # launch UI
        self.initUI()
        
    
    def initUI(self):
        
        # set title
        title = "Backup - "+str(self._dbSetData[2])+" ("+str(self._setId)+")"
        self.setWindowTitle(title)



### TAB: SOURCES ###

class tabSources(QtGui.QWidget):
    
    def __init__(self):
        
        super(tabSources, self).__init__()
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
        self.conn = sqlite3.connect(CONFIGDB_PATH)
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
        if self.cursor.execute("SELECT `rowid` FROM `sources` WHERE `id` = ? AND `userId` = ?", ( sourcePath.encode('base64', 'strict')[0:-1], USERID )).fetchall() == []:
            
            # add to db
            self.cursor.execute("INSERT INTO `sources` ( `id`, `userId`, `sourcePath` ) VALUES ( ?, ?, ? )", ( sourcePath.encode('base64', 'strict')[0:-1], USERID, unicode(sourcePath) ))
            
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
                    self.cursor.execute("DELETE FROM `sources` WHERE `id` = ? AND `userId` = ?", (currentItemText.encode('base64', 'strict')[0:-1], USERID))
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
            if (self.cursor.execute("SELECT `sourcePath` FROM `sources` WHERE `id` = ? AND `userId` = ?", ( drivePath.encode('base64', 'strict')[0:-1], USERID )).fetchall() == []):
                self.cursor.execute("INSERT INTO `sources` ( `id`, `userId`, `sourcePath` ) VALUES ( ?, ?, ? )", ( drivePath.encode('base64', 'strict')[0:-1], USERID, drivePath ))
        self.conn.commit()
        # add db entries
        for sourcePath in self.cursor.execute("SELECT `sourcePath` FROM `sources` WHERE `userId` = ? ORDER BY `sourcePath` ASC", (USERID,)).fetchall():

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
        


### TAB: TARGETS ###

class tabTargets(QtGui.QWidget):
    
    def __init__(self):
        
        super(tabTargets, self).__init__()
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
        self.winAddTarget = winManipTarget(self)
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
            if not os.path.isdir(os.path.join(newTargetDriveLetter, BT_BASEDIR_PATH)):
                try: # set-up data in FS
                    os.mkdir(os.path.join(newTargetDriveLetter, BT_BASEDIR_PATH))
                    try: # set-up data in DB
                        # create config file
                        f = open(os.path.join(newTargetDriveLetter, BT_BASEDIR_PATH, BT_METAFILE_NAME), "w")
                        jsonData = {"id": newTargetId}
                        json.dump(jsonData, f)
                        f.close()
                        # add to db
                        conn = sqlite3.connect(CONFIGDB_PATH)
                        cursor = conn.cursor()
                        res = cursor.execute("INSERT INTO `targets` (`userId`, `targetId`, `targetTitle`) VALUES (?, ?, ?)", (USERID, newTargetId, newTargetTitle))
                        conn.commit()
                        cursor.close()
                        conn.close()
                    except:
                        self.window().showNotification(title = "Database Failure", message = "Database access failed.", description = "An error has occurred when accessing the database. Please make sure you have sufficient write permissions to the config file and folder ("+unicode(CONFIGDB_PATH)+") and try again.")
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
                conn = sqlite3.connect(CONFIGDB_PATH)
                cursor = sqlite3.Cursor(conn)
                res = cursor.execute("DELETE FROM `targets` WHERE `targetId` = ? AND `userId` = ? AND `targetTitle` = ?", (int(targetId), int(USERID), unicode(targetTitle)))
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
                self.winEditTarget = winManipTarget(self)
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
                    conn = sqlite3.connect(CONFIGDB_PATH)
                    cursor = sqlite3.Cursor(conn)
                    res = cursor.execute("UPDATE `targets` SET `targetTitle` = ? WHERE `userId` = ? AND `targetTitle` = ?", (unicode(newTargetTitle), unicode(USERID), unicode(oldTargetTitle)))
                    conn.commit()
                    conn.close()
                    # refresh list
                    self.refreshList()
        else:
            self.window().updateStatusBarMsg("Please select a Backup Target to edit.")
    
        
        
    def refreshList(self):
        
        conn = sqlite3.connect(CONFIGDB_PATH)
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
                if os.path.isfile(os.path.join(driveLetter, BT_BASEDIR_PATH, BT_METAFILE_NAME)):
                    # match id on drive (config.conf) to id in db
                    f = open(os.path.join(driveLetter, BT_BASEDIR_PATH, BT_METAFILE_NAME))
                    jsonData = json.load(f)
                    f.close()
                    if (int(jsonData["id"]) == targetId):
                        targetDriveLetter = driveLetter
                        disabledFlag = False
                        break
                
            if targetDriveLetter == "":
                targetDriveLetter = "<Backup-Target currently unavailable>"      
                disabledFlag = False          
            # if data set has different userId
            if userId != USERID:
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
        

class winManipTarget(QtGui.QDialog):
    
    _dbData = []
    
    def __init__(self, parent):
        
        super(winManipTarget, self).__init__()
        
        self.parent = parent
        
        # get existing dbData
        conn = sqlite3.connect(CONFIGDB_PATH)
        cursor = sqlite3.Cursor(conn)
        self._dbData = cursor.execute("SELECT * FROM `targets` WHERE `userId` = ?", (USERID,)).fetchall()
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
                if not os.path.isdir(os.path.join(driveLetter, BT_BASEDIR_PATH)):
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



class tabFilters(QtGui.QWidget):
    
    def __init__(self):
        
        super(tabFilters, self).__init__()


def main():
    app = QtGui.QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()
    


#####################
## HELPER FUNCTIONS #
#####################
def fcReplCharInStr(standIn, string, index):
    
    stringNew = ""
    i = 0
    for char in string:
        if i == index: char = standIn
        stringNew += char
        i += 1
    return stringNew

## set-up
#myBackupSet.addSourcePath("X:\\sandbox\\source")
#myBackupSet.addTargetPath("X:\\sandbox\\target")
## update data from source
#INSTANCES["backupSet0001FB1_fsData"].readFileDirData(myBackupSet.sourcePaths, myBackupSet.dbPath)
## run
#myBackupSet.doBackup()


# instantiate
#myBackupSet = backupSet("backupSet0001FB1")
#x.sort(key=lambda tup: tup[2][2] )
#o = [z[2][0] for z in x]