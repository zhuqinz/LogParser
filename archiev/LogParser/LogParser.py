'''
Created on Jan 3, 2018

@author: ZhuqinZ
'''
import multiprocessing
import ntpath
import os
import re
import time
import csv


SLEEP_TIME = 2


class LogParser(multiprocessing.Process):
    '''
    Log parser process to screen the log, and save the screened log in _error.csv file
    '''

    def __init__(self, path, watchList, records):
        multiprocessing.Process.__init__(self)
        self.path = path
        self.watchList = watchList
        self.records = records
        
        self.OnInit()
        
    def run(self):
        while(not self.stop):
            
            self.caughtList = []
            self.totalFiles = 0
            
            self.getUpdateTime()
            self.read_log()
            self.write_to_error_log()
            self.update_result()
            time.sleep(SLEEP_TIME)
        
        print ("Job stopped: ", self.parserName, " pid: ", os.getpid())
    
    def OnInit(self):
        # Initialize Parser Name
        self.parserName = ntpath.basename(self.path)
        if self.parserName == '':
            self.parserName = 'Main'
        
        self.totalFiles = 0
        self.stop = False
        self.caughtList = []
        self.errorLogFileName = os.path.join(self.path, self.parserName + '_error.csv')
    
    def getUpdateTime(self):
        try:
            with open(self.errorLogFileName, 'r') as f:
                self.lastUpdateTime = os.path.getmtime(self.errorLogFileName)
            f.close()
        except IOError, err:
                print (err)
                print("Cannot open file" , self.errorLogFileName)
                self.lastUpdateTime = 0
        
    def read_log(self):
        
        # Total files in the directory
        totalFiles = [name for name in os.listdir(self.path)
            if (os.path.isfile(os.path.join(self.path, name)) and not re.match('.*_error.csv', name))]
        self.totalFiles = len(totalFiles)
        
        # Newly added files
        newFiles = [name for name in totalFiles if os.path.getmtime(os.path.join(self.path, name)) > self.lastUpdateTime]
        
        for f in newFiles:
            p = os.path.join(self.path, f)
            try:
                with open(p, 'r') as logFile:
                        for line in logFile:
                            if any(s in line for s in self.watchList):
                                self.recordFinding(f, line)
            
            except IOError, err:
                print (err)
                print("Cannot open file" + p)
    
    def recordFinding(self, filename, line):
        match = ''
        for l in self.watchList:
            if l in line:
                match = l
        row = (filename, match, line.strip())
        self.caughtList.append(row)
        
    def write_to_error_log(self):
        if len(self.caughtList) > 0:
            
            with open(self.errorLogFileName, 'ab') as errorLogFile:
                csv_out=csv.writer(errorLogFile)
                for row in self.caughtList:
                    csv_out.writerow(row)
            errorLogFile.close()

    def countFileLines(self):
        count = 0
        try:
            for line in open(self.errorLogFileName).xreadlines(  ): count += 1
            return count
        except IOError, err:
                print (err)
                print("Cannot open file" + self.errorLogFileName)
                return 0
        
    def update_result(self):
        
        count = self.countFileLines()
        result = (self.parserName, self.totalFiles, count)
        
        # Find filename in the table
        found = False
        for idx, val in enumerate(self.records):
            if val[0] == self.parserName:
                self.records[idx] = result
                found = True
                break
        
        if not found:
            print ("no record found for : " + self.parserName)
            print("Add tuple " , result)
            self.records.append(result)
            
