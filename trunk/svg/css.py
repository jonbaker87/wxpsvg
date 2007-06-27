"""
    Parsing for CSS and CSS-style values, such as transform and filter attributes.
"""

from pyparsing import (Literal, Word, CaselessLiteral, 
    Optional, Combine, Forward, ZeroOrMore, nums, oneOf, Group, delimitedList)
    
#some shared definitions from pathdata

from pathdata import (digit_sequence, sign, exponent, 
    fractionalConstant, floatingPointConstant,
    integerConstant, number, comma)
    
paren = Literal("(").suppress()
cparen = Literal(")").suppress()

def Parenthised(exp):
    return Group(paren + exp + cparen)
    
skewY = Literal("skewY") + Parenthised(number)

skewX = Literal("skewX") + Parenthised(number)

rotate = Literal("rotate") + Parenthised(
    number + Optional(comma + number + comma + number)
)


scale = Literal("scale") + Parenthised(
    number + Optional(comma + number)
)

translate = Literal("translate") + Parenthised(
    number + Optional(comma + number)
)

matrix = Literal("matrix") + Parenthised(
    number + comma + number + comma + number + comma + number
)

transform = (skewY | skewX | rotate | scale | translate | matrix)

transformList = delimitedList(Group(transform), delim=comma)

if __name__ == '__main__':
    from tests.test_css import *
    unittest.main()