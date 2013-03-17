# -*- coding: utf-8 -*-
'''
Created on 29/05/2012

@author: Bossi
'''

import os, win32api

def getDrives():
    '''
    getDrives()
        Returns a list with all drive letters available on the current system in the form of "C:\\"
    '''
    drives = ["B:\\","C:\\","D:\\","E:\\","F:\\","G:\\","H:\\","I:\\","J:\\","K:\\","L:\\","M:\\","N:\\","O:\\","P:\\","Q:\\","R:\\","S:\\","T:\\","U:\\","V:\\","W:\\","X:\\","Y:\\","Z:\\"]
    drivesAvailable = []
    
    for drive in drives:
        if os.path.isdir(drive):
            drivesAvailable.append(drive)
            
    return drivesAvailable


def getDrivesData():
    '''
    Returns a 2-D list with data of all drives in the current system:
    [
        [volumeLabel, volumeSerialNumber, maximumComponentLengthOfAFilename, sysFlags-otherFlagsSpcificToTheFileSystem, fileSystemName, driveLetter],
        ...
    ]
    source: [http://docs.activestate.com/activepython/2.5/pywin32/win32api__GetVolumeInformation_meth.html]
    '''
    drivesData = []
    for driveLetter in getDrives():
        driveData = win32api.GetVolumeInformation(driveLetter)
        driveDataNew = []
        driveDataNew.append(driveData[0])
        driveDataNew.append(driveData[1])
        driveDataNew.append(driveData[2])
        driveDataNew.append(driveData[3])
        driveDataNew.append(driveData[4])
        driveDataNew.append(driveLetter)
        drivesData.append(driveDataNew)
    
    return(drivesData)