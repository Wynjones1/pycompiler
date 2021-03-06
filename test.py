#!/usr/bin/env python2.7
import unittest
import types
from ddt import ddt, data

from src             import lexer
from src.parse       import *
from src.syntax_tree import *
from src.tac         import *

@ddt
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

    @data("1", "12", "123")
    def test_integer(self, data):
        toks = [x for x in lexer.tokenise(data)]
        self.assertEqual(len(toks), 1)
        self.assertIsInstance(toks[0], lexer.Integer)

    @data("0b0", "0b1", "0b10101", "0b0000")
    def test_binary_integer(self, data):
        toks = [x for x in lexer.tokenise(data)]
        self.assertEqual(len(toks), 1)
        self.assertIsInstance(toks[0], lexer.Integer)

    @data("0x0", "0x1", "0X123ABD",
          "1234567890", "0x1234567890abcdefABCDEF", "0x1e123")
    def test_hex_integer(self, data):
        toks = [x for x in lexer.tokenise(data)]
        self.assertEqual(len(toks), 1)
        self.assertIsInstance(toks[0], lexer.Integer)

    @data("0e10", "10e10", "0x1e10")
    def test_exponent_integer(self, data):
        toks = [x for x in lexer.tokenise(data)]
        self.assertEqual(len(toks), 1)
        self.assertIsInstance(toks[0], lexer.Integer)

    @data("0.1", "0.123456789", "123.456789", "1.0e10")
    def test_floats(self, data):
        toks = [x for x in lexer.tokenise(data)]
        self.assertEqual(len(toks), 1)
        self.assertIsInstance(toks[0], lexer.Float)

    def test_comps(self):
        comp_list = ["<", "<=", ">", ">=", "!=", "=="]
        self._test_type(comp_list, lexer.Comp)
        self._test_type(comp_list, lexer.Comp, sep = "")

    def test_simple_string(self):
        string_list = ['"Hello, world!"']
        self._test_type(string_list, lexer.String)

    @unittest.expectedFailure
    def test_escaped_string(self):
        string_list = ['"escaped string\""']
        self._test_type(string_list, lexer.String)

@ddt
class TestParser(unittest.TestCase):
    def assertIsFunction(self, data):
        self.assertIsInstance(data, ast.Function)
        self.assertIsInstance(data.name,      ast.Identifier)
        self.assertIsInstance(data.params,    ast.ParamList)
        self.assertIsInstance(data.ret_type,  ast.Type)
        self.assertIsInstance(data.statements,ast.StatementList)

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
        data = ["print", "hello"]
        self._test_generic(data, parse_identifier, ast.Identifier)

    def test_field_access(self):
        data = ["io.print", "a.b.d", "a.b_c123.d"]
        self._test_generic(data, parse_field_access, ast.FieldAccess)

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


    @data("function a(){}")
    def test_function_param_list(self, data):
        parser = Parser(data)
        func = parse_function(parser)
        self.assertIsFunction(func)

    def test_func_call(self):
        data = ["a()", "a(1)", "a(1, 2, 3)"]
        self._test_generic(data, parse_func_call, ast.FuncCall)

    def test_if(self):
        data = ["if(a < 10){}"]
        self._test_generic(data, parse_if, ast.If)

    def test_if_else(self):
        data = ["if(a < 10){}else{}"]
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

    def test_structure_0(self):
        data = """\
        struct name
        {
            int v0
        }
        """
        self._test_generic([data], parse_struct, ast.Struct)

    def test_structure_1(self):
        data = """\
        struct name
        {
            int v0
            int v1
            int v2
        }
        """
        self._test_generic([data], parse_struct, ast.Struct)

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
    def test_two_funcs_same_param_name(self):
        data = """\
        function f0(int a)
        {}
        function f1(int a)
        {}
        """
        tree = parse(data)
        tree.make_tac(TacState())

@ddt
class TestAST(unittest.TestCase):
    @data((ast.FieldAccess("a", "b"),      ast.FieldAccess("a", "b")),
          (ast.FieldAccess("a"),           ast.FieldAccess("a")),
          (ast.FieldAccess("a", "b", "c"), ast.FieldAccess("a", "b", "c")))
    def test_ast_field_access(self, data):
        self.assertEquals(data[0], data[1])

    def test_ast_field_access_not_equals(self):
        id0 = ast.FieldAccess("a")
        id1 = ast.FieldAccess("a", "b")
        data = [(ast.FieldAccess("a"), ast.FieldAccess("b")),
                (ast.FieldAccess("a"), ast.FieldAccess("a", "b"))]
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

class TestRenameTable(unittest.TestCase):
    def setUp(self):
        self.table = RenameTable()

    def test_no_rename(self):
        self.table.add(Identifier("a"))
        self.table.push()
        self.table.add(Identifier("b"))
        self.assertEqual(self.table[Identifier("b")], Identifier("b"))

    def test_with_rename(self):
        self.table.add(Identifier("a"))
        self.table.push()
        self.table.add(Identifier("a"))
        self.assertEqual(self.table[Identifier("a")], Identifier("a'"))

    def test_two_levels(self):
        self.table.add(Identifier("a"))
        self.table.push()
        self.table.add(Identifier("a"))
        self.table.push()
        self.table.add(Identifier("a"))
        self.assertEqual(self.table[Identifier("a")], Identifier("a''"))

class TestSema(unittest.TestCase):
    def test_function_call(self):
        data = """\
        function test_0(int a)
        {
            print(a)
        }

        function main()
        {
            test_0(10)
        }
        """

        tree = parse(data)
        tree.sema()

    def test_function_call_as_parameter(self):
        data = """\
        function test_0(int a) -> int
        {
            return a
        }

        function main()
        {
            print(test_0(10))
        }
        """
        tree = parse(data)
        tree.sema()

    def test_for_loop(self):
        data = """\
        function test_0()
        {
            for(int i := 0; i < 10; i += 1)
            {
                print(i)
            }
        }
        """
        tree = parse(data)
        tree.sema()

    def test_struct_decl_and_use(self):
        data = """\
        struct vector
        {
            int v0
            int v1
            int v2
        }

        function f0()
        {
            vector a
            a.v0 := 1
            a.v1 := 2
            a.v2 := 3
        }
        """
        tree = parse(data)
        tree.sema()
@ddt
class TestSemaErrors(unittest.TestCase):
    def assertRaisesSemaError(self, data, errortype):
        with self.assertRaises(errortype):
            # Some semantic errors are found during the
            # parse stage.
            tree = parse(data)
            tree.sema()
    
    def test_undefined_variable(self):
        data = """\
        function main()
        {
            a := 10
        }
        """
        self.assertRaisesSemaError(data, SemaIdentifierUndefinedError)

    def test_undefined_function(self):
        data = """\
        function main()
        {
            a()
        }
        """
        self.assertRaisesSemaError(data, SemaFunctionUndefinedError)

    def test_missing_function_parameter(self):
        data = """\
        function func_0(int a)
        {}

        function main()
        {
            func_0()
        }
        """
        self.assertRaisesSemaError(data, SemaParamMismatchError)

    def test_too_many_function_parameters(self):
        data = """\
        function func_0(int a)
        {}

        function main()
        {
            func_0(10, 10)
        }
        """
        self.assertRaisesSemaError(data, SemaParamMismatchError)

    def test_no_return_variable(self):
        data = """\
        function func_0() -> int
        {
            return
        }
        """
        self.assertRaisesSemaError(data, SemaNoReturnValueError)

    def test_returning_value_from_void(self):
        data = """\
        function func_0()
        {
            return 10
        }
        """
        self.assertRaisesSemaError(data, SemaReturnValueFromVoidError)

    def test_multiple_definitions(self):
        data = """\
        function func_0()
        {
            int a
            int a
        }
        """
        self.assertRaisesSemaError(data, SemaMultipleDeclarationError)

    def test_calling_non_function(self):
        data = """\
        function func_0()
        {
            int a
            a()
        }
        """
        self.assertRaisesSemaError(data, SemaCallingNonFunctionError)

    def test_returning_incorrect_type_0(self):
        data = """\
        function func_0() -> int
        {
            return "Some String"
        }
        """
        self.assertRaisesSemaError(data, SemaIncorrectReturnTypeError)

if __name__ == "__main__":
    unittest.main()
