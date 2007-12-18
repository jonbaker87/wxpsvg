import unittest
from svg.css import block

class TestBlockParsing(unittest.TestCase):
    def testBlock(self):
        """ Not a valid CSS statement, but a valid block"""
        self.assertEqual(
            ["causta:", '"}"', "+", "(", ["7"], "*", "'", ")"],
            block.block.parseString("""{ causta: "}" + ({7} * '\'') }""").asList()
        )