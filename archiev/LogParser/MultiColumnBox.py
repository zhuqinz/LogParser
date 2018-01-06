'''
Created on Jan 3, 2018

@author: ZhuqinZ
'''
try:
    from Tkinter import *
    import tkFont
    import ttk
except ImportError:  # Python 3
    from tkinter import *
    import tkinter.font as tkFont
    import tkinter.ttk as ttk

class MultiColumnBox(object):

    def __init__(self, parent, header):
        self.tree = None
        self.parent = parent
        self.header = header
        
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
        
        for col in self.header:
            self.tree.heading(col, text=col.title(),
                command=lambda c=col: sortby(self.tree, c, 0))
            # adjust the column's width to the header string
            self.tree.column(col,
                width=tkFont.Font().measure(col.title()))

        for item in content:
            self.tree.insert('', 'end', values=item)
            # adjust column's width if necessary to fit each value
            for ix, val in enumerate(item):
                col_w = tkFont.Font().measure(val)
                if self.tree.column(self.header[ix], width=None) < col_w:
                    self.tree.column(self.header[ix], width=col_w)
        
        self.tree.update()
                    
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
        