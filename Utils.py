from itertools import count
try:
    from Tkinter import *
    import tkFont
    import ttk
except ImportError:  # Python 3
    from tkinter import *
    import tkinter.font as tkFont
    import tkinter.ttk as ttk

from ConfigParser import ConfigParser
from StringIO import StringIO 

class MultiColumnBox(object):
    '''
        Provide multiple cloumnBox
    '''

    def __init__(self, parent, header, columnWidth):
        self.tree = None
        self.parent = parent
        self.header = header
        self.columnWidth = columnWidth
        
        self._setup_widgets()
        
    def _setup_widgets(self):
        container = ttk.Frame(self.parent)
        container.pack(fill='both', expand=True)
        
        self.tree = ttk.Treeview(columns=self.header, show="headings")
        vsb = ttk.Scrollbar(orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(column=0, row=0, sticky='nsew', in_=container, padx=5, pady=5)
        vsb.grid(column=1, row=0, sticky='ns', in_=container)
        hsb.grid(column=0, row=1, sticky='ew', in_=container)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)
        
    def build_tree(self, content=[]):
        
        self.tree.delete(*self.tree.get_children())
        
        for ix, col in enumerate(self.header):
            self.tree.heading(col, text=col.title(),
                command=lambda c=col: sortby(self.tree, c, 0))
            col_w = self.columnWidth[ix]
            self.tree.column(self.header[ix], width=col_w,anchor=E)
            # adjust the column's width to the header string
#             self.tree.column(col,
#                 width=tkFont.Font().measure(col.title()) + 20)

        for item in content:
            self.tree.insert('', 'end', values=item)
            # adjust column's width if necessary to fit each value
#             for ix, val in enumerate(item):
#                 col_w = tkFont.Font().measure(val) + 5
#                 if self.tree.column(self.header[ix], width=None) < col_w:
#                     self.tree.column(self.header[ix], width=col_w)
        
        self.tree.update()
        
class ConfigureFile(ConfigParser):
    '''
        - Read configuration from properties file
        - Update configuration to the properties file
    '''
    def __init__(self, path, withSection=False):
        ConfigParser.__init__(self)
        self.optionxform=str
        
        self.path = path
        self.withSection = withSection
        
        self.loadConf()
        
    def loadConf(self):
        try:
            with open(self.path) as stream:
                if not self.withSection:
                    stream = StringIO('[top]\n' + stream.read())
                self.readfp(stream)
        except IOError, err:
            print (err)
            print("Cannot open file" + self.path)
            
    def updateConf(self):
        try:
            with open(self.path, 'wb') as outFile:
                self.write(outFile)
                
            if not self.withSection:
                # remove first line which is not in properties
                with open(self.path, 'r') as fin:
                    data = fin.read().splitlines(True)
                with open(self.path, 'wb') as fout:
                    fout.writelines(data[1:])
        except IOError, err:
            print (err)
            print("Cannot open file" + self.path)
        
    
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
    
def countFileLines(path):
    count = 0
    try:
        with open(path, 'r') as f:
            for l in f:
                count +=1
        return count
    except IOError, err:
        print(err)
        print("Cannot open file: "+ path)
        return 0

def updateRowById(records,Id,content):  
    '''
        Search the list of tuples by the first element in tuple,
        if found, update the tuple with content
        if not found, append that tuple to the list
    '''
    found = False
    for idx, val in enumerate(records):
        if val[0] == Id:
            records[idx] = content
            found = True
            break
    
    if not found:
        records.append(content)
        
    
        