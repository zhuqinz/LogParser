import multiprocessing
import ntpath
import time
import os
import re
import Utils
from datetime import datetime

REFRESH_TIMER = 2
# ERROR_LOG_PATTERN = '.*-error_[0-9]+.log'
ERROR_LOG_PATTERN = '.*-error.*.log'
# e.g.172.24.201.114_1515108631327-error_20180106172345.log is matched.
# e.g. 172.24.201.114_1515108631327-error.log is not matched.

class LogMonitor(multiprocessing.Process):
    '''
    Update the info for the files under given path
    '''
    def __init__(self, path, records, exitEvent):
        multiprocessing.Process.__init__(self)
        self.path = path
        self.records = records
        self.exit_event = exitEvent
        
        self.OnInit()
        
        print("Start job: "+ self.Id)
    
    def run(self):
        while(self.exit_event.value == 0):
            self.totalErrorFiles = 0
            
            self.read_logs()
            self.update_record()
            time.sleep(REFRESH_TIMER)
        
        print (self.Id , " doing cleanup and leaving ...")
        
    def OnInit(self):
        self.Id = ntpath.basename(self.path)
        self.lastUpdateTime = 0
        self.totalErrors = 0
    
    def read_logs(self):
        
        totalErrorLogFiles = [basename for basename in os.listdir(self.path)
                      if(os.path.isfile(os.path.join(self.path, basename))) and re.match(ERROR_LOG_PATTERN, basename)]
        self.totalErrorFiles = len(totalErrorLogFiles)
        
        for f in totalErrorLogFiles:
            path = os.path.join(self.path,f)
            if os.path.getmtime(path) > self.lastUpdateTime:
                self.lastUpdateTime = os.path.getmtime(path)
                self.totalErrors += Utils.countFileLines(path)
                
    def update_record(self):
        record = (self.Id, self.totalErrorFiles, self.totalErrors, datetime.fromtimestamp(self.lastUpdateTime).strftime("%Y-%m-%d %H:%M:%S"))
        Utils.updateRowById(self.records, self.Id, record)
        

                    
                        
            