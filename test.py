#!/usr/bin/env python2.7
import unittest
import types
from src             import lexer
from src.parse       import *
from src.syntax_tree import *

class TestLexer(unittest.TestCase):
    def _test_simple(self):
        data = "simple test case 213"
        a = [x for x in tokenise(data)]
        self.assertEqual(len(a), 4)

    def _test_keywords(self):
        data = " ".join(lexer.keyword_list)
        a = [x for x in lexer.tokenise(data)]
        self.assertEqual(len(a), len(lexer.keyword_list))
        self.assertTrue(all([isinstance(x, lexer.Keyword) for x in a]))

    def _test_type(self, test_data, typeof, sep = " "):
        data = sep.join(test_data)
        a = [x for x in lexer.tokenise(data)]
        self.assertEqual(len(a), len(test_data))
        for x in a:
            self.assertIsInstance(x, typeof, "{} is not of type {}".format(x, typeof.__name__))
        #self.assertTrue(all([isinstance(x, type) for x in a]))

    def test_identifiers(self):
        id_list = ["a",
                   "aa",
                   "asd_",
                   "abcdefghijklmnopqrstuvwxyz1234567890",
                   "sodifj_osdjf_naosdf_ofa"]
        self._test_type(id_list, lexer.Identifier)

    def test_integers(self):
        int_list = ["123", "0x123", "0b10010101001010", "0X123ABD", "1234567890", "0x1234567890abcdefABCDEF", "1e123"]
        self._test_type(int_list, lexer.Integer)

    def test_floats(self):
        int_list = ["0.1", "0.123456789", "123.456789", "1.0e10"]
        self._test_type(int_list, lexer.Float)

    def test_comps(self):
        comp_list = ["<", "<=", ">", ">=", "!=", "=="]
        self._test_type(comp_list, lexer.Comp)
        self._test_type(comp_list, lexer.Comp, sep = "")

    @unittest.expectedFailure
    def test_string(self):
        string_list = ['"hello, world!"', '"escaped string\""']
        self._test_type(string_list, lexer.String)

class TestParser(unittest.TestCase):
    def _test_generic(self, data, func, typeof):
        for idx, i in enumerate(data):
            p = Parser(i)
            result = func(p)
            result.make_tables(ast.SymbolTable())
            #result.make_tac()
            self.assertTrue(isinstance(result, typeof), "Test {}: {}".format(idx, i))
            self.assertTrue(isinstance(result, ast.AST),"Test {}: {}".format(idx, i))
            self.assertTrue(p.done(), "Test {}: {}".format(idx, result))

    def test_identifier(self):
        data = ["io.print", "hello", "a.b.d", "a.b_c123.d"]
        self._test_generic(data, parse_identifier, ast.Identifier)

    def test_string(self):
        data = ['"hello"']
        self._test_generic(data, parse_string, ast.String)

    def test_type(self):
        data = ["int"]
        self._test_generic(data, parse_type, ast.Type)

    def test_param_list(self):
        data = ["int a",
                "int a, int b",
                "",
                "int a, int b, int d, int c"
               ]
        self._test_generic(data, parse_param_list, ast.ParamList)

    def test_number(self):
        data = ["123", "123.42", "123e23"]
        self._test_generic(data, parse_number, ast.Number)

    def test_decl(self):
        data = ["int a", "int a := 10", "float b := 10 * 30"]
        self._test_generic(data, parse_decl, ast.Decl)

    def test_expression(self):
        data = ["10 * 10",
                "1 * 2 + 3",
                "1 + 2 * 3",
                "a < 10"]
        self._test_generic(data, parse_expression , ast.Binop)

    def test_for(self):
        data = ["for(int i := 0; i < 10; i += 1){}",
                "for(int i := 0; i < 10;){}",
                "for(int i := 0;; i += 1){}",
                "for(i := 0; i < 10; i += 1){}",
                "for(int i := 0;;){}",
                "for(;i < 10;){}",
                "for(;;i += 1){}",
                "for(;;){}"]
        self._test_generic(data, parse_for, ast.For)

    def test_while(self):
        data = ["while(a < 10){}"]
        self._test_generic(data, parse_while, ast.While)

    def test_function(self):
        data = ["function a(int a) -> int{}",
                "function a(){}",
                "function a(int a, int b){}",
                "function a(int a) -> int{}"]
        self._test_generic(data, parse_function, ast.Function)

    def test_function_in_function(self):
        data = ["""function a()
        {
           function a(){}
        }"""]
        self._test_generic(data, parse_function, ast.Function)

    def test_function_param_list(self):
        data = ["function a(){}"]
        for d in data:
            parser = Parser(d)
            func = parse_function(parser)
            self.assertIsInstance(func, ast.Function)
            self.assertIsInstance(func.name,      ast.Identifier)
            self.assertIsInstance(func.params,    ast.ParamList)
            self.assertIsInstance(func.ret_type,  ast.Type)
            self.assertIsInstance(func.statements,ast.StatementList)

    def test_func_call(self):
        data = ["a()", "a(1)", "a(1, 2, 3)"]
        self._test_generic(data, parse_func_call, ast.FuncCall)

    def test_if(self):
        data = ["if(a < 10){}"]
        self._test_generic(data, parse_if, ast.If)

    def test_return(self):  
        data = ["return", "return 10", "return a", "return (1 + 2)"]
        self._test_generic(data, parse_return, ast.Return)

    def test_program(self):
        data = ["", "function a(){}"]
        self._test_generic(data, parse_program, ast.Program)

    @unittest.expectedFailure
    def test_import(self):
        data = ["import io.network"]
        self._test_generic(data, parse_import, ast.Import)

class TestParserFail(unittest.TestCase):
    def _test_fail(self, func, data):
        for x in data:
            p = Parser(x)
            self.assertRaises((InvalidParse, ParseError), func, p)

    def _test_for(self):
        data = ["for(){",]
        self._test_fail(parse_for, data)

    def _test_identifier(self):
        data = ["a."]
        self._test_fail(parse_identifier, data)

class TestTAC(unittest.TestCase):
    pass

class TestAST(unittest.TestCase):
    def test_ast_identifier_equals(self):
        id0 = ast.Identifier("a")
        id1 = ast.Identifier("a", "b")
        data = [(ast.Identifier("a", "b"), ast.Identifier("a", "b")),
                (ast.Identifier("a"), ast.Identifier("a")),
                (ast.Identifier("a", "b", "c"), ast.Identifier("a", "b", "c")),
                (id0, id0),
                (id1, id1)
               ]
        for lhs, rhs in data:
            self.assertEquals(lhs, rhs)

    def test_ast_identifier_not_equals(self):
        id0 = ast.Identifier("a")
        id1 = ast.Identifier("a", "b")
        data = [(ast.Identifier("a"), ast.Identifier("b")),
                (ast.Identifier("a"), ast.Identifier("a", "b"))]
        for lhs, rhs in data:
            self.assertNotEquals(lhs, rhs)

class TestSymbolTable(unittest.TestCase):
    def test_identifier_in_same_scope(self):
        table = SymbolTable()
        test = Type("int")
        table[ast.Identifier("a")] = test
        temp = table[ast.Identifier("a")]
        self.assertIs(test, temp)

    def test_identifeir_in_different_scope(self):
        table = SymbolTable()
        test = Type("int")
        table[ast.Identifier("a")] = test
        table = SymbolTable(table)
        temp = table[ast.Identifier("a")]
        self.assertIs(test, temp)

    def test_identifier_in_multiple_scopes(self):
        table = SymbolTable()
        table[ast.Identifier("a")] = Type("int")
        table = SymbolTable(table)
        test = Type("int")
        table[ast.Identifier("a")] = test
        temp = table[ast.Identifier("a")]
        self.assertIs(test, temp)

    def test_identifier_not_in_table(self):
        table = SymbolTable()
        with self.assertRaises(KeyError):
            table[ast.Identifier("a")]

    def test_symbol_table_children(self):
        table0 = SymbolTable()
        table1 = SymbolTable(table0)
        table2 = SymbolTable(table0)

        self.assertIs(table0.children[0], table1)
        self.assertIs(table0.children[1], table2)

class TestSema(unittest.TestCase):
    pass

if __name__ == "__main__":
    unittest.main()
