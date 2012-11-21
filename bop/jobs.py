'''
Created on 19/11/2012

@author: frieder.czeschla

These classes accept jobs submitted by certain modules and manage them on request of others (such as the queue, execution, report, precheck etc.)
They also centrally link the job-data up to the dbs.
Designed to start at application runtime initiation and stop at application exit (system-wide, not restricted to user-sessions).
'''
from PyQt4 import QtCore
from bop.activity import BOp_Activity_CTR


class BOp_Jobs_CTR(QtCore.QObject):
    
    _jobs = []
    BOp_update = QtCore.pyqtSignal(int, int)
    
    def __init__(self, parent):
        
        self.parent = parent
        
        super(BOp_Jobs_CTR, self).__init__()
        
        
    def open_BOp_Activity(self):
        '''
        Opens the Backup Operations Activity window.
        '''
        # close if already open
        try:
            if self.BOp_Activity.isHidden() == True:
                self.BOp_Activity = BOp_Activity_CTR(self)
        except:
            # (re-)initialize
            self.BOp_Activity = BOp_Activity_CTR(self)
       
        
    def submitJob(self, id, slotNo):
        '''
        Submits a job to this manager that then broadcasts a signal communicating the update.
        '''
        newJob = [id, slotNo]
        self._jobs.append(newJob)
        
        # submit update signal broadcast
        self.BOp_update.emit(id, slotNo)
        
        
    def getJobs(self):
        '''
        Returns a list with all current jobs and metadata in the queue for specified slot.
        '''
        return self._jobs
    
    
    
    

        

class BOp_Job_CTR(object):
    
    def __init__(self):
        
        super(BOp_Job_CTR, self).__init__()