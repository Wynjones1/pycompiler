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
        self.ret_type = None

class SemaError(RuntimeError):
    def __init__(self, message):
        super(SemaError, self).__init__(message)

class SemaIdentifierUndefinedError(SemaError):
    pass

class SemaCallingNonFunctionError(SemaError):
    pass

class SemaParamMismatchError(SemaError):
    pass

class SemaFunctionUndefinedError(SemaError):
    pass

class SemaReturnValueFromVoidError(SemaError):
    pass

class SemaNoReturnValueError(SemaError):
    pass

class SemaMultipleDeclarationError(SemaError):
    pass

class SemaIncorrectReturnTypeError(SemaError):
    pass

class SemaTypeResolveError(SemaError):
    pass


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
        self.symbol_table = None
        self.parent       = None
        self.start_token  = None
        self.end_token    = None

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
        self.statements = statements

    def make_graph(self, graph):
        global node_count
        node_count = 0
        node0 = make_node("Top", graph)
        for s in self.statements:
            node1 = s.make_graph(graph)
            add_edge(graph, node0, node1)
        return node0

    def make_tac(self, state):
        out = []
        for s in self.statements:
            out += s.make_tac(state)
        return out

    def make_tables(self, table = None):
        self.symbol_table = SymbolTable()
        for s in self.statements:
            s.make_tables(self.symbol_table)

    @semafunc
    def sema(self, data = None):
        if not data:
            data = SemaData()
        for s in self.statements:
            s.sema(data)

class StatementList(AST):
    def __init__(self, *statements):
        super(StatementList, self).__init__()
        self.statements = statements

    def make_tables(self, table):
        self.symbol_table = table
        for s in self.statements:
            s.make_tables(self.symbol_table)

    def __iter__(self):
        return iter(self.statements)

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
        self.name       = name
        self.params     = params
        self.ret_type   = ret_type
        self.statements = statements

    def make_graph(self, graph):
        node0 = make_node("function {}".format(str(self.name)), graph)
        for x in self.params:
            node1  = make_node("param", graph)
            node2 = x.type.make_graph(graph)
            node3 = x.var.make_graph(graph)
            add_edge(graph, node0, node1)
            add_edge(graph, node1, node2)
            add_edge(graph, node1, node3)

        if self.ret_type:
            node1 = self.ret_type.make_graph(graph)
            add_edge(graph, node0, node1, "returns")

        for s in self.statements:
            node1 = s.make_graph(graph)
            add_edge(graph, node0, node1)
        return node0

    def make_tables(self, table):
        table[self.name] = self
        self.symbol_table = ParamTable(table)
        self.name.make_tables(table)
        self.ret_type.make_tables(table)

        self.params.make_tables(self.symbol_table)
        self.statements.make_tables(SubTable(self.symbol_table))

    @semafunc
    def sema(self, data):
        temp = data.ret_type
        data.ret_type = self.ret_type
        self.statements.sema(data)
        data.ret_type = temp

    def make_tac(self, state):
        out = [tac.StartFunc(self.name, self.symbol_table)]
        with state.rename_table.scope():
            out += self.params.make_tac(state)
            state.decl_list = set()
            temp = [tac.EndDecls()]
            temp += self.statements.make_tac(state)
            temp.append(tac.EndFunc(self.name))
        return out + list(state.decl_list) + temp
        

class If(AST):
    def __init__(self, cond, success, failure):
        super(If, self).__init__()
        self.cond    = cond
        self.success = success
        self.failure = failure

    def make_graph(self, graph):
        node0 = make_node("if", graph)
        node1 = self.cond.make_graph(graph)
        add_edge(graph, node0, node1, "cond")
        node2 = make_node("success", graph)
        node3 = make_node("fail", graph)
        add_edge(graph, node0, node2)
        add_edge(graph, node0, node3)
        for s in self.success:
            node1 = s.make_graph(graph)
            add_edge(graph, node2, node1)

        if self.failure:
            for s in self.failure:
                node1 = s.make_graph(graph)
                add_edge(graph, node3, node1)
        return node0

    def make_tables(self, table):
        self.symbol_table = table
        self.cond.make_tables(table)
        self.success.make_tables(SubTable(self.symbol_table))
        if self.failure:
            self.failure.make_tables(SubTable(self.symbol_table))

    @semafunc
    def sema(self, data):
        type0 = self.cond.sema(data)
        resolve_type(type0, Type("int"))
        self.success.sema(data)
        if self.failure:
            self.failure.sema(data)

    def make_tac(self, state):
        """
            CMP
            JZ L0
                S0
                ...
                SN
                JP L1
            L0:
                F0
                ...
                FN
            L1:
        """
        out = []
        l0 = state.make_label()
        out += self.cond.make_tac(state)
        out.append(tac.JZ(l0, state.last_var()))
        with state.rename_table.scope():
            out += self.success.make_tac(state)

        if self.failure:
            l1 = state.make_label()
            out.append(tac.JP(l1))

        out.append(l0)

        if self.failure:
            with state.rename_table.scope():
                out += self.failure.make_tac(state)
            out.append(l1)
        return out

class Return(AST):
    def __init__(self, statement):  
        super(Return, self).__init__()
        self.statement = statement

    def make_graph(self, graph):
        node0 = make_node("return", graph)
        if self.statement:
            node1 = self.statement.make_graph(graph)
            add_edge(graph, node0, node1)
        return node0

    def make_tables(self, table):
        self.symbol_table = table
        if self.statement:
            self.statement.make_tables(table)

    @semafunc
    def sema(self, data):
        if self.statement:
            # Check if we are returning from a void function
            if data.ret_type == ast.Type("void"):
                msg = "Returning value from void function"
                raise SemaReturnValueFromVoidError(msg)
            # Check that the return type matched the data returned.
            type0 = self.statement.sema(data)
            try:
                resolve_type(type0, data.ret_type)
            except SemaTypeResolveError:
                raise SemaIncorrectReturnTypeError("{} {}".format(type0, data.ret_type))
        elif data.ret_type != ast.Type("void"):
            #TODO: Improve the error message given.
            msg = "No return value given"
            raise SemaNoReturnValueError(msg)

    def make_tac(self, state):
        if self.statement:
            out = self.statement.make_tac(state)
            out.append(tac.Return(state.last_var()))
            return out
        return [tac.Return(None)]

def resolve_type(type0, type1, operation = None):
    if not type0 == type1:
        raise SemaTypeResolveError("{} != {}".format(type0, type1))
    return type0

class Binop(AST):
    depth = 0
    def __init__(self, optype, lhs, rhs):
        super(Binop, self).__init__()
        self.optype = optype
        self.lhs    = lhs
        self.rhs    = rhs

    def __str__(self):
        out =  self.optype
        Binop.depth += 1
        out += "\n" + Binop.depth * "\t" + str(self.lhs)
        out += "\n" + Binop.depth * "\t" + str(self.rhs)
        Binop.depth -= 1
        return out

    def make_graph(self, graph):
        node0 = make_node(self.optype, graph)
        node1 = self.lhs.make_graph(graph)
        node2 = self.rhs.make_graph(graph)
        add_edge(graph, node0, node1, "lhs")
        add_edge(graph, node0, node2, "rhs")
        return node0

    def make_tables(self, table):
        self.symbol_table = table
        self.lhs.make_tables(table)
        self.rhs.make_tables(table)
        #Check if this should be a string
        #self.optype.make_tables(table)

    @semafunc
    def sema(self, data):
        type0 = self.lhs.sema(data)
        type1 = self.rhs.sema(data)
        return resolve_type(type0, type1, self.optype)

    def make_tac(self, state):
        out = self.lhs.make_tac(state)
        t0 = state.last_var()
        out += self.rhs.make_tac(state)
        t1 = state.last_var()
        t2 = state.make_temp()
        out.append(tac.Op(self.optype, t2, t0, t1))
        return out

class Op(Binop): pass
class Comp(Binop): pass
class Assign(Binop):    
    def make_tac(self, state):
        out = []
        if self.optype == ":=":
            out += self.rhs.make_tac(state)
            rhs_temp = state.last_var()
            out += self.lhs.make_tac(state)
            out.append(tac.Assign(state.last_var(), rhs_temp))
        else:
            mapping = {"-=" : "-", "+=" : "+"}
            op = mapping[self.optype]

            out += self.rhs.make_tac(state)
            t0 = state.last_var()

            out += self.lhs.make_tac(state)
            t1 = state.last_var()
            out.append(tac.Op(op,state.last_var(), t1, t0))
            out += self.lhs.make_tac(state)
        return out

class Import(AST):
    def __init__(self, identifier):
        self.identifier = identifier

    def make_graph(self, graph):
        node0 = make_node("import", graph)
        node1 = self.identifier.make_graph(graph)
        add_edge(graph, node0, node1)
        return node0

    @semafunc
    def sema(self, data):
        return None

class FuncCall(AST):
    def __init__(self, identifier, params):
        self.identifier = identifier
        self.params     = params

    def make_graph(self, graph):
        node0 = make_node("funccall", graph)
        node1 = make_node(self.identifier, graph)
        add_edge(graph, node0, node1, "name")
        for param in self.params:
            node2 = param.make_graph(graph)
            add_edge(graph, node0, node2, "param")
        return node0

    def make_tables(self, table):
        self.symbol_table = table
        self.identifier.make_tables(table)
        for s in self.params:
            s.make_tables(table)

    @semafunc
    def sema(self, data):
        try:
            function = self.symbol_table[self.identifier]
        except KeyError:
            msg = "function {} cannot be found.".format(self.identifier.value),
            raise SemaFunctionUndefinedError(msg)
        if not isinstance(function, Function):
            msg = "identifier {} is not a function".format(function)
            raise SemaCallingNonFunctionError(msg)
        if len(function.params) != len(self.params):
            raise SemaParamMismatchError(
                      "number of arguments to function does not match")
        for type0, statement in zip(function.params, self.params):
            type1 = statement.sema(data)
            resolve_type(type0.type, type1)
        return function.ret_type

    def make_tac(self, state):
        out = [] 
        #TODO: Add function names to rename table
        name = self.identifier
        for p in self.params[::-1]:
            out += p.make_tac(state)
            out.append(tac.Param(state.last_var()))
        out.append(tac.FuncCall(name, state.make_temp()))
        return out

class Type(AST):
    def __init__(self, identifier):
        super(Type, self).__init__()
        if isinstance(identifier, str):
            self.identifier = Identifier(identifier)
        elif isinstance(identifier, Identifier):
            self.identifier = identifier
        else:
            raise Exception("Type must be Identifier or str")

    def make_graph(self, graph):
        return self.identifier.make_graph(graph)

    def make_tables(self, table):
        self.symbol_table = table
        self.identifier.make_tables(table)

    def make_tac(self, state):
        #TODO: Add types to the rename table
        state.set_var(self)
        return []

    def __str__(self):
        return str(self.identifier)

    def __eq__(self, other):
        return self.identifier == other.identifier

class For(AST):
    def __init__(self, decl, invariant, post, statements):
        self.decl       = decl
        self.invariant  = invariant
        self.post       = post
        self.statements = statements

    def make_graph(self, graph):
        node0 = make_node("for", graph)
        if self.decl:
            node1 = self.decl.make_graph(graph)
            add_edge(graph, node0, node1, "decl")
        if self.invariant:
            node1 = self.invariant.make_graph(graph)
            add_edge(graph, node0, node1, "invariant")
        if self.post:
            node1 = self.post.make_graph(graph)
            add_edge(graph, node0, node1, "post")
        for s in self.statements:
            node1 = s.make_graph(graph)
            add_edge(graph, node0, node1)
        return node0

    def make_tables(self, table):
        self.symbol_table = SubTable(table)
        if self.decl:
            self.decl.make_tables(self.symbol_table)
        if self.invariant:
            self.invariant.make_tables(self.symbol_table)
        if self.post:
            self.post.make_tables(self.symbol_table)
        self.statements.make_tables(self.symbol_table)

    @semafunc
    def sema(self, data):
        if self.decl:
            type0 = self.decl.sema(data)
        if self.invariant:
            type0 = self.invariant.sema(data)
            resolve_type(type0, Type("int"))
        if self.post:
            type0 = self.post.sema(data)
        self.statements.sema(data)

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
        with state.rename_table.scope():
            if self.decl:
                out += self.decl.make_tac(state)
            out.append(tac.JP(l1))
            out.append(l0)
            with state.rename_table.scope():
                out += self.statements.make_tac(state)
            if self.post:
                out += self.post.make_tac(state)
            out.append(l1)
            if self.invariant:
                out += self.invariant.make_tac(state)
            out.append(tac.JNZ(l0, state.last_var()))
        return out

class While(AST):
    def __init__(self, cond, statements):
        self.cond       = cond
        self.statements = statements

    def make_graph(self, graph):
        node0 = make_node("while", graph)
        node1 = self.cond.make_graph(graph)
        add_edge(graph, node0, node1, "cond")
        for s in self.statements:
            node2 = s.make_graph(graph)
            add_edge(graph, node0, node2)
        return node0

    def make_tables(self, table):
        self.symbol_table = table
        self.cond.make_tables(self.symbol_table)
        self.statements.make_tables(SubTable(self.symbol_table))

    @semafunc
    def sema(self, data):
        type0 = self.cond.sema(data)
        resolve_type(type0, "int")
        self.statements.sema(data)

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
        with state.rename_table.scope():
            out += self.statements.make_tac(state)
        out.append(l1)
        out += self.cond.make_tac(state)
        out.append(tac.JNZ(l0, state.last_var()))
        return out

class Decl(AST):
    def __init__(self, type, var, expr):
        self.type = type
        self.var  = var
        self.expr = expr

    def make_graph(self, graph):
        node0 = make_node("decl", graph)
        node1 = self.type.make_graph(graph)
        node2 = self.var.make_graph(graph)
        add_edge(graph, node0, node1)
        add_edge(graph, node0, node2)

        if self.expr:
            node3 = self.expr.make_graph(graph)
            add_edge(graph, node0, node3, "init")
        return node0

    def make_tables(self, table):
        self.symbol_table = table
        self.var.make_tables(table)
        if self.expr:
            self.expr.make_tables(table)
        try:
            table[self.var] = self.type
        except KeyError:
            #TODO: Add a better error message
            msg = ""
            raise SemaMultipleDeclarationError(msg)

    @semafunc
    def sema(self, data):
        if self.expr:
            type0 = self.expr.sema(data)
            resolve_type(self.type, type0)

    def make_tac(self, state):
        state.rename_table.add(self.var)
        name = state.rename_table[self.var]
        self.type.make_tac(state)
        state.decl_list.add(tac.Decl(name, state.last_var()))
        if self.expr:
            out = self.expr.make_tac(state)
            out.append(tac.Assign(name, state.last_var()))
            return out
        return []

class ParamList(AST):
    def __init__(self, *data):
        self.data = list(data)

    def append(self, data):
        self.data.append(data)

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def make_tables(self, table):
        self.symbol_table = table
        for i in self.data:
            i.make_tables(self.symbol_table)

    def __len__(self):
        return len(self.data)

    def make_tac(self, state):
        out = []
        for s in self:
            out += s.type.make_tac(state)
            out.append(tac.Argument(s.type, s.var))
            out += s.make_tac(state)
        return out

class Identifier(AST):
    def __init__(self, value):
        super(Identifier, self).__init__()
        self.value = value

    def __repr__(self):
        return "Identifier<{}>".format(self.value)

    def __str__(self):
        return self.value

    def make_graph(self, graph):
        node0 = make_node(str(self), graph)
        return node0

    def make_tables(self, table):
        self.symbol_table = table 

    def suffix(self, string):
        """ Add a suffix to a single length identifier
        """
        return Identifier(self.value + string)

    def __eq__(self, other):
        try:
            return self.value == other.value
        except:
            raise ValueError("Connot compare identifier with object of type {}".format(other.__class__.__name__))

    def __hash__(self):
        return self.value.__hash__()

    @semafunc
    def sema(self, data):
        try:
            return self.symbol_table[self]
        except KeyError:
            msg = "Identifier '{}' cannot be found in the current scope.".format(self.value)
            raise SemaIdentifierUndefinedError(msg)

    def make_tac(self, state):
        var = state.rename_table[self]
        state.set_var(var)
        return []

class FieldAccess(AST):
    def __init__(self, *identifiers):
        self.identifiers = identifiers

    def __repr__(self):
        return ".".join(self.identifiers)
    def __str__(self):
        return ".".join(self.identifiers)

class Literal(AST):
    def __init__(self, value):
        super(Literal, self).__init__()
        self.value = value

    def __str__(self):
        return self.value

    def make_graph(self, graph):
        node0 = make_node(self.value, graph)
        return node0

    def make_tables(self, table):
        self.symbol_table = table

    def sema(self, data):
        pass

    def make_tac(self, state):
        state.set_var(self)
        return []

class String(Literal):
    count = 0
    def __init__(self, value):
        super(String, self).__init__(value)
        self.count = String.count
        String.count += 1
    def __str__(self):
        return '"{}"'.format(self.value)

    @semafunc
    def sema(self, data):
        return Type("string")

class Number(Literal):
    def __init__(self, value):
        super(Number, self).__init__(value)

class Integer(Number):
    def __init__(self, value):
        super(Integer, self).__init__(value)

    @semafunc
    def sema(self, data):
        return Type("int")

class Float(Number):
    def __init__(self, value):
        super(Float, self).__init__(value)

    @semafunc
    def sema(self, data):
        #TODO: Change to correct type.
        return Type("int")

