#!/usr/bin/env python2.7
import os
from parse import *

class TempVar(object):
    def __init__(self, value):
        self._value = value

    def __str__(self):
        return "_t{}".format(self._value)

class TacState(object):
    def __init__(self):
        self._label_count = 0
        self._last_var    = None
        self._temp_count  = 0

    def last_var(self):
        assert self._last_var != None
        return self._last_var

    def set_var(self, var):
        self._last_var = var

    def make_temp(self):
        out = self._temp_count
        self._temp_count += 1
        self._last_var = TempVar(out)
        return self._last_var

    def make_label(self):
        out = self._label_count
        self._label_count += 1
        return out
        
class TAC:
    def __str__(self):
        raise NotImplementedError()

class Param(TAC):
    def __init__(self, type, identifier):
        self._type = type
        self._identifier = identifier

    def __str__(self):
        return "param {} {}".format(self._type, self._identifier)

class StartFunc(TAC):
    def __init__(self, identifier):
        self._identifier = identifier

    def __str__(self):
        return "startfunc {}".format(self._identifier)
class EndFunc(TAC):
    def __init__(self, identifier):
        self._identifier = identifier

    def __str__(self):
        return "endfunc {}".format(self._identifier)

class Assign(TAC): pass

class Op(TAC):
    def __init__(self, op, assign, lhs, rhs):
        self._op     = op
        self._assign = assign
        self._lhs    = lhs
        self._rhs    = rhs

    def __str__(self):
        return "{} {} {} {}".format(self._op, self._assign,
                                    self._lhs, self._rhs)

class Return(TAC):
    def __init__(self, value):
        self._value = value

    def __str__(self):
        return "return {}".format(self._value if self._value else "")

if __name__ == "__main__":
    test = """
    function a()
    {
        while(a < 10)
        {
            b := 10 + 10
        }
    }
    """
    prog = parse(test)
    prog.make_tac(TacState())

    """
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--input", "-i",
                                 default = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                        "tests", "lang", "simple_0.x"))
    args = argument_parser.parse_args()

    data = open(args.input).read()
    program = parse(data)
    """
