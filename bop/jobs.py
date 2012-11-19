'''
Created on 19/11/2012

@author: frieder.czeschla

These classes accept jobs submitted by certain modules and manage them on request of others (such as the queue, execution, report, precheck etc.)
They also centrally link the job-data up to the dbs.
Designed to start at application runtime initiation and stop at application exit (system-wide, not restricted to user-sessions).
'''


class BOp_Jobs_CTR(object):
    
    def __init__(self):
        
        super(BOp_Jobs_CTR, self).__init__()