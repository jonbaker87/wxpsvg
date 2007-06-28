import os
import time
import pdb
from cStringIO import StringIO
import xml.etree.cElementTree as etree

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
        else:
            dc.DrawText(30,30, "No image available")



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
        self.lastRender = None
        self.document = document
        self.zoom = 100
        self.offset = wx.Point(0,0)
        #self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnWheel)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_MIDDLE_UP, self.OnMiddleClick)
        
    def OnPaint(self, evt):
        start = time.time()
        dc = wx.PaintDC(self)
        if not self.document:
            dc.DrawText("No Document", 20, 20)
            return
        gc = wx.GraphicsContext_Create(dc)
        scale = float(self.zoom) / 100.0
        
        gc.Translate(*self.offset)
        gc.Scale(scale, scale)
        
        self.document.render(gc)
        self.lastRender = time.time() - start
        
    def GetBestSize(self):
        if not self.document:
            return (-1,-1)
        sz = map(int,self.document.tree.getroot().get("viewBox").split())
        return wx.Rect(*sz).GetSize()
    
    def OnWheel(self, evt):
        self.zoom += (evt.m_wheelRotation / evt.m_wheelDelta) * 10
        self.Refresh()
    
    def OnLeftDown(self, evt):
        self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        self.CaptureMouse()
        self.offsetFrom = evt.GetPosition()
        evt.Skip()
    
    def OnLeftUp(self, evt):
        if self.HasCapture():
            self.ReleaseMouse()
        self.SetCursor(wx.NullCursor)
        evt.Skip()
        
    def OnMotion(self, evt):
        if not self.HasCapture():
            return
        self.offset += (evt.GetPosition() - self.offsetFrom)
        self.offsetFrom = evt.GetPosition()
        self.Refresh()
        
    def OnMiddleClick(self, evt):
        self.offset = wx.Point(0,0)
        self.zoom = 100
        self.Refresh()
            
        
    
        
    
class ViewFrame(wx.Frame):
    #status bar cell locations
    SCROLL_OFFSET = 0
    FILE = 1
    LOAD_TIME = 2
    RENDER_TIME = 3
    
    def __init__(self, parent):
        wx.Frame.__init__(self, parent)
        self._mgr = wx.aui.AuiManager()
        self._mgr.SetManagedWindow(self)
        
        self.wrap = wx.Panel(self)
        
        self.tree = XMLTree(self, None)
        self.render = RenderPanel(self.wrap)
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
        self.CreateStatusBar(5)
        self.Maximize()
        self._mgr.Update()
        
        self.Bind(wx.EVT_MENU, self.OnOpenFile, id=wx.ID_OPEN)
        self.Bind(wx.EVT_CHOICE, self.OnChooseFile)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnTreeSelectionChange)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI)
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
        start = time.time()
        tree = etree.parse(filenameOrBuffer)
        try:
            self.document = document.SVGDocument(tree.getroot())
            self.render.document = self.document
        except:
            #pdb.set_trace()
            import traceback
            self.render.document = None
            traceback.print_exc()
            
        amount = time.time() - start
        self.tree.updateTree(tree)
        self.SetStatusText("Loaded in %2f seconds" % amount, self.LOAD_TIME)
        self.SetStatusText(filenameOrBuffer)
        
        self.Refresh()
    
    def OnChooseFile(self, evt):
        fname = self.filePicker.GetString(self.filePicker.GetSelection())
        if fname == '':
            return
        svg = os.path.join(self.getSVGDir(), fname+'.svg')
        self.openFile(svg)
        png = os.path.join(self.getPNGDir(), 'full-'+fname+'.png')
        if os.path.isfile(png):
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
    def OnUpdateUI(self, evt):
        if self.render.lastRender is not None:
            self.SetStatusText("Rendered in %2f seconds" % self.render.lastRender, self.RENDER_TIME)
        
if __name__ == '__main__':
    app = wx.App(0)
    f = ViewFrame(None)
    f.Show()
    app.MainLoop()