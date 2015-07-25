#!/usr/bin/env python2.7
from lexer import *
import functools
import sys
import argparse

class Parser(object):
    def __init__(self, tokens):
        if type(tokens) == str:
            tokens = [x for x in tokenise(tokens)]
        self._tokens = tokens
        self._pos    = -1

    def next(self):
        try:
            self._pos += 1
            out = self._tokens[self._pos]
            return out
        except IndexError:
            return None

    def peek(self, *test):
        try:
            if len(test):
                return any( self._tokens[self._pos + 1] == x for x in test)
            else:
                return self._tokens[self._pos + 1]
        except IndexError:
            return None

    def cur(self):
        try:
            return self._tokens[self._pos]
        except IndexError:
            raise InvalidParse()

    def expect(self, test, message = ""):
        if self.cur() != test:
            raise InvalidParse(message)
        return self.cur()

    def accept(self, test, message = ""):
        self.next()
        return self.expect(test, message)

    def get_pos(self):
        return self._pos

    def set_pos(self, pos):
        self._pos = pos

    def done(self):
        return self._pos + 1 == len(self._tokens)

    def consume(self, test):
        while self.peek(test):
            self.next()

indent  = 0
verbose = False
def parsefunc(func):
    @functools.wraps(func)
    def wrap(parser):
        global indent
        pos = parser.get_pos()
        if verbose:
            print("\t" * indent + "enter: " + func.__name__)
        indent += 1
        try:
            retval = func(parser)
            indent -= 1
            #print("\t" * indent + "exit : " + func.__name__)
            return retval
        except InvalidParse as e:
            if e._function == None:
                e._function = func
            parser.set_pos(pos)
            indent -= 1
            if verbose:
                print("\t" * indent + "fail : " + func.__name__)
            raise
    return wrap

class InvalidParse(Exception):
    def __init__(self, *args, **kwargs):
        super(Exception, self).__init__(*args, **kwargs)
        self._function = None

class ParseError(RuntimeError):
    pass

@parsefunc
def parse_identifier(parser):
    identifiers = [parser.accept(Identifier).get_value()]
    while parser.peek("."):
        try:
            parser.next()
            identifiers.append(parser.accept(Identifier).get_value())
        except InvalidParse:
            raise ParseError("", parser.cur()), None, sys.exc_info()[2]
    return ast.Identifier(*identifiers)

@parsefunc
def parse_string(parser):
    return ast.String(parser.accept(String).get_value())

@parsefunc
def parse_type(parser):
    if parser.peek("function"):
        parser.next()
        return ast.Type(ast.Identifier("function"))
    return ast.Type(parse_identifier(parser))

@parsefunc
def parse_param(parser):
    type = parse_type(parser)
    name = parse_identifier(parser)
    return (type, name)

@parsefunc
def parse_param_list(parser):
    out = []
    while True:
        try:
            out.append(parse_param(parser))
        except InvalidParse:
            break
        if parser.peek(","):
            parser.next()
        else:
            break
    return out

@parsefunc
def parse_number(parser):
    if parser.peek(Integer):
        return ast.Integer(parser.next().get_value())
    if parser.peek(Float):
        return ast.Float(parser.next().get_value())
    raise InvalidParse()

@parsefunc
def parse_var_decl(parser):
    type = parse_type(parser)
    id   = parse_identifier(parser)
    parser.accept(":=")
    expr = parse_expression(parser)
    return ast.Decl(type, id, expr)

@parsefunc
def parse_for(parser):
    decl      = None
    invariant = None
    post      = None
    parser.accept("for")
    try:
        parser.accept("(")
        if not parser.peek(";"):
            try:
                decl = parse_var_decl(parser)
            except InvalidParse:
                decl = parse_expression(parser)
        parser.accept(";")
        if not parser.peek(";"):
            invariant = parse_expression(parser)
        parser.accept(";")
        if not parser.peek(")"):
            post = parse_expression(parser)
        parser.accept(")")
        parser.consume("\n")
        parser.accept("{")
        parser.consume("\n")
        statements = parse_statement_list(parser) 
        parser.accept("}")
        return ast.For(decl, invariant, post, statements)
    except InvalidParse as e:
        raise ParseError("", parser.cur()), None, sys.exc_info()[2]

@parsefunc
def parse_if(parser):
    parser.accept("if")
    try:
        parser.accept("(")
        cond = parse_expression(parser)
        parser.accept(")")
        parser.consume("\n")
        parser.accept("{")
        parser.consume("\n")
        statements = parse_statement_list(parser)
        parser.accept("}")
        return ast.If(cond = cond, statements = statements)
    except InvalidParse as e:
        raise ParseError("", parser.cur()), None, sys.exc_info()[2]

@parsefunc
def parse_return(parser):
    parser.accept("return")
    try:
        ret = ast.Return(parse_expression(parser))
        parser.consume("\n")
        return ret
    except InvalidParse:
        raise ParseError("", parser.cur()), None, sys.exc_info()[2]

@parsefunc
def parse_paren_expr(parser):
    parser.accept("(")
    ret = parse_expression(parser)
    parser.accept(")")
    return ret

@parsefunc
def parse_func_call(parser):
    identifier = parse_identifier(parser)
    parser.accept("(")
    params = []
    try:
        params.append(parse_expression(parser))
        while parser.peek(","):
            parser.next()
            out.append(parse_expr(parser))
    except InvalidParse:
        pass
    parser.accept(")")
    return ast.FuncCall(identifier, params)

@parsefunc
def parse_atomic_expr(parser):
    funcs = (parse_func_call,
             parse_identifier,
             parse_number,
             parse_paren_expr,
             parse_string,)
    for func in funcs:
        try:
            return func(parser)
        except InvalidParse:
            pass
    raise InvalidParse()

@parsefunc
def parse_ops(parser):
    raise InvalidParse()

def is_left_assoc(op):
    return True

def get_prec(op):
    prec_table = {
        ":=" : 0,
        "+=" : 0,
        "-=" : 0,
        "*=" : 0,
        "/=" : 0,
        "!=" : 1,
        "==" : 1,
        "<"  : 1,
        "<=" : 1,
        ">"  : 1,
        ">=" : 1,
        "-"  : 2,
        "+"  : 3,
        "/"  : 4,
        "*"  : 5,
    }
    return prec_table[op._value]

def make_op(list_in):
    if list_in[-1] in (Op, Comp, AssignBase):
        optype = list_in.pop()
        rhs = make_op(list_in)
        lhs = make_op(list_in)
        return ast.Op(optype.get_value(), lhs, rhs)
    else:
        return list_in.pop()

@parsefunc
def parse_expression(parser):
    stack  = []
    output = []
    while not parser.peek("\n"):
        if parser.peek(Op, Comp, AssignBase):
            op1 = parser.next()
            while len(stack):
                op2 = stack[-1]
                if (is_left_assoc(op1) and get_prec(op1) <= get_prec(op2)) or (get_prec(op1) < get_prec(op2)):
                    output.append(stack.pop())
                else:
                    break
            stack.append(op1)
        else:
            try:
                output.append(parse_atomic_expr(parser))
            except InvalidParse:
                break

    if output:
        while stack:
            output.append(stack.pop())
        ret = make_op(output)
        if(output):
            raise InvalidParse()
        return ret
    else:
        raise InvalidParse()

@parsefunc
def parse_statement(parser):
    funcs = (parse_var_decl,
             parse_expression,
             parse_for,
             parse_function,
             parse_return,
             parse_while,
             parse_if,)
    for func in funcs:
        try:
            return func(parser)
        except InvalidParse:
            pass
    raise InvalidParse()

@parsefunc
def parse_statement_list(parser):
    out = []
    while True:
        try:
            out.append(parse_statement(parser))
            parser.consume("\n")
        except InvalidParse:
            break
    return out

@parsefunc
def parse_function(parser):
    ret_type = None
    # function declaration 
    parser.accept("function")
    try:
        name = parse_identifier(parser)
        parser.accept("(")
        params = parse_param_list(parser)
        parser.accept(")")
        # parse return type
        if parser.peek("->"):
            parser.next()
            ret_type = parse_type(parser)
        parser.consume("\n")
        # start of function body
        parser.accept("{")
        parser.consume("\n")
        statements = parse_statement_list(parser)
        parser.consume("\n")
        parser.accept("}")
        return ast.Function(name       = name,
                            params     = params,
                            ret_type   = ret_type,
                            statements = statements)
    except InvalidParse as e:
        raise ParseError("", parser.cur()), None, sys.exc_info()[2]

@parsefunc
def parse_while(parser):
    parser.accept("while")
    try:
        parser.accept("(")
        expr = parse_expression(parser)
        parser.accept(")")
        parser.consume("\n")
        parser.accept("{")
        parser.consume("\n")
        statements = parse_statement_list(parser)
        parser.accept("}")
        return ast.While(expr, statements)
    except InvalidParse:
        raise ParseError("", parser.cur()), None, sys.exc_info()[2]

@parsefunc
def parse_import(parser):
    parser.accept("import")
    try:
        return ast.Import(parse_identifier(parser))
    except InvalidParse:
        raise ParseError("", parser.cur()), None, sys.exc_info()[2]

def parse(tokens):
    parser = Parser(tokens)
    funcs = (parse_function, parse_import)
    statements = []
    parser.consume("\n")
    try:
        while not parser.done():
            for func in funcs:
                try:
                    statements.append(func(parser))
                    break
                except InvalidParse:
                    pass
            else:
                raise
            parser.consume("\n")
        return ast.Program(statements)
    except ParseError as e:
        print(e[1].highlight(10, 10))
        raise
