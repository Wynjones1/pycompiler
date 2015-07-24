#!/usr/bin/env python2.7
import unittest
import lexer
from   compiler import *

class TestLexer(unittest.TestCase):
    def test_simple(self):
        data = "simple test case 213"
        a = [x for x in lexer.tokenise(data)]
        self.assertEqual(len(a), 4)

    def test_keywords(self):
        data = " ".join(lexer.keyword_list)
        a = [x for x in lexer.tokenise(data)]
        self.assertEqual(len(a), len(lexer.keyword_list))
        self.assertTrue(all([isinstance(x, lexer.Keyword) for x in a]))

    def _test_type(self, test_data, typeof, sep = " "):
        data = sep.join(test_data)
        a = [x for x in lexer.tokenise(data)]
        self.assertEqual(len(a), len(test_data))
        for x in a:
            self.assertTrue(isinstance(x, typeof), "{} is not of type {}".format(x, typeof.__name__))
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

    """
    def test_string(self):
        string_list = ['"hello, world!"', '"escaped string\""']
        self._test_type(string_list, lexer.String)
    """

class TestParser(unittest.TestCase):
    def _test_generic(self, data, func, typeof):
        for i in data:
            p = Parser(i)
            self.assertTrue(isinstance(func(p), typeof))
            self.assertTrue(p.done())

    def test_identifier(self):
        data = ["io.print", "hello", "a.b.d", "a.b_c123.d"]
        self._test_generic(data, parse_identifier, ast.Identifier)

    def test_string(self):
        data = ['"hello"']
        self._test_generic(data, parse_string, ast.String)

    def test_type(self):
        data = ["int", "function"]
        self._test_generic(data, parse_type, ast.Type)

    def test_param(self):
        data = ["int a, int b, int d, int c"]
        self._test_generic(data, parse_param_list, list)

    def test_number(self):
        data = ["123", "123.42", "123e23"]
        self._test_generic(data, parse_number, ast.Number)

    def test_var_decl(self):
        data = ["int a := 10", "float b := 10 * 30"]
        self._test_generic(data, parse_var_decl, ast.Decl)

    def test_expression(self):
        data = ["10"]
        self._test_generic(data, parse_expression , ast.Number)

    def test_for(self):
        data = ["for(int i := 0; i < 10; i += 1){}"]
        self._test_generic(data, parse_for, ast.For)

    def test_while(self):
        data = ["while(a < 10){}"]
        self._test_generic(data, parse_while, ast.While)

    def test_function(self):
        data = ["function a(int a) -> int{}"]
        self._test_generic(data, parse_function, ast.Function)

    def test_import(self):
        data = ["import io.network"]
        self._test_generic(data, parse_import, ast.Import)

if __name__ == "__main__":
    unittest.main()
