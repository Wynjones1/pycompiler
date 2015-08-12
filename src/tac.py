#!/usr/bin/env python2.7
import os
from parse import *

class TempVar(object):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "_t{}".format(self.value)

class Label(object):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "L{}:".format(self.value)

class TacState(object):
    def __init__(self):
        self.label_count = 0
        self._last_var    = None
        self.temp_count  = 0

    def last_var(self):
        assert self._last_var != None
        return self._last_var

    def set_var(self, var):
        self._last_var = var

    def make_temp(self):
        out = self.temp_count
        self.temp_count += 1
        self._last_var = TempVar(out)
        return self._last_var

    def make_label(self):
        out = self.label_count
        self.label_count += 1
        return Label(out)
        
class TAC:
    def __str__(self):
        raise NotImplementedError("{}".format(self.__class__.__name__))

class Argument(TAC):
    def __init__(self, type, identifier):
        self.type = type
        self.identifier = identifier

    def __str__(self):
        return "arg {} {}".format(self.type, self.identifier)

class FuncCall(TAC):
    def __init__(self, identifier):
        self.identifier = identifier

    def __str__(self):
        return "CALL {}".format(self.identifier)

class Param(TAC):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "param {}".format(self.value)

class StartFunc(TAC):
    def __init__(self, identifier, symbol_table):
        self.identifier = identifier
        self.symbol_table = symbol_table

    def __str__(self):
        return "startfunc {}".format(self.identifier)

class EndFunc(TAC):
    def __init__(self, identifier):
        self.identifier = identifier

    def __str__(self):
        return "endfunc {}".format(self.identifier)

class Assign(TAC):
    def __init__(self, identifier, var):
        self.identifier = identifier
        self.var        = var

    def __str__(self):
        return ":= {} {}".format(self.identifier, self.var)

class Op(TAC):
    def __init__(self, op, assign, lhs, rhs):
        self.op     = op
        self.assign = assign
        self.lhs    = lhs
        self.rhs    = rhs

    def __str__(self):
        return "{} {} {} {}".format(self.op, self.assign,
                                    self.lhs, self.rhs)

class Return(TAC):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "return {}".format(self.value if self.value else "")

class JP(TAC):
    def __init__(self, label):
        self.label = label

    def __str__(self):
        return "JP {}".format(self.label)

class JNZ(TAC):
    def __init__(self, label, var):
        self.label = label
        self.var   = var

    def __str__(self):
        return "JNZ {} {}".format(self.label, self.var)

class JZ(TAC):
    def __init__(self, label, var):
        self.label = label
        self.var   = var

    def __str__(self):
        return "JZ {} {}".format(self.label, self.var)

class Load(TAC):
    def __init__(self, dest, source):
        self.dest = dest
        self.source = source

    def __str__(self):
        return "Load {} {}".format(self.dest, self.source)

class Store(TAC):
    def __init__(self, dest, source):
        self.dest = dest
        self.source = source

    def __str__(self):
        return "Store {} {}".format(self.dest, self.source)

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
