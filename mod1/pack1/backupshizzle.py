# -*- coding: utf-8 -*-
'''
Created on 28/04/2012

@author: Bossi
'''
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

#try:
#    pass
#except Exception, e:
#    print e