#!/usr/bin/env python2.7
import pydot

node_counter = 0
def make_node(name, graph):
    global node_counter
    node = pydot.Node("{}".format(node_counter), label='"{}"'.format(name))
    graph.add_node(node)
    node_counter += 1
    return node

def add_edge(graph, node0, node1, label):
    graph.add_edge(pydot.Edge(node0, node1, label=label))

class AST(object):
    def __repr__(self):
        return "ast.{}".format(type(self).__name__)

    def output_graph(self, filename):
        graph = pydot.Dot(graph_type="digraph")
        self.make_graph(graph)
        graph.write_png(filename)

    def make_graph(self, graph):
        raise NotImplementedError(type(self).__name__)
        return make_node("", graph)

class Program(AST):
    def __init__(self, statements):
        self._statements = statements

    def make_graph(self, graph):
        global node_count
        node_count = 0
        node0 = make_node("Top", graph)
        for s in self._statements:
            node1 = s.make_graph(graph)
            add_edge(graph, node0, node1, "")
        return node0

class Function(AST):
    def __init__(self, name, params, ret_type, statements):
        super(Function, self).__init__()
        self._name       = name
        self._params     = params
        self._ret_type   = ret_type
        self._statements = statements

    def make_graph(self, graph):
        node0 = make_node("function {}".format(str(self._name)), graph)
        for type, identifier in self._params:
            node  = make_node("param", graph)
            node1 = type.make_graph(graph)
            node2 = identifier.make_graph(graph)
            add_edge(graph, node0, node, "")
            add_edge(graph, node, node1, "")
            add_edge(graph, node, node2, "")

        if self._ret_type:
            node1 = self._ret_type.make_graph(graph)
            add_edge(graph, node0, node1, "returns")

        for s in self._statements:
            node1 = s.make_graph(graph)
            add_edge(graph, node0, node1, "")
        return node0

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
            add_edge(graph, node0, node1, "")
        return node0

class Return(AST):
    def __init__(self, statement):  
        super(Return, self).__init__()
        self._statement = statement

    def make_graph(self, graph):
        node0 = make_node("return", graph)
        node1 = self._statement.make_graph(graph)
        add_edge(graph, node0, node1, "")
        return node0

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

class Import(AST):
    def __init__(self, identifier):
        self._identifier = identifier

    def make_graph(self, graph):
        node0 = make_node("import", graph)
        node1 = self._identifier.make_graph(graph)
        add_edge(graph, node0, node1, "")
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

class Type(AST):
    def __init__(self, identifier):
        self._identifier = identifier

    def make_graph(self, graph):
        return self._identifier.make_graph(graph)

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
            add_edge(graph, node0, node1, "")
        return node0

class While(AST):
    def __init__(self, cond, statements):
        self._cond       = cond
        self._statements = statements

class Decl(AST):
    def __init__(self, type, var, expr):
        self._type = type
        self._var  = var
        self._expr = expr

    def make_graph(self, graph):
        node0 = make_node("decl", graph)
        node1 = self._type.make_graph(graph)
        node2 = self._var.make_graph(graph)
        node3 = self._expr.make_graph(graph)
        add_edge(graph, node0, node1, "")
        add_edge(graph, node0, node2, "")
        add_edge(graph, node0, node3, "")
        return node0


class Identifier(AST):
    def __init__(self, *identifiers):
        self._identifiers = identifiers

    def __str__(self):
        return ".".join(self._identifiers)

    def make_graph(self, graph):
        node0 = make_node(".".join(self._identifiers), graph)
        return node0

class Literal(AST):
    def __init__(self, value):
        super(Literal, self).__init__()
        self._value = value

    def make_graph(self, graph):
        node0 = make_node(self._value, graph)
        return node0

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
