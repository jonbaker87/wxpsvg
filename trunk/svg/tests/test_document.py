import unittest
import svg.document as document
import wx

class TestCSSColor(unittest.TestCase):
    def setUp(self):
        #need an app for wx.TheColourDatabase
        app = wx.App(0)
    def testHex6Character(self):
        self.assertEqual(
            document.wxColourFromCSS("#010101"),
            wx.Colour(1, 1, 1)
        )
    def testHexNoLeadingMark(self):
        """ hex format with no # is a named colour and returns the null colour when
        not found"""
        self.assertEqual(
            document.wxColourFromCSS("ffffff"),
            wx.NullColour
        )
    def testHex3Character(self):
        result = document.wxColourFromCSS("#fab")
        self.assertEqual(
            result,
            wx.Colour(0xff, 0xaa, 0xbb)
        )
        