#!/usr/bin/env python2.7
import functools
import pydot
import tac
from symbol_table import *

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
    FUNCTION_NOT_FOUND      = 3
    def __init__(self, message, errno):
        super(SemaError, self).__init__(message, errno)

def semafunc(function):
    @functools.wraps(function)
    def wrap(*args, **kwargs):
        try:
            retval = function(*args, **kwargs)
        except Exception as e:
            if not hasattr(e, "ast"):
                e.ast = args[0]
            raise
        return retval 
    return wrap

class AST(object):
    def __init__(self):
        self._symbol_table = None
        self._parent       = None
        self._start_token  = None
        self._end_token    = None

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

    @semafunc
    def sema(self, data):
        raise NotImplementedError(type(self).__name__)

    def make_tac(self, state):
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

    def make_tac(self, state):
        out = []
        for s in self._statements:
            out += s.make_tac(state)
        return out

    def make_tables(self, table = None):
        self._symbol_table = SymbolTable()
        for s in self._statements:
            s.make_tables(self._symbol_table)

    @semafunc
    def sema(self, data = None):
        if not data:
            data = SemaData()
        for s in self._statements:
            s.sema(data)

class StatementList(AST):
    def __init__(self, *statements):
        super(StatementList, self).__init__()
        self._statements = statements

    def make_tables(self, table):
        for s in self._statements:
            s.make_tables(table)

    def __iter__(self):
        return iter(self._statements)

    @semafunc
    def sema(self, data):
        for s in self:
            s.sema(data)

    def make_tac(self, state):
        out = []
        for s in self:
            out += s.make_tac(state)
        return out

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
        self._statements.make_tables(table)

    @semafunc
    def sema(self, data):
        temp = data._ret_type
        data._ret_type = self._ret_type
        self._statements.sema(data)
        data._ret_type = temp

    def make_tac(self, state):
        out = []
        out += self._params.make_tac(state)
        out.append(tac.StartFunc(self._name))
        out += self._statements.make_tac(state)
        out.append(tac.EndFunc(self._name))
        return out
        

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
        self._statements.make_tables(self._symbol_table)

    @semafunc
    def sema(self, data):
        type0 = self._cond.sema(data)
        resolve_type(type0, "int")
        self._statements.sema(data)

    def make_tac(self, state):
        """
            CMP
            JZ L0
                S0
                ...
                SN
            L0:
        """
        out = []
        l0 = state.make_label()
        out += self._cond.make_tac(state)
        out.append(tac.JZ(l0, state.last_var()))
        out += self._statements.make_tac(state)
        out.append(l0)
        return out

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

    @semafunc
    def sema(self, data):
        if self._statement:
            type0 = self._statement.sema(data)
            resolve_type(type0, data._ret_type)

    def make_tac(self, state):
        if self._statement:
            out = self._statement.make_tac(state)
            out.append(tac.Return(state.last_var()))
            return out
        return [tac.Return(None)]

def resolve_type(type0, type1, operation = None):
    return
    raise NotImplementedError()

class Binop(AST):
    depth = 0
    def __init__(self, optype, lhs, rhs):
        super(Binop, self).__init__()
        self._optype = optype
        self._lhs    = lhs
        self._rhs    = rhs

    def __str__(self):
        out =  self._optype
        Binop.depth += 1
        out += "\n" + Binop.depth * "\t" + str(self._lhs)
        out += "\n" + Binop.depth * "\t" + str(self._rhs)
        Binop.depth -= 1
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

    @semafunc
    def sema(self, data):
        type0 = self._lhs.sema(data)
        type1 = self._rhs.sema(data)
        return resolve_type(type0, type1, self._optype)

    def make_tac(self, state):
        out = self._lhs.make_tac(state)
        t0 = state.last_var()
        out += self._rhs.make_tac(state)
        t1 = state.last_var()
        t2 = state.make_temp()
        out.append(tac.Op(self._optype, t2, t0, t1))
        return out

class Op(Binop): pass
class Comp(Binop): pass
class Assign(Binop):    
    def make_tac(self, state):
        out = self._rhs.make_tac(state)
        rhs_temp = state.last_var()
        lhs_temp = state.make_temp()
        out += self._lhs.make_tac(state)
        out.append(tac.Assign(self._lhs, rhs_temp))
        return out

class Import(AST):
    def __init__(self, identifier):
        self._identifier = identifier

    def make_graph(self, graph):
        node0 = make_node("import", graph)
        node1 = self._identifier.make_graph(graph)
        add_edge(graph, node0, node1)
        return node0

    @semafunc
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

    @semafunc
    def sema(self, data):
        try:
            function = self._symbol_table[self._identifier]
        except KeyError:
            print(self._identifier._start_token)
            raise SemaError("function {} cannot be found.".format(self._identifier._strval), 3)
        if not isinstance(function, Function):
            raise SemaError("identifier {} is not a function".format(function), 1)
        if len(function._params) != len(self._params):
            raise SemaError("number of arguments to function does not match", 2)
        for type0, statement in zip(function._params, self._params):
            type1 = statement.sema(data)
            resolve_type(type0, type1)

    def make_tac(self, state):
        out = [] 
        for p in self._params:
            out += p.make_tac(state)
            out.append(tac.Param(state.last_var()))
        out.append(tac.FuncCall(self._identifier))
        return out
class Type(AST):
    def __init__(self, identifier):
        if isinstance(identifier, str):
            self._identifier = Identifier(identifier)
        elif isinstance(identifier, Identifier):
            self._identifier = identifier
        else:
            raise Exception("Type must be Identifier for str")

    def make_graph(self, graph):
        return self._identifier.make_graph(graph)

    def make_tables(self, table):
        pass

    def __str__(self):
        return str(self._identifier)

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
        self._statements.make_tables(self._symbol_table)

    @semafunc
    def sema(self, data):
        if self._decl:
            type0 = self._decl.sema(data)
        if self._invariant:
            type0 = self._invariant.sema(data)
            resolve_type(type0, "int")
        if self._post:
            type0 = self._post.sema(data)
        self._statements.sema(data)

    def make_tac(self, state):
        out = []
        """
            INIT
            JP L1
            L0:
                S0
                ...
                SN
                POST
            L1:
                CMP
                JNZ L0
        """
        l0 = state.make_label()
        l1 = state.make_label()
        out = []
        if self._decl:
            out += self._decl.make_tac(state)
        out.append(tac.JP(l1))
        out.append(l0)
        out += self._statements.make_tac(state)
        if self._post:
            out += self._post.make_tac(state)
        out.append(l1)
        if self._invariant:
            out += self._invariant.make_tac(state)
        out.append(tac.JNZ(l0, state.last_var()))
        return out

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
        self._statements.make_tables(self._symbol_table)

    @semafunc
    def sema(self, data):
        type0 = self._cond.sema(data)
        resolve_type(type0, "int")
        self._statements.sema(data)

    def make_tac(self, state):
        """
            JP L1
            L0:
                S0
                ...
                SN
            L1:
                CMP
                JNZ L0
        """
        out = []
        l0 = state.make_label()
        l1 = state.make_label()
        out.append(tac.JP(l1))
        out.append(l0)
        out += self._statements.make_tac(state)
        out.append(l1)
        out += self._cond.make_tac(state)
        out.append(tac.JNZ(l0, state.last_var()))
        return out

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

    @semafunc
    def sema(self, data):
        if self._expr:
            type0 = self._expr.sema(data)
            resolve_type(self._type, type0)

    def make_tac(self, state):
        if self._expr:
            out = self._expr.make_tac(state)
            out.append(tac.Assign(self._var, state.last_var()))
            return out
        return []

class ParamList(AST):
    def __init__(self, *data):
        self._data = list(data)

    def append(self, data):
        self._data.append(data)

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def make_tables(self, table):
        for i in self._data:
            i.make_tables(table)

    def __len__(self):
        return len(self._data)

    def make_tac(self, state):
        out = []
        for s in self:
            out.append(tac.Argument(s._type, s._var))
            out += s.make_tac(state)
        return out

class Identifier(AST):
    def __init__(self, *identifiers):
        self._identifiers = identifiers
        self._strval      = ".".join(identifiers)

    def __repr__(self):
        return "Identifier<{}>".format(self._strval)

    def __str__(self):
        return self._strval

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

    @semafunc
    def sema(self, data):
        try:
            return self._symbol_table[self]
        except KeyError:
            raise SemaError("Identifier '{}' cannot be found in the current scope.".format(self._strval), 0)

    def make_tac(self, state):
        state.set_var(self)
        return []

class Literal(AST):
    def __init__(self, value):
        super(Literal, self).__init__()
        self._value = value

    def __str__(self):
        return self._value

    def make_graph(self, graph):
        node0 = make_node(self._value, graph)
        return node0

    def make_tables(self, table):
        self._symbol_table = table

    def sema(self, data):
        pass

    def make_tac(self, state):
        state.set_var(self)
        return []

class String(Literal):
    def __init__(self, value):
        super(String, self).__init__(value)
    def __str__(self):
        return '"{}"'.format(self._value)

class Number(Literal):
    def __init__(self, value):
        super(Number, self).__init__(value)

class Integer(Number):
    def __init__(self, value):
        super(Integer, self).__init__(value)

    @semafunc
    def sema(self, data):
        return "int"

class Float(Number):
    def __init__(self, value):
        super(Float, self).__init__(value)

    @semafunc
    def sema(self, data):
        return "int"

