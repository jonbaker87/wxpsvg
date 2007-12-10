"""

"""

import wx

def AddEllipticalArc(self, x, y, w, h, startAngle, endAngle, clockwise=False):
    """ Draws an arc of an ellipse within bounding rect (x,y,w,h) 
    from startArc to endArc (in radians, relative to the horizontal line of the eclipse)"""
    
    #implement in terms of AddArc by applying a transformation matrix
    mtx = wx.GraphicsRenderer_GetDefaultRenderer().CreateMatrix()
    path = wx.GraphicsRenderer_GetDefaultRenderer().CreatePath()
    mtx.Translate(x+w/2.0, y+h/2.0)
    mtx.Scale(w/2.0, y/2.0)
    
    path.AddArc(0, 0, 1, startAngle, endAngle, clockwise)
    path.Transform(mtx)
    self.AddPath(path)
    self.MoveToPoint(path.GetCurrentPoint())
    self.CloseSubpath()
    
if not hasattr(wx.GraphicsPath, "AddEllipticalArc"):
    wx.GraphicsPath.AddEllipticalArc = AddEllipticalArc

del AddEllipticalArc
    