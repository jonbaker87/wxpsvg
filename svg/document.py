import pdb
"""
    SVGDocument
"""
import wx
import xml.etree.cElementTree as etree
from cStringIO import StringIO
import warnings
import math

import pathdata
import css
from colour import FindColour, rgb

document = """<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" 
  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="4cm" height="4cm" viewBox="0 0 400 400"
     xmlns="http://www.w3.org/2000/svg" version="1.1">
  <title>Example triangle01- simple example of a 'path'</title>
  <desc>A path that draws a triangle</desc>
  <rect x="1" y="1" width="398" height="398"
        fill="none" stroke="blue" />
  <path d="M 100 100 L 300 100 L 200 300 z"
        fill="red" stroke="blue" stroke-width="3" />
</svg>"""

#~ document1 = """<?xml version="1.0" standalone="no"?>
#~ <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" 
  #~ "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
#~ <svg width="4cm" height="4cm" viewBox="0 0 400 400"
     #~ xmlns="http://www.w3.org/2000/svg" version="1.1">
  #~ <title>Example triangle01- simple example of a 'path'</title>
  #~ <desc>A path that draws a triangle</desc>
  #~ <rect x="1" y="1" width="398" height="398"
        #~ fill="none" stroke="blue" />
  #~ <path class="SamplePath" d="M100,200 C 175,0,325,0,400,200
                                       #~ " />
#~ </svg>"""


makePath = lambda: wx.GraphicsRenderer_GetDefaultRenderer().CreatePath()

def attrAsFloat(node, attr):
        try:
            return float(node.get(attr, 0))
        except TypeError:
            return float(0)

def wxColourFromCSS(scolor):
    #note: CSS spec only has 17 named colors + system colors,
    #but seems to permit adding arbitrary named colors
    #TODO: need to return a false value for unknown colors
    scolor = scolor.strip()
    named = FindColour(scolor)
    if named:
        return named
    if scolor.startswith("#"):
        scolor = scolor[1:]
        if len(scolor) == 6:
            r = int(scolor[0:2], 16)
            g = int(scolor[2:4], 16)
            b = int(scolor[4:6], 16)
            return wx.Colour(r,g,b)
        elif len(scolor) == 3:
            #3 character for is made by doubling each
            #character, as per CSS 2.1 spec, section 4.3.6
            #hence fab becomes ffaabb
            r, g, b = map(lambda x: int(x*2, 16), scolor)
            return wx.Colour(r,g,b)
        else:
            warnings.warn("invalid color value: %s" % scolor)
    elif scolor.startswith("rgb"):
        r, g, b = rgb.parseString(scolor)
        return wx.Colour(r,g,b)
    warnings.warn("No valid colour found? "+scolor)
    return wx.NullColour
        

def pathHandler(func):
    #decorator for methods which return a path operation
    def inner(self, node):
        path = wx.GraphicsRenderer_GetDefaultRenderer().CreatePath()
        func(self, node, path)
        ops = self.generatePathOps(path)
        return path, ops
    return inner
        

class SVGDocument(object):
    lastControl = None
    def __init__(self, xmlbuffer):
        """
            Create an SVG document from an xml description
            
        """
        self.handlers = {
            '{http://www.w3.org/2000/svg}svg':self.addGroupToDocument,
            '{http://www.w3.org/2000/svg}a':self.addGroupToDocument,
            '{http://www.w3.org/2000/svg}g':self.addGroupToDocument,
            '{http://www.w3.org/2000/svg}rect':self.addRectToDocument,
            '{http://www.w3.org/2000/svg}circle': self.addCircleToDocument,
            '{http://www.w3.org/2000/svg}ellipse': self.addEllipseToDocument,
            '{http://www.w3.org/2000/svg}line': self.addLineToDocument,
            '{http://www.w3.org/2000/svg}polyline': self.addPolyLineToDocument,
            '{http://www.w3.org/2000/svg}polygon': self.addPolygonToDocument,
            '{http://www.w3.org/2000/svg}path':self.addPathDataToDocument,
            '{http://www.w3.org/2000/svg}text':self.addTextToDocument
        }
        self.tree = etree.parse(xmlbuffer)
        self.paths = {}
        self.stateStack = [{}]
        try:
            path, ops = self.processElement(self.tree.getroot())
            self.ops = ops
        except:
            import traceback
            traceback.print_exc()
        
        
        
    @property
    def state(self):
        return self.stateStack[-1]
        
    def processElement(self, element):
        current = dict(self.state)
        current.update(element.items())
        current.update(css.inlineStyle(element.get("style", "")))
        self.stateStack.append(current)
        handler = self.handlers.get(element.tag, lambda *any: (None, None))        
        path, ops = handler(element)
        self.paths[element] = path
        self.stateStack.pop()
        return path, ops

    def createTransformOpsFromNode(self, node):
        """ Returns an oplist for transformations.
        This applies to a node, not the current state because
        the transform stack is saved in the wxGraphicsContext.
        
        This oplist does *not* include the push/pop state commands
        """
        ops = []
        transform = node.get('transform')
        if transform:
            for transform, args in css.transformList.parseString(transform):
                if transform == 'scale':
                    if len(args) == 1:
                        x = y = args[0]
                    else:
                        x, y = args
                    ops.append(
                        (wx.GraphicsContext.Scale, (x, y))
                    )
                if transform == 'translate':
                    if len(args) == 1:
                        x = args[0]
                        y = 0
                    else:
                        x, y = args
                    ops.append(
                        (wx.GraphicsContext.Translate, (x, y))
                    )
                if transform == 'rotate':
                    if len(args) == 3:
                        angle, cx, cy = args
                        angle = math.radians(angle)
                        ops.extend([
                            (wx.GraphicsContext.Translate, (cx, cy)),
                            (wx.GraphicsContext.Rotate, (angle,)),
                            (wx.GraphicsContext.Translate, (-cx, -cy)),
                        ])
                    else:
                        angle = args[0]
                        angle = math.radians(angle)
                        ops.append(
                            (wx.GraphicsContext.Rotate, (angle,))
                        )
                if transform == 'matrix':
                    matrix = wx.GraphicsRenderer_GetDefaultRenderer().CreateMatrix(
                        *args
                    )
                    ops.append(
                        (wx.GraphicsContext.ConcatTransform, (matrix,))
                    )
                if transform == 'skewX':
                    matrix = wx.GraphicsRenderer_GetDefaultRenderer().CreateMatrix(
                        1,0,math.tan(math.radians(args[0])),1,0,0
                    )
                    ops.append(
                        (wx.GraphicsContext.ConcatTransform, (matrix,))
                    )
                if transform == 'skewY':
                    matrix = wx.GraphicsRenderer_GetDefaultRenderer().CreateMatrix(
                        1,math.tan(math.radians(args[0])),0,1,0,0
                    )
                    ops.append(
                        (wx.GraphicsContext.ConcatTransform, (matrix,))
                    )
                    
        return ops
        
    
    def addGroupToDocument(self, node):
        ops = [
            (wx.GraphicsContext.PushState, ())
        ]
        
        path = makePath()
        ops.extend(self.createTransformOpsFromNode(node))
        for child in node.getchildren():
            cpath, cops = self.processElement(child)
            if cpath:
                path.AddPath(cpath)
            if cops:
                ops.extend(cops)
        ops.append(
            (wx.GraphicsContext.PopState, ())
        )
        return path, ops
        
            
        
    def getFontFromState(self):
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        family = self.state.get("font-family")
        if family:
            font.SetFaceName(family)
        size = self.state.get("font-size")
        if size:
            font.SetPixelSize(wx.Size(int(size), int(size)))
        return font
    
    def addTextToDocument(self, node):
        x, y = [attrAsFloat(node, attr) for attr in ('x', 'y')]
        
        def DoDrawText(context, text, x, y):
            #SVG spec appears to originate text from the bottom
            #rather than the top as with our API. This function
            #will measure and then re-orient the text as needed.
            w, h = context.GetTextExtent(text)
            y -= h
            context.DrawText(text, x, y)
        font = self.getFontFromState()
        brush = self.getBrushFromState()
        text = node.text
        ops = [
            (wx.GraphicsContext.SetFont, (font,)),
            (wx.GraphicsContext.SetBrush, (brush,)),
            (DoDrawText, (text, x, y))
        ]
        return None, ops
        
    @pathHandler
    def addRectToDocument(self, node, path):
        x, y, width, height = (attrAsFloat(node, attr) for attr in ['x', 'y', 'width', 'height'])
        rx = node.get('rx')
        ry = node.get('ry')
        if rx or ry:
            if rx and ry:
                rx, ry = float(rx), float(ry)
            elif rx:
                rx = ry = float(rx)
            elif ry:
                rx = ry = float(ry)
            ##TODO: This is totally wrong. Re-implement in terms
            ##of paths once Arc is implemented reasonably
            path.AddRoundedRectangle(x,y,width,height,rx)
            
        else:
            path.AddRectangle(
                x, y, width, height
            )
    
    @pathHandler
    def addCircleToDocument(self, node, path):
        cx, cy, r = [float(node.get(attr, 0)) for attr in ('cx', 'cy', 'r')]
        path.AddCircle(cx, cy, r)
        
    @pathHandler
    def addEllipseToDocument(self, node, path):
        cx, cy, rx, ry = [float(node.get(attr, 0)) for attr in ('cx', 'cy', 'rx', 'ry')]
        #cx, cy are centerpoint.
        #rx, ry are radius.
        #wxGC coords are the rect of the ellipse bounding box.
        if rx <= 0 or ry <= 0:
            return
        x = cx - rx
        y = cy - ry
        path.AddEllipse(x, y, rx*2, ry*2)
    
    @pathHandler            
    def addLineToDocument(self, node, path):
        x1, y1, x2, y2 = [float(node.get(attr, 0)) for attr in ('x1', 'y1', 'x2', 'y2')]
        path.MoveToPoint(x1, y1)
        path.AddLineToPoint(x2, y2)
        
    @pathHandler
    def addPolyLineToDocument(self, node, path):
        #translate to pathdata and render that
        data = "M " + node.get("points")
        self.addPathDataToPath(data, path)
    
    @pathHandler    
    def addPolygonToDocument(self, node, path):
        #translate to pathdata and render that
        data = "M " + node.get("points") + " Z"
        self.addPathDataToPath(data, path)
        
    @pathHandler
    def addPathDataToDocument(self, node, path):
        self.addPathDataToPath(node.get('d', ''), path)
    
    def addPathDataToPath(self, data, path):
        self.lastControl = None
        self.lastControlQ = None
        self.firstPoints = []
        def normalizeStrokes(parseResults):
            for command, arguments in parseResults:
                if not arguments:
                    yield (command, ())
                else:
                    arguments = iter(arguments)
                    if command ==  'm':
                        yield (command, arguments.next())
                        command = "l"
                    elif command == "M":
                        yield (command, arguments.next())
                        command = "L"
                    for arg in arguments:
                        yield (command, arg)
        for stroke in normalizeStrokes(pathdata.svg.parseString(data)):  
            self.addStrokeToPath(path, stroke)
        
    def generatePathOps(self, path):
        ops = []
        brush = self.getBrushFromState()
        fillRule = self.state.get('fill-rule', 'nonzero')
        frMap = {'nonzero':wx.WINDING_RULE, 'evenodd': wx.ODDEVEN_RULE}
        fr = frMap.get(fillRule, wx.ODDEVEN_RULE)
        if brush:
            ops.append(
                (wx.GraphicsContext.SetBrush, (brush,))
            )
            ops.append(
                (wx.GraphicsContext.FillPath, (path, fr))
            )
            
        pen = self.getPenFromState()
        if pen:
            ops.append(
                    (wx.GraphicsContext.SetPen, (pen,))
                )
            ops.append(
                (wx.GraphicsContext.StrokePath, (path,))
            )
        return ops
        
    def getPenFromState(self):
        pencolour = self.state.get('stroke', 'none')
        if not pencolour or pencolour == 'none':
            return wx.NullPen
        pen = wx.Pen(wxColourFromCSS(pencolour))
        width = self.state.get('stroke-width')
        if width:
            pen.SetWidth(float(width))
        capmap = {
            'butt':wx.CAP_BUTT,
            'round':wx.CAP_ROUND,
            'square':wx.CAP_PROJECTING
        }
        joinmap = {
            'miter':wx.JOIN_MITER,
            'round':wx.JOIN_ROUND,
            'bevel':wx.JOIN_BEVEL
        }
        pen.SetCap(capmap.get(self.state.get('stroke-linecap', None), wx.CAP_BUTT))
        pen.SetJoin(joinmap.get(self.state.get('stroke-linejoin', None), wx.JOIN_MITER))
        return wx.GraphicsRenderer_GetDefaultRenderer().CreatePen(pen)
            
    def getBrushFromState(self):
        brushcolour = self.state.get('fill', 'none')
        if brushcolour == 'currentColor':
            brushcolour = self.state.get('color', 'none')
        if brushcolour == 'none':
            return wx.NullBrush
        brushcolour = wxColourFromCSS(brushcolour)
        return wx.GraphicsRenderer_GetDefaultRenderer().CreateBrush(
            wx.Brush(brushcolour)
        )
        
    def addStrokeToPath(self, path, stroke):
        type, arg = stroke
        relative = False
        if type == type.lower():
            relative = True
            ox, oy = path.GetCurrentPoint().Get()
        else:
            ox = oy = 0
        def normalizePoint(arg):
            x, y = arg
            return x+ox, y+oy
        def reflectPoint(point, relativeTo):
            x, y = point
            a, b = relativeTo
            return ((a*2)-x), ((b*2)-y)
        type = type.upper()
        if type == 'M':
            pt = normalizePoint(arg)
            self.firstPoints.append(pt)
            path.MoveToPoint(pt)
            #~ if relative:
                #~ self.addStrokeToPath(path, ("l", args[1:]))
            #~ else:
                #~ self.addStrokeToPath(path, ("L", args[1:]))
        elif type == 'L':
            path.AddLineToPoint(normalizePoint(arg))
        elif type == 'C':
            #control1, control2, endpoint = arg
            control1, control2, endpoint = map(
                normalizePoint, arg
            )
            self.lastControl = control2
            path.AddCurveToPoint(
                control1, 
                control2, 
                endpoint
            )
            #~ cp = path.GetCurrentPoint()
            #~ path.AddCircle(c1x, c1y, 5)
            #~ path.AddCircle(c2x, c2y, 3)
            #~ path.AddCircle(x,y, 7)
            #~ path.MoveToPoint(cp)
            #~ print "C", control1, control2, endpoint
        
        elif type == 'S':
            #control2, endpoint = arg
            control2, endpoint = map(
                normalizePoint, arg
            )
            if self.lastControl:
                control1 = reflectPoint(self.lastControl, path.GetCurrentPoint())
            else:
                control1 = path.GetCurrentPoint()
            #~ print "S", self.lastControl,":",control1, control2, endpoint    
            self.lastControl = control2
            path.AddCurveToPoint(
                control1, 
                control2, 
                endpoint
            )
        elif type == "Q":
            (cx, cy), (x,y) = map(normalizePoint, arg)
            self.lastControlQ = (cx, cy)
            path.AddQuadCurveToPoint(cx, cy, x, y)
        elif type == "T":
            x, y, = normalizePoint(arg)
            if self.lastControlQ:
                cx, cy = reflectPoint(self.lastControlQ, path.GetCurrentPoint())
            else:
                cx, cy = path.GetCurrentPoint()
            self.lastControlQ = (cx, cy)
            path.AddQuadCurveToPoint(cx, cy, x, y)
                
        elif type == "V":
            _, y = normalizePoint((0, arg))
            x, _ = path.GetCurrentPoint()
            path.AddLineToPoint(x,y)
        
        elif type == "H":
            x, _ = normalizePoint((arg, 0))
            _, y = path.GetCurrentPoint()
            path.AddLineToPoint(x,y)
            
        elif type == "A":
            #wxGC currently only supports circular arcs,
            #not eliptical ones
            
            #angle is *in degrees*
            ((rx, ry), #radii of ellipse
            angle, #angle of rotation on the ellipse
            (fa, fs), #arc and stroke angle flags
            (x, y)) = arg #endpoint on the arc
            
            x, y = normalizePoint((x,y))
            cx, cy = path.GetCurrentPoint()
            if (cx, cy) == (x, y):
                return #noop
                
            if (rx == 0 or ry == 0):
                #no radius is effectively a line
                path.AddLineToPoint(x,y)
                return
            
            #find the center point for the ellipse
            #translation via the angle
            angle = angle % 360
            angle = math.radians(angle)
            
            #translated endpoint
            xPrime = math.cos(angle) * ((cx-x)/2)
            xPrime += math.sin(angle) * ((cx-x)/2)
            yPrime = -(math.sin(angle)) * ((cy-y)/2)
            yPrime += (math.cos(angle)) * ((cy-y)/2)
            
            
            temp = ((rx**2) * (ry**2)) - ((rx**2) * (yPrime**2)) - ((ry**2) * (xPrime**2))
            temp /= ((rx**2) * (yPrime**2)) + ((ry**2)*(xPrime**2))
            temp = math.sqrt(temp)
            cxPrime = temp * ((rx * yPrime) / ry)
            cyPrime = temp * -((ry * xPrime) / rx)
            if fa == fs:
                cxPrime, cyPrime = -cxPrime, -cyPrime
            
            #reflect backwards now for the origin
            cnx = math.cos(angle) * cxPrime
            cnx += math.sin(angle) * cxPrime
            cny = -(math.sin(angle)) * cyPrime
            cny += (math.cos(angle)) * cyPrime
            cnx += ((cx+x)/2.0)
            cny += ((cy+y)/2.0)
            
            #calculate the angle between the two endpoints
            lastArc = wx.Point2D(x-cnx, y-cny).GetVectorAngle()
            firstArc = wx.Point2D(cx-cnx, cy-cny).GetVectorAngle()
            lastArc = math.radians(lastArc)
            firstArc = math.radians(firstArc)
            
            
            #aargh buggines.
            #AddArc draws a straight line between
            #the endpoints of the arc.
            #putting it in a subpath makes the strokes come out 
            #correctly, but it still only fills the slice
            #taking out the MoveToPoint fills correctly.
            npath = makePath()
            if rx == ry:
                npath.AddArc(cnx, cny, rx, firstArc, lastArc, False)
            else:
                warnings.warn("elliptical arcs not supported")
            path.AddPath(npath)
            #npath.MoveToPoint(x,y)
            
            
        elif type == 'Z':
            #~ Bugginess:
            #~ CloseSubpath() doesn't change the
            #~ current point, as SVG spec requires.
            #~ However, manually moving to the endpoint afterward opens a new subpath
            #~ and (apparently) messes with stroked but not filled paths.
            #~ This is possibly a bug in GDI+?
            #~ Manually closing the path via AddLineTo gives incorrect line join
            #~ results
            #~ Manually closing the path *and* calling CloseSubpath() appears
            #~ to give correct results on win32
                
            pt = self.firstPoints.pop()
            path.AddLineToPoint(pt)
            path.CloseSubpath()
                
    def render(self, context):
        if not hasattr(self, "ops"):
            return
        for op, args in self.ops:
            op(context, *args)
            
if __name__ == '__main__':
    from tests.test_document import *
    unittest.main()