import ntpath
import os
import threading
import datetime
import time


try:
    from Tkinter import *
    import tkFont
    import ttk
except ImportError:  # Python 3
    from tkinter import *
    import tkinter.font as tkFont
    import tkinter.ttk as ttk

table_header = ['File Name', 'Caught', 'Full line']

     
class LogParser(threading.Thread):

    def __init__(self, path, watchList, tabControl):
        threading.Thread.__init__(self)
        self.tree = None
        self.caught_list = []
        
        self.watchList = watchList
        self.path = path
        self.tabControl = tabControl
        self.tab = None
#         self.autoRefresh = autoRefresh
        self.updateTime = StringVar()
        
        self._setup_widgets()
#         self.displayData()
        self._read_log()
        self._build_tree()

    def _setup_widgets(self):
        
        # New Tab
        self.tab = ttk.Frame(self.tabControl)
        tabName = ntpath.basename(self.path)
        if (tabName == ''):
            tabName = 'Main'
        self.tabControl.add(self.tab, text=tabName)
        self.tabControl.pack(expand=1, fill="both", side=BOTTOM, ipadx=5, ipady=5, padx=5, pady=5)
        # New Window
#         self.root = Tk()
#         container = ttk.Frame(self.root)
#         container.pack(fill='both', expand=True)

        self.tree = ttk.Treeview(columns=table_header, show="headings")
        vsb = ttk.Scrollbar(orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(column=0, row=0, sticky='nsew', in_=self.tab, padx=5, pady=5)
        vsb.grid(column=1, row=0, sticky='ns', in_=self.tab)
        hsb.grid(column=0, row=1, sticky='ew', in_=self.tab)
        self.tab.grid_columnconfigure(0, weight=1)
        self.tab.grid_rowconfigure(0, weight=1)
        timeLable = ttk.Label(self.tab, textvariable=self.updateTime, width=400)
        timeLable.grid(column=0,row=2, sticky='n', in_=self.tab, padx=5, pady=5)

    def _read_log(self):
#         files = [f for f in os.listdir(self.path) if re.match('.*.log', f)]

        files = [f for f in os.listdir(self.path)]
         
        for f in files:
            p = os.path.join(self.path, f)
            if(os.path.isfile(p)):
#                 print ("try to open: " + p)
                try:
                    with open(p, 'r') as logFile:
                        for line in logFile:
                            if any(s in line for s in self.watchList):
                                self.recordFinding(ntpath.basename(p), line)
                except IOError, err:
                        print (err)
                        print("Cannot open file" + p )
         
    def recordFinding(self, fileName, line):
        match = ''
        for l in self.watchList:
            if l in line:
                match = l
        row = (fileName, match, line.strip())
        self.caught_list.append(row)
    
#     def displayData(self):
#         now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         self.updateTime.set('Log updated at: ' + now)
#         if(self.autoRefresh==0):
#             print "No auto refresh"
#             self._read_log()
#             self._build_tree()
#         else:
#             print "Auto Refreshing..."
#             self._read_log()
#             self._build_tree()
#             self.tree.after(10000, self.displayData())

    def _build_tree(self):
        for col in table_header:
            self.tree.heading(col, text=col.title(),
                command=lambda c=col: sortby(self.tree, c, 0))
            # adjust the column's width to the header string
            self.tree.column(col,
                width=tkFont.Font().measure(col.title()))

        for item in self.caught_list:
            self.tree.insert('', 'end', values=item)
            # adjust column's width if necessary to fit each value
            for ix, val in enumerate(item):
                col_w = tkFont.Font().measure(val)
                if ((self.tree.column(table_header[ix], width=None) < col_w) & (ix != 2)):
                    self.tree.column(table_header[ix], width=col_w)
    
def sortby(tree, col, descending):
    """sort tree contents when a column header is clicked on"""
    # grab values to sort
    data = [(tree.set(child, col), child) \
        for child in tree.get_children('')]
    # if the data to be sorted is numeric change to float
    # data =  change_numeric(data)
    # now sort the data in place
    data.sort(reverse=descending)
    for ix, item in enumerate(data):
        tree.move(item[1], '', ix)
    # switch the heading so it will sort in the opposite direction
    tree.heading(col, command=lambda col=col: sortby(tree, col, \
        int(not descending)))

