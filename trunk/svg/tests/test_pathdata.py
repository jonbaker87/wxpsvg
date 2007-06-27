import unittest
from pyparsing import ParseException

from svg.pathdata import *

class TestParserPart(object):
    def testValid(self):
        for num in self.valid:
            self.assertEqual(
                float(num),
                self.parser.parseString(num)[0]
            )
    def testInvalid(self):
        for num in self.invalid:
            self.assertRaises(
                ParseException,
                lambda: self.parser.parseString(num)
            )
            
class TestFractionalConstant(unittest.TestCase, TestParserPart):
    parser = fractionalConstant
    valid = ['1.', '1.0', '0.1']
    invalid = ['.', '1', 'f']

class TestFPConstant(TestFractionalConstant):
    parser = floatingPointConstant
    valid = ['1.e10', '1e2', '1e+4', '1e-10']
    invalid = ['e10']

class TestNumber(unittest.TestCase, TestParserPart):
    parser = number
    valid = TestFPConstant.valid + TestFractionalConstant.valid + ['-10', '+10', '-1e10', '-1453.7e-6']
    invalid = ['', 'f']
    def testToFloat(self):
        for num in self.valid:
            parsed = self.parser.parseString(str(num))[0]
            self.assert_(float(parsed))

class TestCoords(unittest.TestCase):
    def testCoordPair(self):
        self.assertEqual(
            coordinatePair.parseString('100 100')[0],
            (100.0, 100.0)
        )
        self.assertEqual(
            coordinatePair.parseString('100,2E7')[0],
            (100,2e7)
        )

class TestMoveTo(unittest.TestCase):
    def testSimple(self):
        self.assertEqual(
            moveTo.parseString("M 100 100").asList()[0],
            ["M", [(100.0, 100.0)]]
        )
    def testLonger(self):
        self.assertEqual(
            moveTo.parseString("m 100 100 94 1e7").asList()[0],
            ["m", [(100.0, 100.0), (94, 1e7)]]
        )
    def testLine(self):
        self.assertEqual(
            lineTo.parseString("l 300 100").asList()[0],
            ["l", [(300.0, 100.0)]]
        )
    def testHorizonal(self):
        self.assertEqual(
            horizontalLine.parseString("H 100 5 20").asList()[0],
            ["H", [100.0, 5.0, 20.0]]
        )
    def testVertical(self):
        self.assertEqual(
            verticalLine.parseString("V 100 5 20").asList()[0],
            ["V", [100.0, 5.0, 20.0]]
        )
class TestEllipticalArc(unittest.TestCase):
    def testParse(self):
        self.assertEqual(
            ellipticalArc.parseString("a25,25 -30 0,1 50,-25").asList()[0],
            ["a", [[(25.0, 25.0), -30.0, (False,True), (50.0, -25.0)]]]
        )
class TestSmoothQuadraticBezierCurveto(unittest.TestCase):
    def testParse(self):
        self.assertEqual(
            smoothQuadraticBezierCurveto.parseString("t1000,300").asList()[0],
            ["t", [(1000.0, 300.0)]]
        )
class TestQuadraticBezierCurveto(unittest.TestCase):
    def testParse(self):
        self.assertEqual(
            quadraticBezierCurveto.parseString("Q1000,300 200 5").asList()[0],
            ["Q", [
                    [(1000.0, 300.0), (200.0,5.0)]
                ]
            ]
        )
class TestCurve(unittest.TestCase):
    def testParse(self):
        self.assertEqual(
            curve.parseString("C 100 200 300 400 500 600 100 200 300 400 500 600").asList()[0],
            ["C", [
                [(100.0,200.0), (300.0,400.0), (500.0, 600.0)],
                [(100.0,200.0), (300.0,400.0), (500.0, 600.0)]
                ]
            ]
            
        )
class TestClosePath(unittest.TestCase):
    def testParse(self):
        self.assertEqual(
            closePath.parseString('Z').asList()[0],
            ("Z", (None,))
        )

class TestSVG(unittest.TestCase):
    def testParse(self):
        path = 'M 100 100 L 300 100 L 200 300 z a 100,100 -4 0,1 25 25 z T300 1000 t40, 50 h4 42 2 2,1 v1,1,1 Z Q 34,10 1 1'
        r = svg.parseString(path)
        
        