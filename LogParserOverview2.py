'''
LogParserOverview is used to 
- read all the log files under base directory (baseDir)
- read all the log files under sub-directories of base directory
- Each directory will be treated as one target, related info will be displayed in related tabs (_LogParser Class)
- It supports to analyze log files lively (auto refresh) 

Author: Zhuqin
'''
import datetime
import multiprocessing
import ntpath
import os
import time
import tkFileDialog
import MultiColumnBox
import LogParser_2

# import LogParser2
try:
    from Tkinter import *
#     import ttk
except ImportError:  # Python 3
    from tkinter import *
#     import tkinter.ttk as ttk

table_header = ['Folder name', 'total files', 'error found']
REFRESH_TIMER = 5000

class LogParserOverview2 (object):

    def __init__(self, master, title):
        self.master = master
        self.title = title
        self.baseDir = StringVar()
        self.watchListName = StringVar()
        self.updateTime = StringVar() 
        self.watchList = []
        self.autoRefresh = IntVar()
        self.jobs = []
        self.records = multiprocessing.Manager().list([])
        
        self.OnInit()
        
    def OnInit(self):
        # Create Main Window
        self.master.wm_title(self.title)
        self.master.geometry('1200x700')
        self.master.resizable(0, 1)
        
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
        self.running = False
        for job in self.jobs:
            job.terminate()
            job.join()
        self.jobs = []
    
#     def parseLogs(self):
#                 
#         # Get directory resultList
#         targetList = [""] + [name for name in os.listdir(self.baseDir.get())
#             if os.path.isdir(os.path.join(self.baseDir.get(), name))]
#         targetList = [os.path.join(self.baseDir.get(), basename) for basename in targetList]
#         
#         for path in targetList:
# #             p = multiprocessing.Process(target=Log, args=(self.watchList,path))
# #             p.start()
# #             pass
#             logTab = LogParser.LogParser(path=path, watchList=self.watchList, tabControl=self.tabControl, autoRefresh=self.autoRefresh.get())
#             self.jobs.append(logTab)
#             logTab.start()    
    
    def startAll(self):
         
        # Get directory resultList
        targetList = [""] + [name for name in os.listdir(self.baseDir.get())
            if os.path.isdir(os.path.join(self.baseDir.get(), name))]
        targetList = [os.path.join(self.baseDir.get(), basename) for basename in targetList]
         
        for path in targetList:
            p = LogParser_2.LogParser_2(path=path, watchList=self.watchList, records = self.records)
            self.jobs.append(p)
            p.start()
             
        print('Jobs started')
    
    def displayResult(self):
        
        print('Refreshing...')
        
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.updateTime.set('Log parsing started at: ' + now)
         
        if self.autoRefresh.get() == 0:
#             pass
            self.resultList.build_tree(self.records) 
        else:
            for item in self.records:
                print('Received in tree: ', item)
            
            self.resultList.build_tree(self.records) 
            self.resultFrame.after(3000, self.displayResult)        
            
    
#     def refresh(self):
#         print('refreshed')
#         now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         self.updateTime.set('Log parsing started at: ' + now)
        
#         self.resultList.build_tree(self.records)
         
#         now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         self.updateTime.set('Log parsing started at: ' + now)
#         
#         if self.autoRefresh.get() == 0:
#             self.parseLogs()
#         else:
#             self.parseLogs()
#             self.resultFrame.after(2000, self.startAll)        
        
    def cleanResult(self):
        # Wait all threads finish
        for i in self.jobs:
            i.terminate()
            i.join()
        
        self.jobs = []
#         
#         if self.autoRefresh.get() == 0:
#             self.parseLogs(tabControl)
#         else:
#             self.parseLogs(tabControl)
#             resultFrame.after(5000, self.startParse)
#             
#     def parseLogs(self, tabControl):  
#         
#         # Get directory resultList
#         dirList = [""] + [name for name in os.listdir(self.baseDir.get())
#             if os.path.isdir(os.path.join(self.baseDir.get(), name))]
#         targetList = [path for path in dirList if not self.findTargetDir(path) == None]
#         targetList = [os.path.join(self.baseDir.get(), basename) for basename in targetList]
#                 
#         # Create tabs for each directories
#         self.jobs = []
#         for path in targetList:
#             tab = self.createTab(tabControl, path)
#             p = _LogParser.LogParserProcess(path, self.watchList, tab)
#             self.jobs.append(p)
#             p.start()
#         
#         for i in self.jobs:
#             i.join()
#     
#     def createTab(self, tabControl, path):
#         tab = ttk.Frame(tabControl)
#         tabName = ntpath.basename(path)
#         tabControl.add(tab, text=tabName)
#         tabControl.pack(expand=1, fill=BOTH)
#         return tab
    
#     def findTargetDir(self, path):
#         fullPath = os.path.join(self.baseDir.get(), path)
#         files = [f for f in os.listdir(fullPath) if re.match('.*.log', f)]
#         if files == []:
#             return None
#         else:
#             return path   

# def createNewTab(tabControl):
    
# def Log(watchList, path):    
#     listBox = LogParser.LogParser(watchList, path)


if __name__ == '__main__':
    top = Tk()
    LogParserOverview2(top, title='Log Parser Tool v1.00')
    top.mainloop()
    