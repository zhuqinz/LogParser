'''
LogMonitor is used to 
- Read all the log/error_log files under sub-directory of base directory
- Each directory will be treated as one target (refer to Target_Log)
- User can update watch list of keywords lively

Created on 2018-01-06
@author: Zhuqin
'''

from datetime import datetime
from multiprocessing import freeze_support
import multiprocessing
import ntpath
import os
import time
import tkFileDialog
import Utils


try:
    from Tkinter import *  # Python 2
    import ttk    
except ImportError:  # Python 3
    from tkinter import *
    import tkinter.ttk as ttk    

log_table_header = ['Folder name', 'total files', 'error found', 'Last updated']
log_table_col_width = [140, 100, 100, 300]

confPath = os.path.join(os.path.join(os.getcwd(), 'conf'), 'setup.ini')
CONF = Utils.ConfigureFile(confPath)
# confDir = "C:\\Users\\zhuqinz\\Desktop\\logMonitor\\conf"
UPDATE_TIMER = 2000
# ERROR_LOG_PATTERN = '.*-error.*.log'


class LogParserOverviewMP (object):

    def __init__(self, master, title):
        self.master = master
        self.title = title
        
        # Configurable fields
        self.baseDir = StringVar()
        self.includeCurrentLog = IntVar()
        self.itemToAdd = StringVar()
        self.sortByCol = 0
        
        # Multiprocessing
        self.exit_event = multiprocessing.Manager().Value('i', 0)
        self.records = multiprocessing.Manager().list([])
        self.scanJob = None
        
        self.setup_widget()
        self.loadInitData()
    
    def setup_widget(self):
        # Create Main Window
        self.master.wm_title(self.title)
        self.master.geometry('900x500')
        self.master.resizable(0, 0)
        
        #===Configuration frame===
        targetFrame = LabelFrame(self.master, text='Target ')
        targetFrame.grid(row=0, sticky='WE', padx=5, pady=5, ipadx=5, ipady=5)
        # Log file location base directory
        baseDir_lbl = Label(targetFrame, text='Log Files Base Directory:')
        baseDir_lbl.grid(row=0, column=0, sticky='W', padx=5, pady=2)
        baseDir_txt = Entry(targetFrame, textvariable=self.baseDir, width=50)
        baseDir_txt.grid(row=0, column=1, pady=3)
        baseDir_btn = Button(targetFrame, text='Browse...', command=self.loadBaseDirectory)
        baseDir_btn.grid(row=0, column=2, sticky=E, padx=5, pady=2)
        
        # ===Control frame===
        controlFrame = LabelFrame(self.master, text='Control ')
        controlFrame.grid(row=1, sticky='WE', padx=5, pady=5, ipadx=5, ipady=5)
#         includeCurrentLog_ck = Checkbutton(controlFrame, text='Include current log', variable=self.includeCurrentLog)
#         includeCurrentLog_ck.grid(row=0, column=0, sticky=W , padx=15, pady=2)
        start_btn = Button(controlFrame, text='Start/Restart', command=self.onClickStart, width=10)
        start_btn.grid(row=0, column=1, padx=150, pady=2)
        stop_btn = Button(controlFrame, text='Quit', command=self.onClickQuit, width=10)
        stop_btn.grid(row=0, column=2, sticky='E', padx=15, pady=2)
        
        # ===Monitor frame===
        self.logMonitorFrame = LabelFrame(self.master, text='Monitor')
        self.logMonitorFrame.grid(row=2, sticky='WE', padx=5, pady=5, ipadx=5, ipady=5)
        self.tabControl = ttk.Notebook(self.logMonitorFrame)
        
        # Tab Logs
        tabLogs = ttk.Frame(self.tabControl)
        self.tabControl.add(tabLogs, text='Logs')      
        self.tabControl.pack(expand=1, fill="both")
        self.logListTable = Utils.MultiColumnBox(parent=tabLogs, header=log_table_header, columnWidth=log_table_col_width, doubleClickCb=self.OnDoubleClickLogList)
                
        # Tab WatchList
        tabKeywordList = ttk.Frame(self.tabControl)
        self.tabControl.add(tabKeywordList, text='SysLog Conf')      
        self.tabControl.pack(expand=1, fill="both")
        # Watch List Box
        watchListBoxFrame = Frame(tabKeywordList, width=500)
        watchListBoxFrame.pack(side=LEFT, fill=BOTH)
        s = Scrollbar(watchListBoxFrame)
        s.pack(side=RIGHT, fill=Y)
        self.watchListBox = Listbox(watchListBoxFrame, width=60, selectmode=EXTENDED)
        self.watchListBox.pack(side=LEFT, fill=BOTH, padx=5, pady=5, ipadx=5, ipady=5)
        s.config(command=self.watchListBox.yview)
        self.watchListBox.config(yscrollcommand=s.set)
        # Sys log conf Control buttons
        watchBoxBtnFrame = Frame(tabKeywordList)
        watchBoxBtnFrame.pack(side=RIGHT)
        watchListLoad_btn = Button(watchBoxBtnFrame, text='Load Watch', command=self.loadWatchList, width=20)
        watchListLoad_btn.grid(row=0, column=2, columnspan=2, sticky='WE', padx=5, pady=5, ipadx=5, ipady=5)
        self.item_txt = Entry(watchBoxBtnFrame, textvariable=self.itemToAdd, width=20)
        self.item_txt.grid(row=1, column=2, sticky='WE', pady=5)
        watchListAdd_btn = Button(watchBoxBtnFrame, text='Add Item', command=self.onClickAdd)
        watchListAdd_btn.grid(row=1, column=3, sticky='WE', padx=5, pady=5, ipadx=5, ipady=5)
        watchListDel_btn = Button(watchBoxBtnFrame, text='Remove selected items', command=self.onClickDelete, width=20)
        watchListDel_btn.grid(row=2, column=2, columnspan=2, sticky='WE', padx=5, pady=5, ipadx=5, ipady=5)

    def loadInitData(self):
        self.syslogConf = Utils.ConfigureFile(path=os.path.join(CONF.get('SysLog', 'SYSLOG_CONF_DIR'), 'syslog.properties'))
        self.loadWatchList()

    # ============ Configure Frame Event ===========================
    def loadBaseDirectory(self):
        dirname = tkFileDialog.askdirectory(parent=self.master, initialdir=os.getcwd(), title='Please select a directory stored log files')
        if len(dirname) > 0:
            print ("Log File Base Directory %s " % dirname)
            self.baseDir.set(dirname)
        else:
            print ("Log File Base Directory not selected.")
            
    # ============ Control Frame Event =============================
    def onClickStart(self):
        self.stopScan()
        self.startScan()
        self.refreshResult()
    
    def onClickQuit(self):
        self.stopScan()
        sys.exit()
        
    def startScan(self):
        
        self.exit_event.value = 0
        
        del self.records[:]
        # Initial table
        folderList = [name for name in os.listdir(self.baseDir.get())
                          if os.path.isdir(os.path.join(self.baseDir.get(), name))]
        for f in folderList:
            self.records.append((f,0,0,0))
        
        self.scanJob = multiprocessing.Process(target=scanLogFolder, args=(self.baseDir.get(), self.exit_event, self.records))
        self.scanJob.daemon = True
        self.scanJob.start()
        
    def stopScan(self):
        self.exit_event.value = 1
        if self.scanJob != None:
            self.scanJob.join()
        print ("Scan stoped.")
            
    # ================ Log Table Frame ============================
    def refreshResult(self):
        
        if (self.tabControl.tab(self.tabControl.select(), "text") == 'Logs'):
            self.logListTable.build_tree(self.records)
        
        self.logMonitorFrame.after(UPDATE_TIMER, self.refreshResult)
               
    def OnDoubleClickLogList(self, selectedItem):
        id = selectedItem[0]
        if(id != ''):
            try:
                os.startfile(os.path.join(self.baseDir.get(), id))
            except IOError, err:
                print (err)
                print("Cannot open file" + os.path.join(self.baseDir, id))
             
    # ================ Watch List Frame Event ======================
    def loadWatchList(self):
        self.watchListBox.delete(0, END)
        # Read from conf
        try: 
            watchListStr = self.syslogConf.get('top', 'ERROR_KEYWORD')
            watchList = watchListStr.split(':')
        except Exception  as err:
            print (err)
            watchList = ['Rsyslog path is not found: ' + CONF.get('SysLog', 'SYSLOG_CONF_DIR')]
            
        for item in watchList:
                self.watchListBox.insert(END, item)
            
    def onClickAdd(self):
        text = self.item_txt.get()
        if not text.isspace():
            self.watchListBox.insert(END, text)
            self.UpdateListToConf()
        self.itemToAdd.set('')
            
    def onClickDelete(self):
        items = self.watchListBox.curselection()
        pos = 0
        for i in items :
            idx = int(i) - pos
            self.watchListBox.delete(idx, idx)
            pos = pos + 1
        self.UpdateListToConf()
        
    def UpdateListToConf(self):
        watchList = self.watchListBox.get(0, END)
        watchListStr = ':'.join(str(x) for x in watchList)
        self.syslogConf.set(section='top', option='ERROR_KEYWORD', value=watchListStr)
        self.syslogConf.updateConf()


def scanLogFolder(path, exit_event, records):

    targetList = []
    for idx, item in enumerate(records):
        subFolderPath = os.path.join(path, item[0])
        target = TargetFolder(subFolderPath, idx, records)
        targetList.append(target)
    
    while exit_event.value== 0:
        print "entered"
        for target in targetList:
            if (exit_event.value == 0):
                target.update()
            else:
                break
        time.sleep(3)

class TargetFolder(object):

    def __init__(self, path, idx, records):
        self.idx = idx
        self.path = path
        self.records = records
        self.lastUpdateTime = 0
        self.totalErrors = 0
        self.Id = ntpath.basename(self.path)
    
    def update(self):
        self.read_logs()
        self.update_record()
    
    def read_logs(self):
        totalErrorLogFiles = [basename for basename in os.listdir(self.path)
                      if(os.path.isfile(os.path.join(self.path, basename))) and re.match(CONF.get('SysLog','ERROR_LOG_PATTERN'), basename)]
        self.totalErrorFiles = len(totalErrorLogFiles)
        
        for f in totalErrorLogFiles:
            path = os.path.join(self.path, f)
            if os.path.getmtime(path) > self.lastUpdateTime:
                self.lastUpdateTime = os.path.getmtime(path)
                self.totalErrors += Utils.countFileLines(path)

    def update_record(self):
        record = (self.Id, self.totalErrorFiles, self.totalErrors, datetime.fromtimestamp(self.lastUpdateTime).strftime("%Y-%m-%d %H:%M:%S"))
        self.records[self.idx] = record

if __name__ == '__main__':
    freeze_support()
    
    top = Tk()
    LogParserOverviewMP(top, title='Log Monitor v1.00')
    top.mainloop()
