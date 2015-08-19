#!/usr/bin/env python2.7
import os
from parse import *
import syntax_tree as ast
from graph import Graph

class TempVar(object):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "_t{}".format(self.value)

    def __eq__(self, other):
        if isinstance(other, TempVar):
            return self.value == other.value
        return False

    def __hash__(self):
        return self.value.__hash__()

    def __repr__(self):
        return "TempVar<{}>".format(self.value)

class Label(object):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return ".L{}:".format(self.value)

class RenameTable(object):
    """ RenameTable is used to keep track of identifiers that should
        be renamed, if they are in the table they are renames else
        they are left alone, adding an element to the table will
        add a suffix to make it unique. this suffix stacks so that
        if multiple nested  "scopes"  are dealt with correctly.

        e.g a -> a'
    """
    def __init__(self):
        self.data = [{}]

    def scope(self):
        class ContextManager(object):
            def __enter__(s):
                self.push()
            def __exit__(s, *args, **kwargs):
                self.pop()
        return ContextManager()

    def push(self):
        self.data.append({})

    def pop(self):
        self.data.pop()

    def add(self, value):
        if value in self.data[-1]:
            raise Exception("Duplicate Key : {}".format(value))
        try:
            prev = self[value]
            self.data[-1][value] = prev.suffix("'")
        except KeyError:
            self.data[-1][value] = value

    def __getitem__(self, key):
        for d in self.data[::-1]:
            try:
                if key in d:
                    return d[key]
            except KeyError:
                pass
        raise KeyError()

class TacState(object):
    def __init__(self):
        self.label_count = 0
        self._last_var    = None
        self.temp_count  = 0
        self.rename_table = RenameTable()
        self.decl_list = set()

    def last_var(self):
        assert self._last_var != None
        return self._last_var

    def set_var(self, var):
        self._last_var = var

    def make_temp(self):
        out = self.temp_count
        self.temp_count += 1
        id0 = ast.Identifier("_t{}".format(self.temp_count))
        self._last_var = id0
        #TODO: Cleanup the handling of this.
        self.decl_list.add(Decl(id0 , ast.Type("int")))
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
    def __init__(self, identifier, retval = None):
        self.identifier = identifier
        self.retval     = retval

    def __str__(self):
        if self.retval:
            return "{} = CALL {}".format(self.retval, self.identifier)
        else:
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
        return "{} := {}".format(self.identifier, self.var)

class Op(TAC):
    def __init__(self, op, assign, lhs, rhs):
        self.op     = op
        self.assign = assign
        self.lhs    = lhs
        self.rhs    = rhs

    def __str__(self):
        return "{} := {} {} {}".format( self.assign, self.lhs, self.op, self.rhs)

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

class Decl(TAC):
    def __init__(self, name, typename):
        self.name     = name
        self.typename = typename

    def __str__(self):
        return "decl {} {}".format(self.name, self.typename)

    def __eq__(self, other):
        return self.name == other.name and self.typename == other.typename

    def __hash__(self):
        return str(self).__hash__()

class EndDecls(TAC):
    def __str__(self):
        return "end_decls"

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
    function a(int a)
    {
        int local0 := 10
        if(1)
        {
            int a := 123
            int local0 := 11
            print(local0)
            print(a * a * (a + 1))
            print(a)

            if(1)
            {
                int a := 321
            }

            while(1)
            {
                int a := 1234
            }
        }
        print(local0)
    }
    """
    prog = parse(test)
    tac = prog.make_tac(TacState())
    graph = Graph()
    last = None
    for x in tac:
        print(x)
        graph.add_node(str(x))
        if len(graph.nodes) > 1:
            graph.add_edge(-2, -1)
    graph.output("tac_output.png")

    """
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--input", "-i",
                                 default = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                        "tests", "lang", "simple_0.x"))
    args = argument_parser.parse_args()

    data = open(args.input).read()
    program = parse(data)
    """
