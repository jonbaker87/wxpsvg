import unittest
from pyparsing import ParseException

from svg.css.transform import *
import svg.css.colour as colour

#list of tuples: parser, string, result
transformTestsGood = [
    (skewY, "skewY(10)",            ["skewY", [10]]),
    (skewX, "skewX(10)",            ["skewX", [10]]),
    (rotate, "rotate(90)",          ["rotate", [90]]),
    (rotate, "rotate(90, 10 10)",   ["rotate", [90,10,10]]),
]

#parse, string - exception is always ParseException
transformTestsError = [
    (skewY, "skewY 10"),
    (skewX, "skewX (45"),
    (rotate, "rotate"),
]

class TestTransformParser(unittest.TestCase):
    def testTransformList(self):
        self.assertEqual(
            transformList.parseString(
                "matrix(1,2,3,4) translate(-10), scale(23, 45.9)"
            ).asList(),
            [
                ["matrix", [1,2,3,4]],
                ["translate", [-10]],
                ["scale", [23, 45.9]]
            ]
        )
    def testTransformGood(self):
        for parser, string, result in transformTestsGood:
            self.assertEqual(
                transform.parseString(string).asList(),
                result
            )
    def testTransformError(self):
        for parser, string in transformTestsError:
            self.assertRaises(
                ParseException,
                transform.parseString,
                string
            ) 
    def testPartsGood(self):
        for parser, string, result in transformTestsGood:
            self.assertEqual(
                parser.parseString(string).asList(),
                result
            )
    def testPartsError(self):
        for parser, string in transformTestsError:
            self.assertRaises(
                ParseException,
                parser.parseString,
                string
            )

    
            
class testColourValueClamping(unittest.TestCase):
    def testByte(self):
        self.assertEqual(
            100,
            colour.clampColourByte(100)
        )
        self.assertEqual(
            0,
            colour.clampColourByte(-100)
        )
        self.assertEqual(
            255,
            colour.clampColourByte(300)
        )
        
class testRGBParsing(unittest.TestCase):
    parser = colour.rgb
    def testRGBByte(self):
        self.assertEqual(
            self.parser.parseString("rgb(300,45,100)").asList(),
            ["RGB", [255,45,100]]
        )
    def testRGBPerc(self):
        self.assertEqual(
            self.parser.parseString("rgb(100%,0%,0.1%)").asList(),
            ["RGB", [255,0,0]]
        )
        
class testHexParsing(unittest.TestCase):
    parser = colour.hexLiteral
    def testHexLiteralShort(self):
        self.assertEqual(
            self.parser.parseString("#fab").asList(),
            ["RGB", (0xff, 0xaa, 0xbb)]
        )
    def testHexLiteralLong(self):
        self.assertEqual(
            self.parser.parseString("#f0a1b2").asList(),
            ["RGB", [0xf0, 0xa1, 0xb2]]
        )
    def testHexLiteralBroken(self):
        self.assertRaises(
            ParseException,
            self.parser.parseString,
            "#fab0"
        )
        self.assertRaises(
            ParseException,
            self.parser.parseString,
            "#fab0102d"
        )
        self.assertRaises(
            ParseException,
            self.parser.parseString,
            "#gab"
        )

class TestNamedColours(unittest.TestCase):
    parser = colour.namedColour
    def testNamedColour(self):
        self.assertEqual(
            self.parser.parseString("fuchsia").asList(),
            ["NAMED", (0xFF, 0, 0xFF)]
        )
class TestURLColour(unittest.TestCase):
    parser = colour.url
    def testURL(self):
        self.assertEqual(
            self.parser.parseString("url(#someGradient)").asList(),
            ["URL", ('', '', '', '', "someGradient")]
        )
        
class TestValueParserNamed(TestNamedColours):
    parser = colour.colourValue
        
    
    
    