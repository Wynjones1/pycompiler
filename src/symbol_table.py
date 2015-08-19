#!/usr/bin/env python2.7
import syntax_tree as ast
from   collections import OrderedDict

_global_symbol_table = None

class SymbolTable(object):
    """ SymbolTable contains the mapping of identifiers to types
        it can contain point to one of
        function or type
    """
    def __init__(self, parent = None):
        #TODO: remove this ugly hack
        global _global_symbol_table
        init_global_symbol_table()

        self.data     = OrderedDict()
        if parent:
            parent.children.append(self)

        self.parent   = parent if parent else _global_symbol_table
        self.children = []


    def __getitem__(self, key):
        try:
            return self.data[key]
        except KeyError as e:
            if self.parent:
                return self.parent[key]
            raise

    def __setitem__(self, key, value):
        assert(isinstance(value, (ast.Function, ast.Type)))
        assert(isinstance(key, ast.Identifier))
        if key in self.data.keys():
            raise KeyError()
        self.data[key] = value

    def set_parent(self, parent):
        assert isinstance(parent, SymbolTable)
        self.parent = parent

    def __str__(self):
        out = ""
        if self.parent:
            out = str(self.parent)
        out += str(self.data) + "\n"
        return out

class ParamTable(SymbolTable):
    pass

class SubTable(SymbolTable):
    pass


def dummy_function(name, return_type_name, *args):
    return_type = ast.Type(ast.Identifier(return_type_name))
    params = []
    for i, j in enumerate(args):
        param_name = "param_{}".format(i)
        params.append(ast.Decl(ast.Type(j),
                               ast.Identifier(param_name),
                               None))
        
    return ast.Function(ast.Identifier(name),
                        ast.ParamList(*params),
                        return_type,
                        ast.StatementList())

def add_dummy_function(name, return_type, *args):
    _global_symbol_table[ast.Identifier(name)] = \
                dummy_function(name, return_type, *args)
def init_global_symbol_table():
    global _global_symbol_table
    if not _global_symbol_table:
        _global_symbol_table = True
        _global_symbol_table = SymbolTable()
        _global_symbol_table.parent = None
        add_dummy_function("print", "void", "int")
        add_dummy_function("prints", "void", "string")
        add_dummy_function("putc", "void", "int")
