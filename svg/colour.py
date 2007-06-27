"""
    CSS colour values
"""
import wx
import string
from pyparsing import Literal
from .pathdata import integerConstant

#rgb format parser
comma = Literal(",").suppress()
rgb = Literal("rgb(").suppress() + integerConstant + comma + integerConstant + comma + integerConstant + Literal(")").suppress()

NamedColours = {
    #html named colours
    "black":(0,0,0),
    "silver": (0xc0, 0xc0, 0xc0),
    "gray": (0x80, 0x80, 0x80),
    "white":(255,255,255),
    "maroon":(0x80, 0, 0),
    "red":(0xff, 0, 0),
    "purple":(0x80, 0, 0x80),
    "fuchsia":(0xff, 0, 0xff),
    "green": (0, 0x80, 0),
    "lime": (0, 0xff, 0),
    "olive": (0x80, 0x80, 00),
    "yellow":(0xff, 0xff, 00),
    "navy": (0, 0, 0x80),
    "blue": (0, 0, 0xff),
    "teal": (0, 0x80, 0x80),
    "aqua": (0, 0xff, 0xff),
    "none": (-1, -1, -1),
    "transparent": (0,0,0,0)
}

def FindColour(name):
    #early out
    if name.startswith("rgb"):
        return False
    if name.startswith("#"):
        return wx.NullColour
    try:
        return wx.Colour(*NamedColours[name.lower()])
    except KeyError:
        return wx.NullColour