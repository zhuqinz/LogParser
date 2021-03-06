'''
LogParserOverview is used to 
- read all the log files under base directory (baseDir)
- read all the log files under sub-directories of base directory
- Each directory will be treated as one target, related info will be displayed in related tabs (_LogParser Class)
- It supports to analyze log files lively (auto refresh) 

Author: Zhuqin
'''
import datetime
from multiprocessing import freeze_support
import multiprocessing
import os
import tkFileDialog

import LogParser
import MultiColumnBox


# import LogParser2
try:
    from Tkinter import *
#     import ttk
except ImportError:  # Python 3
    from tkinter import *
#     import tkinter.ttk as ttk

table_header = ['Folder name', 'total files', 'error found']
REFRESH_TIMER = 2000

class LogParserOverview (object):

    def __init__(self, master, title):
        self.master = master
        self.title = title
        
        # Configuration fields
        self.baseDir = StringVar()
        self.watchListName = StringVar()
        self.updateTime = StringVar()
        self.autoRefresh = IntVar()
        
        # Multiprocessing
        self.jobs = []
        self.watchList = multiprocessing.Manager().list([])
        self.records = multiprocessing.Manager().list([])
        
        self.OnInit()
        
    def OnInit(self):
        # Create Main Window
        self.master.wm_title(self.title)
        self.master.geometry('800x600')
        self.master.resizable(0, 0)
        
        # ===Configuration frame for user to select files===
        configFrame = LabelFrame(self.master, text='Configuration ', height='300')
        configFrame.grid(row=0, columnspan=4, sticky='WE', padx=5, pady=5, ipadx=5, ipady=5)
        # Log file location base directory
        baseDir_lbl = Label(configFrame, text='Log Files Base Directory:')
        baseDir_lbl.grid(row=0, column=0, sticky=W, padx=5, pady=2)
        baseDir_txt = Entry(configFrame, textvariable=self.baseDir, width=80)
        baseDir_txt.grid(row=0, column=1, columnspan=2, sticky=NW, pady=3)
        baseDir_btn = Button(configFrame, text='Browse...', command=self.loadBaseDirectory)
        baseDir_btn.grid(row=0, column=7, sticky=E, padx=5, pady=2)
        # Watch resultList file location
        baseDir_lbl = Label(configFrame, text='Watch List File: ')
        baseDir_lbl.grid(row=1, column=0, sticky=W, padx=5, pady=2)
        baseDir_txt = Entry(configFrame, textvariable=self.watchListName, width=80)
        baseDir_txt.grid(row=1, column=1, columnspan=5, sticky=NW, pady=3)
        baseDir_btn = Button(configFrame, text='Browse...', command=self.loadWatchList)
        baseDir_btn.grid(row=1, column=7, sticky=E, padx=5, pady=2)
                
        # ===Control frame===
        # Auto refresh
        controlFrame = LabelFrame(self.master, text='Control ', height='300')
        controlFrame.grid(row=1, columnspan=7, sticky='WE', padx=5, pady=5, ipadx=5, ipady=5)
        autoRefresh_ck = Checkbutton(controlFrame, text='Auto Refresh', variable=self.autoRefresh)
        autoRefresh_ck.grid(row=0, column=0, sticky=W , padx=15, pady=2)
        start_btn = Button(controlFrame, text='Start', command=self.onClickStart, width=10)
        start_btn.grid(row=0, column=1, sticky=E, padx=5, pady=2)
        blank_lbl_2 = Label(controlFrame, width=20)
        blank_lbl_2.grid(row=0, column=2, sticky=W, padx=5, pady=2)
        stop_btn = Button(controlFrame, text='Stop', command=self.onClickStop, width=10)
        stop_btn.grid(row=0, column=3, sticky=E, padx=5, pady=2)
        blank_lbl_3 = Label(controlFrame, width=20)
        blank_lbl_3.grid(row=0, column=4, sticky=W, padx=5, pady=2)
        exit_btn = Button(controlFrame, text='Exit', command=self.onClickExit, width=10)
        exit_btn.grid(row=0, column=5, sticky=E, padx=5, pady=2)
        
        # ===== Result screen display frame ====
        self.resultFrame = LabelFrame(self.master, text='Result Screen')
        self.resultFrame.grid(row=2, columnspan=7, sticky='WE', padx=5, pady=5, ipadx=5, ipady=5)
        msg = Message(self.resultFrame, textvariable=self.updateTime, relief=SUNKEN, width=400)
        msg.pack(side=TOP)
        self.resultList = MultiColumnBox.MultiColumnBox(parent=self.resultFrame, header=table_header)
                
    def loadBaseDirectory(self):
        dirname = tkFileDialog.askdirectory(parent=self.master, initialdir=os.getcwd(), title='Please select a directory stored log files')
        if len(dirname) > 0:
            print ("Log File Base Directory %s " % dirname)
            self.baseDir.set(dirname)
        else:
            print ("Log File Base Directory not selected.")
        
    def loadWatchList(self):
        watchListFile = tkFileDialog.askopenfile(parent=self.master, mode='rb', title='Choose a file contains watch resultList')
        if watchListFile != None:
            self.watchListName.set(watchListFile.name)
            print ("Watch List file selected: %s" % watchListFile.name)
            with open(watchListFile.name) as f:
                self.watchList = f.readlines()
            self.watchList = [x.strip() for x in self.watchList]
        else:
            print ("No watch resultList file selected.")    
    
    def onClickStart(self):
        # Stop current running job
        self.cleanResult()
        
        # Start new job resultList
        self.startAll()
        
        # Display result
        self.displayResult()
    
    def onClickStop(self):
        self.stopAll()
        
    def onClickExit(self):
        self.stopAll()
        print ("Exit...")
        sys.exit()
   
    def stopAll(self):
        
        for job in self.jobs:
            job.terminate()
            job.join()

        self.jobs = []
#         while len(self.jobs) > 0:
#             self.jobs = [job for job in self.jobs if job.is_alive()]
#             time.sleep(1)
        
    def startAll(self):
        
        targetList = [""] + [name for name in os.listdir(self.baseDir.get())
            if os.path.isdir(os.path.join(self.baseDir.get(), name))]
        targetList = [os.path.join(self.baseDir.get(), basename) for basename in targetList]
         
        for path in targetList:
            p = LogParser.LogParser(path=path, watchList=self.watchList, records=self.records)
            self.jobs.append(p)
            p.daemon = True
            p.start()
             
        print('Jobs started')
    
    def displayResult(self):
        
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.updateTime.set('Log parsing started at: ' + now)
         
        if self.autoRefresh.get() == 0:
            self.resultList.build_tree(self.records) 
        else:
            self.resultList.build_tree(self.records) 
            self.resultFrame.after(REFRESH_TIMER, self.displayResult)        
    
    def cleanResult(self):
        self.stopAll()


if __name__ == '__main__':
    freeze_support()
    top = Tk()
    LogParserOverview(top, title='Log Parser Tool v1.00')
    top.mainloop()
    
