'''
Created on Jan 3, 2018

@author: ZhuqinZ
'''
import multiprocessing
import os
import re
import time
import ntpath

SLEEP_TIME = 2

class LogParser_2(multiprocessing.Process):
    '''
    Log parser process to screen the log, and save the screened log in error.list file
    '''

    def __init__(self, path, watchList, records):
        multiprocessing.Process.__init__(self)
        self.path = path
        self.watchList = watchList
        self.records = records
        
        self.totalFiles = 0
        self.caughtList=[]
        self.stop = False
        
    def run(self):
        while(not self.stop):
            self.caughtList=[]
            self.totalFiles = 0
            self.read_log()
            self.update_result()
            time.sleep(SLEEP_TIME)
    
    def stop(self):
        self.stop = True    
        
    def read_log(self):
        files = [name for name in os.listdir(self.path)
            if (os.path.isfile(os.path.join(self.path, name)) and not re.match('.*.list',name))]
        
        self.totalFiles = len(files)        
        
        for f in files:
            p = os.path.join(self.path, f)
            try:
                with open(p, 'r') as logFile:
                        for line in logFile:
                            if any(s in line for s in self.watchList):
                                self.recordFinding(f, line)
            
            except IOError, err:
                print (err)
                print("Cannot open file" + p )
    
    def recordFinding(self, filename, line):
        match = ''
        for l in self.watchList:
            if l in line:
                match = l
        row = (filename, match, line.strip())
        self.caughtList.append(row)
        
    def update_result(self):
        
        # Prepare result
        folder = ntpath.basename(self.path)
        if folder == '':
            folder = 'Main'
        result = (folder, self.totalFiles, len(self.caughtList))
        
        # Find filename in the table
        found = False
        for item in self.records:
            if item[0] == folder:
                print ('Update table', result)
                item = result
                found = True
                break
        
        if not found:
            print ("no record found for : " + folder)
            print( "Add tuple " , result)
            self.records.append(result)
        
        # Update that line's statistics
        