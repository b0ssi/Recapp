'''
Created on 19/11/2012

@author: frieder.czeschla

These classes accept jobs submitted by certain modules and manage them on request of others (such as the queue, execution, report, precheck etc.)
They also centrally link the job-data up to the dbs.
Designed to start at application runtime initiation and stop at application exit (system-wide, not restricted to user-sessions).
'''
from PyQt4 import QtCore
from bop.activity import BOp_Activity_CTR
from bop.prep import BOp_Prep_CTR


class BOp_Jobs_CTR(QtCore.QObject):
    
    _jobs = []
    BOp_update = QtCore.pyqtSignal(int, int)
    
    def __init__(self, session_gui):
        
        self.parent = session_gui
        
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
        
        
    def open_BOp_Prep(self, setId):
        '''
        Opens the Backup Operations Activity window.
        '''
        # close if already open
        try:
            if self.BOp_Prep.isHidden() == True:
                self.BOp_Prep = BOp_Prep_CTR(self)
        except:
            # (re-)initialize
            self.BOp_Prep = BOp_Prep_CTR(self, setId)
       
        
    def prepJob(self, setId):
        '''
        Opens BOp_Prep_CTR to run prep checks on given job
        '''
        # create new BOp_Job_CTR
        BOp_Job = BOp_Job_CTR(self)
        
        slotNo = -1
        newJob = { slotNo : [ BOp_Job, slotNo ] }
        self._jobs.append(newJob)
        
        # open BOp_Prep_CTR
        self.BOp_Prep = BOp_Prep_CTR(self, setId)
        
        
    def submitJobToPrep(self, setId, slotNo):
        '''
        Submits a job to this manager that then broadcasts a signal communicating the update.
        '''
        
        # submit update signal broadcast
        self.BOp_update.emit(setId, slotNo)
        
        
    def getJobs(self):
        '''
        Returns a list with all current jobs and metadata in the queue for specified slot.
        '''
        return self._jobs
    
    
    
    

        

class BOp_Job_CTR(object):
    
    def __init__(self, session_gui):
        
        self.parent = session_gui
        
        super(BOp_Job_CTR, self).__init__()