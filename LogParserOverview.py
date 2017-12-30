'''
LogParser is used to 
- read all the log files under base directory (baseDir)
- read all the log files under sub-directories of base directory
- Each directory will be treated as one unit, related info will be displayed in related tabs
- if any content in the log files match the (error) content listed in watchList
  display in the table, and save it to xxxx_error.log (xxx is original log file name)
- It supports to analyze log files lively (auto refresh) 

Author: Zhuqin
'''
from Tkinter import *
import os
import tkFileDialog


class LogParserOverview (object):

    def __init__(self, master, title):
        self.master = master
        self.title = title
        self.baseDir = StringVar()
        self.watchList = ''
        
        self.OnInit()
        
    def OnInit(self):
        # Create Main Window
        self.master.title(self.title)
        self.master.geometry('1100x700')
        self.master.resizable(0, 1)
        
        # Configuration frame for user to select files
        mainFrame = LabelFrame(master=self.master, text='Configuration ', height='300', labelanchor='nw')
        mainFrame.pack(anchor=N, fill=X, expand=True, padx=5)
        # Log file location base directory
        baseDir_lbl = Label(mainFrame, text='Log Files Base Directory:')
        baseDir_lbl.pack(anchor=NW, side=LEFT, padx=5, pady=5)
        baseDir_entry = Entry(mainFrame, relief=FLAT, width=80, textvariable=self.baseDir)
        baseDir_entry.pack(padx=5, pady=5, side=LEFT, expand=True)
        baseDir_btn = Button(mainFrame, text='Browse', command=self.loadBaseDirectory)
        baseDir_btn.pack(side=RIGHT, padx=5, pady=5, expand=True)
            
    def loadBaseDirectory(self):
        self.baseDir.set(tkFileDialog.askdirectory(parent=self.master, initialdir=os.getcwd(), title='Please select a directory stored log files'))


if __name__ == '__main__':
    top = Tk()
    LogParserOverview(top, title='Log Parser Tool v1.00')
    top.mainloop()
    
