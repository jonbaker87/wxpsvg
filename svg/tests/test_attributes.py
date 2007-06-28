import unittest
import svg.attributes as a

from .test_css import TestValueParser


class TestURLParser(unittest.TestCase):
    parser = a.url
    def testURL(self):
        self.assertEqual(
            self.parser.parseString("url(#someGradient)").asList(),
            ["URL", [('', '', '', '', "someGradient"), ()]]
        )
    def testURLWithFallback(self):
        self.assertEqual(
            self.parser.parseString("url(someGradient) red").asList(),
            ["URL", [('', '', "someGradient", '', ''), ['NAMED', (255,0,0)]]]
        )
    def testEmptyURL(self):
        self.assertEqual(
            self.parser.parseString("url() red").asList(),
            ["URL", [('', '', '', '', ''), ['NAMED', (255,0,0)]]]
        )
    def testxPointerURL(self):
        self.assertEqual(
            self.parser.parseString("url(#xpointer(idsomeGradient))").asList(),
            ["URL", [('', '', '', '', "xpointer(idsomeGradient)"), ()]]
        )
        
class TestPaintValue(TestValueParser):
    parser = a.paintValue
    def testNone(self):
        self.assertEqual(
            self.parser.parseString("none").asList(),
            ["NONE", ()]
        )
        
    def testCurrentColor(self):
        self.assertEqual(
            self.parser.parseString("currentColor").asList(),
            ["CURRENTCOLOR", ()]
        )