# -*- encoding: utf-8 -*-

import os, zipfile, hashlib

zipFilePath = os.path.realpath("Y:/My Documents/Bossi/Desktop/test/test.zip")
targetFolderPath = os.path.realpath('Y:/My Documents/Bossi/Desktop/test/target')
folderToAdd = os.path.realpath("C:/Program Files (x86)/Valve/Half-Life 2/hl1")




def packIndividually():    
    for baseDir, folders, files in os.walk(folderToAdd):
        for file in files:
            m = hashlib.sha512()
            m.update(os.path.join(baseDir, file))
            print m.hexdigest()
            
            with zipfile.ZipFile(os.path.join(targetFolderPath, m.hexdigest()), "a", zipfile.ZIP_DEFLATED) as myzip:
                myzip.write(os.path.join(baseDir, file))
                
def packIntoOne():
    with zipfile.ZipFile(os.path.join(zipFilePath), "a", zipfile.ZIP_DEFLATED) as myzip:
        for baseDir, folders, files in os.walk(folderToAdd):
            for file in files:
                filePath = os.path.join(baseDir, file)
                myzip.write(filePath)
                
packIndividually()
#packIntoOne()