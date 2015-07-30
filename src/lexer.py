#!/usr/bin/env python2.7
import re

class Token(object):
    def __init__(self, value, line, pos, data):
        self._value = value
        self._line  = line
        self._pos   = pos
        self._data  = data

    def get_value(self):
        return self._value

    def get_pos(self):
        """ return the position in the line of the token"""
        return self._pos

    def get_line(self):
        """ return the line the token is on """
        return self._line

    def __repr__(self):
        return "{}<{}>".format(type(self).__name__, repr(self._value))

    def __eq__(self, other):
        if type(other) == type:
            return isinstance(self, other)
        return self._value == other

    def __ne__(self, other):
        return not self == other

    def highlight(self, context_above = 0, context_below = 0):
        assert context_above >= 0 and context_below >= 0
        out = ""
        lineno = self.get_line()
        lines = self._data.split("\n")
        pos  = self.get_pos()
        for line in lines[max(0, lineno - context_above):lineno]:
            out += line + "\n"
        out += lines[lineno] + "\n"
        out += " " * pos + "^" + "~" * (len(self._value) - 1) + "\n"
        for line in lines[lineno + 1:lineno + context_below + 1]:
            out += line + "\n"
        return out

class Keyword(Token): pass
class Number(Token): pass
class Integer(Number): pass
class Float(Number): pass
class LParen(Token): pass
class RParen(Token): pass
class LBrace(Token): pass
class RBrace(Token): pass
class LCurly(Token): pass
class RCurly(Token): pass
class Whitespace(Token): pass
class Comment(Token): pass
class LArrow(Token): pass
class RArrow(Token): pass
class Comma(Token): pass
class Colon(Token): pass
class Semicolon(Token): pass
class Period(Token): pass
class Newline(Whitespace):
    def __init__(self, value, line, pos, data):
        super(Whitespace, self).__init__("\n", line, pos, data)

class String(Token):
    def __init__(self, value, line, pos, data):
        super(String, self).__init__(value[1:-1], line, pos, data)

#Ops
class Op(Token): pass
class Add(Op): pass
class Sub(Op): pass
class Div(Op): pass
class Mult(Op): pass

#Comps
class Comp(Token): pass
class EQ(Comp): pass
class LTEQ(Comp): pass
class LT(Comp): pass
class GT(Comp): pass
class GTEQ(Comp): pass
class NEQ(Comp): pass

#Assignes
class AssignBase(Token): pass
class Assign(AssignBase): pass
class AddAssign(AssignBase): pass
class SubAssign(AssignBase): pass
class MultAssign(AssignBase): pass
class DivAssign(AssignBase): pass

keyword_list = (
    "and",
    "elif",
    "else",
    "for",
    "function",
    "if",
    "import",
    "or",
    "return",
    "while",
    "xor",
)

class Identifier(Token):
    def __new__(cls, value, line, pos, data):
        if value in keyword_list:
            return Keyword(value, line, pos, data)
        out = object.__new__(cls, value, line, pos, data)
        return out

token_dict = (
    (re.compile(r"^//.*\n"), Comment), #Remove comment first
    (re.compile(r"^\d*[.]\d+([eE]\d+)?") , Float),
    (re.compile(r"^(0[bB][01]+|0[xX][a-zA-Z0-9]+|\d+([eE]\d+)?)"), Integer),
    (re.compile(r"^[A-Za-z]\w*") , Identifier),
    (re.compile(r'"[^"]*"')      , String),
    (re.compile(r"^<-")          , LArrow),
    (re.compile(r"^->")          , RArrow),
    # Comp Ops
    (re.compile(r"^<=")  , LTEQ),
    (re.compile(r"^>=")  , GTEQ),
    (re.compile(r"^==")  , EQ),
    (re.compile(r"^!=")  , NEQ),
    (re.compile(r"^<")   , LT),
    (re.compile(r"^>")   , GT),
    #Assignes
    (re.compile(r"^:=")  , Assign),
    (re.compile(r"^\+=") , AddAssign),
    (re.compile(r"^\-=") , SubAssign),
    (re.compile(r"^\*=") , MultAssign),
    (re.compile(r"^/=")  , DivAssign),
    # Ops
    (re.compile(r"^\+")  , Add),
    (re.compile(r"^\-")  , Sub),
    (re.compile(r"^/")   , Div),
    (re.compile(r"^\*")  , Mult),
    # Braces
    (re.compile(r"^\(")  , LParen),
    (re.compile(r"^\)")  , RParen),
    (re.compile(r"^\[")  , LBrace),
    (re.compile(r"^\]")  , RBrace),
    (re.compile(r"^{")   , LCurly),
    (re.compile(r"^}")   , RCurly),
    #Singles
    (re.compile(r"^,")   , Comma),
    (re.compile(r"^:")   , Colon),
    (re.compile(r"^;")   , Semicolon),
    (re.compile(r"^\.")  , Period),
    #Whitespace
    (re.compile(r"^[ \t]+") , Whitespace),
    (re.compile(r"^\n+")    , Newline),
)

def set_line_pos(value, line, pos):
    linecount = value.count("\n")
    if linecount:
        line += linecount 
        pos = 0
    else:
        pos += len(value)
    return line, pos


def tokenise(data):
    pos    = 0
    line   = 0
    string = data
    while string:
        for pattern, token_type in token_dict:
            match = pattern.match(string)
            if match:
                value  = match.group(0)
                string = string[len(value):]
                if token_type not in (Whitespace, Comment):
                    yield token_type(value, line, pos, data)
                line, pos = set_line_pos(value, line, pos)
                break
        else:
            raise Exception("Lexing error:\n{}".format(string))

if __name__ == "__main__":
    import argparse
    import os
    from   os.path import join as pjoin
    filepath = os.path.dirname(os.path.realpath(__file__))
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--input", "-i",
                                 default = pjoin(filepath, "../tests/pass/simple_0.x"))
    args = argument_parser.parse_args()

    data = open(args.input).read()
    for x in tokenise(data):
        print(x)
