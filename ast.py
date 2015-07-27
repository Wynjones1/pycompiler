#!/usr/bin/env python2.7
import pydot

node_counter = 0
def make_node(name, graph):
    global node_counter
    node = pydot.Node("{}".format(node_counter), label='"{}"'.format(name))
    graph.add_node(node)
    node_counter += 1
    return node

def add_edge(graph, node0, node1, label = ""):
    graph.add_edge(pydot.Edge(node0, node1, label='"{}"'.format(label)))

class SymbolTable(object):
    def __init__(self, parent = None):
        self._data   = {}
        self._parent = parent

    def __getitem__(self, key):
        try:
            return self._data[key]
        except KeyError:
            if self._parent:
                return self._parent[key]

    def __setitem__(self, key, value):
        if value in self._data:
            raise InvalidParse("identifier {} already defined in this scope".format(value))
        self._data[key] = value

    def set_parent(self, parent):
        assert isinstance(parent, SymbolTable)
        self._parent = parent

class AST(object):
    def __init__(self):
        self._symbol_table = None
        self._parent       = None

    def __repr__(self):
        return "ast.{}".format(type(self).__name__)

    def output_graph(self, filename):
        graph = pydot.Dot(graph_type="digraph")
        self.make_graph(graph)
        graph.write_png(filename)

    def make_graph(self, graph):
        raise NotImplementedError(type(self).__name__)

    def make_tables(self, table = None):
        raise NotImplementedError(type(self).__name__)

class Program(AST):
    def __init__(self, statements):
        super(Program, self).__init__()
        self._statements = statements

    def make_graph(self, graph):
        global node_count
        node_count = 0
        node0 = make_node("Top", graph)
        for s in self._statements:
            node1 = s.make_graph(graph)
            add_edge(graph, node0, node1)
        return node0

    def make_tables(self, table = None):
        self._symbol_table = SymbolTable()
        for s in self._statements:
            s.make_tables(self._symbol_table)

class Function(AST):
    def __init__(self, name, params, ret_type, statements):
        super(Function, self).__init__()
        self._name       = name
        self._params     = params
        self._ret_type   = ret_type
        self._statements = statements

    def make_graph(self, graph):
        node0 = make_node("function {}".format(str(self._name)), graph)
        for x in self._params:
            node  = make_node("param", graph)
            node1 = x._type.make_graph(graph)
            node2 = x._var.make_graph(graph)
            add_edge(graph, node0, node)
            add_edge(graph, node, node1)
            add_edge(graph, node, node2)

        if self._ret_type:
            node1 = self._ret_type.make_graph(graph)
            add_edge(graph, node0, node1, "returns")

        for s in self._statements:
            node1 = s.make_graph(graph)
            add_edge(graph, node0, node1)
        return node0

    def make_tables(self, table):
        self._symbol_table = SymbolTable(table)
        for x in self._params:
            self._symbol_table[x._var] = x._type
        for s in self._statements:
            s.make_tables(self._symbol_table)

class If(AST):
    def __init__(self, cond, statements):
        super(If, self).__init__()
        self._cond = cond
        self._statements = statements

    def make_graph(self, graph):
        node0 = make_node("if", graph)
        node1 = self._cond.make_graph(graph)
        add_edge(graph, node0, node1, "cond")
        for s in self._statements:
            node1 = s.make_graph(graph)
            add_edge(graph, node0, node1)
        return node0

    def make_tables(self, table):
        self._symbol_table = SymbolTable(table)
        self._cond.make_tables(self._symbol_table)
        for s in self._statements:
            s.make_tables(self._symbol_table)

class Return(AST):
    def __init__(self, statement):  
        super(Return, self).__init__()
        self._statement = statement

    def make_graph(self, graph):
        node0 = make_node("return", graph)
        node1 = self._statement.make_graph(graph)
        add_edge(graph, node0, node1)
        return node0

    def make_tables(self, table):
        self._symbol_table = table
        self._statement.make_tables(table)

class Op(AST):
    depth = 0
    def __init__(self, optype, lhs, rhs):
        super(Op, self).__init__()
        self._optype = optype
        self._lhs    = lhs
        self._rhs    = rhs

    def __str__(self):
        out =  self._optype
        Op.depth += 1
        out += "\n" + Op.depth * "\t" + str(self._lhs)
        out += "\n" + Op.depth * "\t" + str(self._rhs)
        Op.depth -= 1
        return out

    def make_graph(self, graph):
        node0 = make_node(self._optype, graph)
        node1 = self._lhs.make_graph(graph)
        node2 = self._rhs.make_graph(graph)
        add_edge(graph, node0, node1, "lhs")
        add_edge(graph, node0, node2, "rhs")
        return node0

    def make_tables(self, table):
        self._symbol_table = table
        self._lhs.make_tables(table)
        self._rhs.make_tables(table)

class Import(AST):
    def __init__(self, identifier):
        self._identifier = identifier

    def make_graph(self, graph):
        node0 = make_node("import", graph)
        node1 = self._identifier.make_graph(graph)
        add_edge(graph, node0, node1)
        return node0

class FuncCall(AST):
    def __init__(self, identifier, params):
        self._identifier = identifier
        self._params     = params

    def make_graph(self, graph):
        node0 = make_node("funccall", graph)
        node1 = make_node(self._identifier, graph)
        add_edge(graph, node0, node1, "name")
        for param in self._params:
            node2 = param.make_graph(graph)
            add_edge(graph, node0, node2, "param")
        return node0

    def make_tables(self, table):
        self._symbol_table = table

class Type(AST):
    def __init__(self, identifier):
        self._identifier = identifier

    def make_graph(self, graph):
        return self._identifier.make_graph(graph)

    def make_tables(self, table):
        pass

class For(AST):
    def __init__(self, decl, invariant, post, statements):
        self._decl       = decl
        self._invariant  = invariant
        self._post       = post
        self._statements = statements

    def make_graph(self, graph):
        node0 = make_node("for", graph)
        if self._decl:
            node1 = self._decl.make_graph(graph)
            add_edge(graph, node0, node1, "decl")
        if self._invariant:
            node1 = self._invariant.make_graph(graph)
            add_edge(graph, node0, node1, "invariant")
        if self._post:
            node1 = self._post.make_graph(graph)
            add_edge(graph, node0, node1, "post")
        for s in self._statements:
            node1 = s.make_graph(graph)
            add_edge(graph, node0, node1)
        return node0

    def make_tables(self, table):
        self._symbol_table = SymbolTable(table)
        if self._decl:
            self._decl.make_tables(self._symbol_table)
        if self._invariant:
            self._invariant.make_tables(self._symbol_table)
        if self._post:
            self._post.make_tables(self._symbol_table)
        for s in self._statements:
            s.make_tables(self._symbol_table)

class While(AST):
    def __init__(self, cond, statements):
        self._cond       = cond
        self._statements = statements

    def make_graph(self, graph):
        node0 = make_node("while", graph)
        node1 = self._cond.make_graph(graph)
        add_edge(graph, node0, node1, "cond")
        for s in self._statements:
            node2 = s.make_graph(graph)
            add_edge(graph, node0, node2)
        return node0

    def make_tables(self, table):
        self._symbol_table = SymbolTable(table)
        self._cond.make_tables(self._symbol_table)
        for s in self._statements:
            s.make_tables(self._symbol_table)

class Decl(AST):
    def __init__(self, type, var, expr):
        self._type = type
        self._var  = var
        self._expr = expr

    def make_graph(self, graph):
        node0 = make_node("decl", graph)
        node1 = self._type.make_graph(graph)
        node2 = self._var.make_graph(graph)
        add_edge(graph, node0, node1)
        add_edge(graph, node0, node2)

        if self._expr:
            node3 = self._expr.make_graph(graph)
            add_edge(graph, node0, node3, "init")
        return node0

    def make_tables(self, table):
        self._symbol_table = table
        table[self._var] = self._type

class ParamList(AST):
    def __init__(self):
        self._data = []

    def append(self, data):
        self._data.append(data)

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def make_tables(self, table):
        for i in self._data:
            i.make_tables(table)

class Identifier(AST):
    def __init__(self, *identifiers):
        self._identifiers = identifiers

    def __str__(self):
        return ".".join(self._identifiers)

    def make_graph(self, graph):
        node0 = make_node(".".join(self._identifiers), graph)
        return node0

    def make_tables(self, table):
        self._symbol_table = table 

class Literal(AST):
    def __init__(self, value):
        super(Literal, self).__init__()
        self._value = value

    def make_graph(self, graph):
        node0 = make_node(self._value, graph)
        return node0

    def make_tables(self, table):
        self._symbol_table = table

class String(Literal):
    def __init__(self, value):
        super(String, self).__init__(value)

class Number(Literal):
    def __init__(self, value):
        super(Number, self).__init__(value)

class Integer(Number):
    def __init__(self, value):
        super(Integer, self).__init__(value)

class Float(Number):
    def __init__(self, value):
        super(Float, self).__init__(value)
