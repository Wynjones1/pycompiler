#!/usr/bin/env python2.7
import pydot
import tac

node_counter = 0
def make_node(name, graph):
    global node_counter
    node = pydot.Node("{}".format(node_counter), label='"{}"'.format(name))
    graph.add_node(node)
    node_counter += 1
    return node

def add_edge(graph, node0, node1, label = ""):
    graph.add_edge(pydot.Edge(node0, node1, label='"{}"'.format(label)))

class SemaData(object):
    def __init__(self):
        self._ret_type = None

class SemaError(RuntimeError):
    IDENTIFIER_UNDEFINED    = 0
    IDENTIFIER_NOT_FUNCTION = 1
    FUNCTION_PARAM_MISMATCH = 2
    def __init__(self, message, errno):
        super(SemaError, self).__init__(message, errno)

class SymbolTable(object):
    """ SymbolTable contains the mapping of identifiers to types
        it can contain point to one of
        function or type
    """
    def __init__(self, parent = None):
        self._data   = {}
        self._parent = parent

    def __getitem__(self, key):
        try:
            return self._data[key]
        except KeyError as e:
            if self._parent:
                return self._parent[key]
            raise

    def __setitem__(self, key, value):
        assert(isinstance(value, (Function, Type)))
        assert(isinstance(key, Identifier))
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

_global_symbol_table = SymbolTable()

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

    def sema(self, data):
        raise NotImplementedError(type(self).__name__)

    def make_tac(self, label, var):
        """ make_tac generates the three address code
            intermediate representation

            Args:
            label -- count of labels used previously

            Returns:
            tuple (var, label) where:
            var   -- last temporary or variable generated
            label -- updated label count
        """
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

    def sema(self, data = None):
        if not data:
            data = SemaData()
        for s in self._statements:
            s.sema(data)

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
            node1  = make_node("param", graph)
            node2 = x._type.make_graph(graph)
            node3 = x._var.make_graph(graph)
            add_edge(graph, node0, node1)
            add_edge(graph, node1, node2)
            add_edge(graph, node1, node3)

        if self._ret_type:
            node1 = self._ret_type.make_graph(graph)
            add_edge(graph, node0, node1, "returns")

        for s in self._statements:
            node1 = s.make_graph(graph)
            add_edge(graph, node0, node1)
        return node0

    def make_tables(self, table):
        table[self._name] = self
        self._symbol_table = SymbolTable(table)
        self._params.make_tables(table)
        for s in self._statements:
            s.make_tables(self._symbol_table)

    def sema(self, data):
        temp = data._ret_type
        data._ret_type = self._ret_type
        for s in self._statements:
            s.sema(data)
        data._ret_type = temp
        

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
        self._cond.make_tables(table)
        for s in self._statements:
            s.make_tables(self._symbol_table)

    def sema(self, data):
        type0 = self._cond.sema(data)
        resolve_type(type0, "int")
        for s in self._statements:
            s.sema(data)

class Return(AST):
    def __init__(self, statement):  
        super(Return, self).__init__()
        self._statement = statement

    def make_graph(self, graph):
        node0 = make_node("return", graph)
        if self._statement:
            node1 = self._statement.make_graph(graph)
            add_edge(graph, node0, node1)
        return node0

    def make_tables(self, table):
        self._symbol_table = table
        if self._statement:
            self._statement.make_tables(table)

    def sema(self, data):
        if self._statement:
            type0 = self._statement.sema(data)
            resolve_type(type0, data._ret_type)

def resolve_type(type0, type1, operation = None):
    return
    raise NotImplementedError()

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

    def sema(self, data):
        type0 = self._lhs.sema(data)
        type1 = self._rhs.sema(data)
        return resolve_type(type0, type1, self._optype)

class Import(AST):
    def __init__(self, identifier):
        self._identifier = identifier

    def make_graph(self, graph):
        node0 = make_node("import", graph)
        node1 = self._identifier.make_graph(graph)
        add_edge(graph, node0, node1)
        return node0

    def sema(self, data):
        return None

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
        self._identifier.make_tables(table)
        for s in self._params:
            s.make_tables(table)

    def sema(self, data):
        function = self._symbol_table[self._identifier]
        if not isinstance(function, Function):
            raise SemaError("identifier {} is not a function".format(function), 1)
        if len(function._params) != len(self._params):
            raise SemaError("number of arguments to function does not match", 2)
        for type0, statement in zip(function._params, self._params):
            type1 = statement.sema(data)
            resolve_type(type0, type1)

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
        self._cond.make_tables(table)
        for s in self._statements:
            s.make_tables(self._symbol_table)

    def sema(self, data):
        type0 = self._cond.sema(data)
        resolve_type(type0, "int")
        for s in self._statements:
            s.sema(data)

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

    def sema(self, data):
        type0 = self._expr.sema(data)
        resolve_type(self._type, type0)

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
        self._strval      = ".".join(identifiers)
    def __repr__(self):
        return "Identifier<{}>".format(self._strval)

    def make_graph(self, graph):
        node0 = make_node(self._strval, graph)
        return node0

    def make_tables(self, table):
        self._symbol_table = table 

    def __eq__(self, other):
        if not isinstance(other, Identifier):
            return False
        if len(self._identifiers) != len(other._identifiers):
            return False
        return all(x == y for x, y, in zip(self._identifiers, other._identifiers))

    def __hash__(self):
        return self._strval.__hash__()

    def sema(self, data):
        try:
            return self._symbol_table[self]
        except KeyError:
            raise SemaError("Identifier '{}' cannot be found in the current scope.".format(self._strval), 0)

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

    def sema(self, data):
        return "int"

class Float(Number):
    def __init__(self, value):
        super(Float, self).__init__(value)

    def sema(self, data):
        return "int"
