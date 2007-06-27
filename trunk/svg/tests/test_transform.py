import unittest
from pyparsing import ParseException
from svg.css.transform import *

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

class TestCSSParsing(unittest.TestCase):
    def testTestsGood(self):
        for parser, string, result in transformTestsGood:
            self.assertEqual(
                parser.parseString(string).asList(),
                result
            )
    def testTestsError(self):
        for parser, string in transformTestsError:
            self.assertRaises(
                ParseException,
                parser.parseString,
                string
            )
class TestTransform(unittest.TestCase):
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
        
        
        
        