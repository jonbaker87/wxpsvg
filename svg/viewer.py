import os
from cStringIO import StringIO

import wx
import wx.aui
from wx.lib.mixins import treemixin

import svg.document as document

class ReferencePanel(wx.Panel):
    def __init__(self, parent, bmp):
        super(ReferencePanel, self).__init__(parent)
        self.bmp = bmp
        self.Bind(wx.EVT_PAINT, self.OnPaint)
    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        if self.bmp:
            dc.DrawBitmap(self.bmp, 0, 0)



class XMLTree(wx.TreeCtrl):
    """
        wxTreeCtrl that displays an ElementTree
    """
    def __init__(self, parent, tree=None):
        wx.TreeCtrl.__init__(self, parent)
        if tree:
            self.updateTree(tree)
    def updateTree(self, tree):
        self.DeleteAllItems()
        self.tree = tree
        self.addElementToTree(self.tree.getroot(), None)
        self.SetPyData(self.GetRootItem(), self.tree.getroot())
        self.Expand(self.GetRootItem())
        
            
    def addElementToTree(self, element, node):
        """ Recursively adds an element to the tree.
        element is the element being added, node is the parent node.
        If node is None, then the element is the root.
        """
        if node is None:
            node = self.AddRoot(element.tag)
        else:
            if element.text and element.text.strip():
                txt = element.tag + ':' + element.text
            else:
                txt = element.tag
            node = self.AppendItem(node, txt)
            self.SetPyData(node, element)
        #children
        for child in element.getchildren():
            self.addElementToTree(child, node)
        #attributes
        for key, value in element.items():
            item = self.AppendItem(node, "%s:%s"%(key,value))
            self.SetPyData(item, element)
            
class RenderPanel(wx.PyPanel):
    def __init__(self, parent, document=None):
        wx.PyPanel.__init__(self, parent)
        self.document = document
        self.zoom = 100
        #self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnWheel)
        
    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        if not self.document:
            return
        gc = wx.GraphicsContext_Create(dc)
        scale = float(self.zoom) / 100.0
        gc.Scale(scale, scale)
        self.document.render(gc)
        
    def GetBestSize(self):
        if not self.document:
            return (-1,-1)
        sz = map(int,self.document.tree.getroot().get("viewBox").split())
        return wx.Rect(*sz).GetSize()
    
    def OnWheel(self, evt):
        self.zoom += (evt.m_wheelRotation / evt.m_wheelDelta) * 10
        self.Refresh()
        
    
class ViewFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent)
        self._mgr = wx.aui.AuiManager()
        self._mgr.SetManagedWindow(self)
        
        self.wrap = wx.Panel(self)
        
        self.document = document.SVGDocument(StringIO(document.document))
        self.tree = XMLTree(self, self.document.tree)
        self.render = RenderPanel(self.wrap, self.document)
        self.reference = ReferencePanel(self.wrap, None)
        sz = wx.BoxSizer(wx.HORIZONTAL)
        sz.Add(self.render, 1, wx.EXPAND|wx.RIGHT, 1)
        sz.Add(self.reference, 1, wx.EXPAND|wx.LEFT, 1)
        self.wrap.SetSizer(sz)
        
        self.SetMenuBar(self.makeMenus())
        self.SetToolBar(self.makeToolBar())
        
        self._mgr.AddPane(
            self.tree, 
                wx.aui.AuiPaneInfo().
                    Top().
                    CloseButton(False).
                    Layer(0).
                    Caption("XML Tree").
                    MinSize(self.tree.GetBestSize()),
            "XML TREE"
        )
        
        self._mgr.AddPane(
            self.wrap, 
            wx.aui.AuiPaneInfo().CentrePane().Caption("SVG Rendering"),
            "VIEWER"
        )        
        
        self.Maximize()
        self._mgr.Update()
        
        self.Bind(wx.EVT_MENU, self.OnOpenFile, id=wx.ID_OPEN)
        self.Bind(wx.EVT_CHOICE, self.OnChooseFile)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnTreeSelectionChange)
        self.filePicker.SetSelection(self.filePicker.FindString('linking-a-05-t'))
        self.OnChooseFile(None)
                
    def makeMenus(self):
        fileMenu = wx.Menu()
        fileMenu.Append(wx.ID_OPEN, "&Open\tCtrl-O")
        
        mb = wx.MenuBar()
        mb.Append(fileMenu, "&File")
        
        return mb

    def makeToolBar(self):
        tb = wx.ToolBar(self, style=wx.TB_FLAT)
        self.filePicker = wx.Choice(tb, choices=self.getFileList())
        tb.AddControl(self.filePicker)
        tb.Realize()
        return tb
    
    def getFileList(self):
        #look for the test files in the "compliance" dir next to our package
        files = os.listdir(self.getSVGDir())
        splitted = map(os.path.splitext, files)
        
        return sorted(fname for fname, ext in splitted)
    
    def getSVGDir(self):
        dir = os.path.dirname(document.__file__)
        dir = os.path.join(dir, "compliance", "svg")
        return dir
        
    def getPNGDir(self):
        dir = os.path.dirname(document.__file__)
        dir = os.path.join(dir, "compliance", "png")
        return dir
            
        
    
    def openFile(self, filenameOrBuffer):
        self.document = document.SVGDocument(filenameOrBuffer)
        self.tree.updateTree(self.document.tree)
        self.render.document = self.document
        self.Refresh()
    
    def OnChooseFile(self, evt):
        fname = self.filePicker.GetString(self.filePicker.GetSelection())
        if fname == '':
            return
        svg = os.path.join(self.getSVGDir(), fname+'.svg')
        self.openFile(svg)
        png = os.path.join(self.getPNGDir(), 'full-'+fname+'.png')
        self.reference.bmp = wx.Bitmap(png)
        
    def OnOpenFile(self, evt):
        dlg = wx.FileDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            self.openFile(dlg.GetPath())
    
    def OnTreeSelectionChange(self, evt):
        item = self.tree.GetSelection()
        element = self.tree.GetItemPyData(item)
        if element is None:
            return
        path = self.document.paths[element]
        print path
        
if __name__ == '__main__':
    app = wx.App(0)
    f = ViewFrame(None)
    f.Show()
    app.MainLoop()