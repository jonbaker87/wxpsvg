"""
Parser for various kinds of CSS values as per CSS2 spec section 4.3
"""
from pyparsing import Word, Combine, Optional, Literal, oneOf, CaselessLiteral

def asInt(s,l,t):
    return int(t[0])
    
def asFloat(s,l,t):
    return float(t[0])
    
def asFloatOrInt(s,l,t):
    """ Return an int if possible, otherwise a float"""
    v = t[0]
    try:
        return int(v)
    except ValueError:
        return float(v)

integer = Word("0123456789").setParseAction(asInt)

number = Combine(
    Optional(Word("0123456789")) + Literal(".") + Word("01234567890")
    | integer
)


sign = oneOf("+ -")

signedNumber = Combine(Optional(sign) + number).setParseAction(asFloat)

lengthValue = Combine(Optional(sign) + number).setParseAction(asFloatOrInt)

#TODO: The physical units like in, mm
lengthUnit = CaselessLiteral("em") | CaselessLiteral("ex") | CaselessLiteral("px")
#percentags
lengthUnit |= CaselessLiteral("%")

#the spec says that the unit is only optional for a 0 length, but
#there are just too many places where a default is permitted.
#TODO: Maybe should use a ctor like optional to let clients declare it?
length = lengthValue + Optional(lengthUnit, default=None)

#set the parse action aftward so it doesn't "infect" the parsers that build on it
number.setParseAction(asFloat)