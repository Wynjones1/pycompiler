#!/usr/bin/env python2.7
import os
from parse import *

class TempVar(object):
    def __init__(self, value):
        self._value = value

    def __str__(self):
        return "_t{}".format(self._value)

class Label(object):
    def __init__(self, value):
        self._value = value

    def __str__(self):
        return "L{}:".format(self._value)

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
        return Label(out)
        
class TAC:
    def __str__(self):
        raise NotImplementedError("{}".format(self.__class__.__name__))

class Argument(TAC):
    def __init__(self, type, identifier):
        self._type = type
        self._identifier = identifier

    def __str__(self):
        return "arg {} {}".format(self._type, self._identifier)

class FuncCall(TAC):
    def __init__(self, identifier):
        self._identifier = identifier

    def __str__(self):
        return "CALL {}".format(self._identifier)

class Param(TAC):
    def __init__(self, value):
        self._value = value

    def __str__(self):
        return "param {}".format(self._value)

class StartFunc(TAC):
    def __init__(self, identifier, symbol_table):
        self._identifier = identifier
        self._symbol_table = symbol_table

    def __str__(self):
        return "startfunc {}".format(self._identifier)

class EndFunc(TAC):
    def __init__(self, identifier):
        self._identifier = identifier

    def __str__(self):
        return "endfunc {}".format(self._identifier)

class Assign(TAC):
    def __init__(self, identifier, var):
        self._identifier = identifier
        self._var        = var

    def __str__(self):
        return ":= {} {}".format(self._identifier, self._var)

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

class JP(TAC):
    def __init__(self, label):
        self._label = label

    def __str__(self):
        return "JP {}".format(self._label)

class JNZ(TAC):
    def __init__(self, label, var):
        self._label = label
        self._var   = var

    def __str__(self):
        return "JNZ {} {}".format(self._label, self._var)

class JZ(TAC):
    def __init__(self, label, var):
        self._label = label
        self._var   = var

    def __str__(self):
        return "JZ {} {}".format(self._label, self._var)

class Load(TAC):
    def __init__(self, dest, source):
        self._dest = dest
        self._source = source

    def __str__(self):
        return "Load {} {}".format(self._dest, self._source)

class Store(TAC):
    def __init__(self, dest, source):
        self._dest = dest
        self._source = source

    def __str__(self):
        return "Store {} {}".format(self._dest, self._source)

def make_tac(input):
    try:
        prog = parse(input)
        prog.make_tables()
        prog.sema()
        return prog.make_tac(TacState())
    except ast.SemaError as e:
        raise
    except KeyError as e:
        raise

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
