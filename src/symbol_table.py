#!/usr/bin/env python2.7
import syntax_tree as ast

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

        self._data   = {}
        self._parent = parent if parent else _global_symbol_table


    def __getitem__(self, key):
        try:
            return self._data[key]
        except KeyError as e:
            if self._parent:
                return self._parent[key]
            raise

    def __setitem__(self, key, value):
        assert(isinstance(value, (ast.Function, ast.Type)))
        assert(isinstance(key, ast.Identifier))
        if value in self._data:
            raise InvalidParse("identifier {} already defined in this scope".format(value))
        self._data[key] = value

    def set_parent(self, parent):
        assert isinstance(parent, SymbolTable)
        self._parent = parent

    def __str__(self):
        out = ""
        if self._parent:
            out = str(self._parent)
        out += str(self._data) + "\n"
        return out


def dummy_function(name):
    return ast.Function(ast.Identifier(name),
                        ast.ParamList(),
                        ast.Type(ast.Identifier("void")),
                        ast.StatementList())

def init_global_symbol_table():
    global _global_symbol_table
    if not _global_symbol_table:
        _global_symbol_table = True
        _global_symbol_table = SymbolTable()
        _global_symbol_table._parent = None
        _global_symbol_table[ast.Identifier("print")] = dummy_function("print")
