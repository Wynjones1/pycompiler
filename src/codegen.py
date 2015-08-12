#!/usr/bin/env python2.7
from tac import *

class CodeGenState(object):
    def __init__(self):
        self.output = []
        self.param_count = 0
        self.symbol_table = None

    def outl(self, line, *args, **kwargs):
        self.out("\t" + line, *args, **kwargs)

    def out(self, line, *args, **kwargs):
        self.output.append(line.format(*args, **kwargs))

    def load(self, var, register):
        pass

    def get_offset(self, identifier):
        offset = 0
        return - 4

    def get_register(self, temp):
        """ returns the current location of temp in registers
        """
        return "eax"

class StackFrame(object):
    def __init__(self, parent):
        #contains, (type, name, size, offset)
        self.parent = parent
        self.arguments = []
        #contains, (type, name, size, offset)
        self.params = []
        self.size   = 0

    def add_argument(self, type, name):
        self.argument.append((type, name, offset))
        self.size += 4

    def add_param(self, type, name):
        self.argument.append((type, name, offset))
        self.size += 4

def gen_StartFunc(x, state):
    state.symbol_table = x.symbol_table
    print("{} : {}".format(x, state.symbol_table.children))
    print("{}".format(state.symbol_table.children[0]))
    state.out("{}:", x.identifier)
    state.outl("push ebp")
    state.outl("mov ebp, esp")

def gen_FuncCall(x, state):
    state.outl("call {}", x.identifier)
    state.outl("add esp, {}", state.param_count * 4)
    state.param_count = 0

def gen_Param(x, state):
    if isinstance(x.value, ast.Literal):
        state.outl("push {}", x.value)
    elif isinstance(x.value, ast.Identifier):
        offset = state.get_offset(x.value)
        state.outl("mov eax, [esp + {}]", offset)
        state.outl("push eax")
    else:
        state.outl("push {}", state.get_register(x.value))
    state.param_count += 1

def gen_Argument(x, state):
    pass

def gen_Op(x, state):
    """
        <op> <result> <lhs> <rhs>
    """
    instructions = {
        "+" : "add eax,",
        "-" : "sub eax,",
        "*" : "mul"
    }
    instr = instructions[x.op]

    # load the lhs into eax
    if isinstance(x.lhs, ast.Identifier):
        offset = state.get_offset(x.lhs)
        state.outl("mov eax, [esp + {}]", offset)
    elif isinstance(x.lhs, ast.Literal):
        state.outl("mov eax, {}", x.lhs)
    else:
        raise NotImplementedError()

    # load the rhs into ebx
    state.outl("push ebx")
    if isinstance(x.rhs, ast.Identifier):
        offset = state.get_offset(x.rhs)
        state.outl("mov ebx, [esp + {}]", offset)
    elif isinstance(x.rhs, ast.Literal):
        state.outl("mov ebx, {}", x.rhs)
    else:
        raise NotImplementedError()
    state.outl("{} ebx", instr)
    state.outl("pop ebx")

def gen_Assign(x, state):
    offset = state.get_offset(x.identifier)
    if isinstance(x.var, ast.Literal):
        state.outl("mov dword [esp + {}], {}", offset, x.var)
    elif isinstance(x.var, ast.Identifier):
        raise NotImplementedError()
    else:
        register = state.get_register(x.var)
        state.outl("mov [esp + {}], {}", offset, register)

def gen_EndFunc(x, state):
    state.out(".end:")
    state.outl("pop ebp")
    state.outl("ret")
    pass

def gen_Return(x, state):
    state.outl("jp .end")

def output_print(state):
    state.outl("mov eax, 4")
    state.outl("mov ebx, 1")
    state.outl("mov ecx, print")
    state.outl("mov edx, print_len")
    state.outl("int 80h")

def gen_asm(tac):

    state = CodeGenState()
    state.out("[BITS 32]")

    state.out("section .data")

    state.out("section .bss")
    state.out("str0: resb 0x20")
    setup_stack = True
    if setup_stack:
        state.out("_stack_start:")
        state.outl("resb 0xffff")
        state.out("_stack_end:")

    state.out("section .text")
    state.outl("global _start")
    state.out("_start:")
        
    if setup_stack:
        state.outl("mov esp, _stack_start")
    state.outl("mov ebp, esp")
    state.outl("call main")
    state.outl("mov ebx, 0")
    state.outl("mov eax, 1")
    state.outl("int 0x80")

    for x in tac:
        state.out(";------------------------------------| {}", x)
        if isinstance(x, StartFunc):
            gen_StartFunc(x, state)
        elif isinstance(x, Param):
            gen_Param(x, state)
        elif isinstance(x, Argument):
            gen_Argument(x, state)
        elif isinstance(x, Op):
            gen_Op(x, state)
        elif isinstance(x, Return):
            gen_Return(x, state)
        elif isinstance(x, JP):
            gen_JP(x, state)
        elif isinstance(x, JNZ):
            gen_JNZ(x, state)
        elif isinstance(x, JZ):
            gen_JZ(x, state)
        elif isinstance(x, Assign):
            gen_Assign(x, state)
        elif isinstance(x, EndFunc):
            gen_EndFunc(x, state)
        elif isinstance(x, Return):
            gen_Return(x, state)
        elif isinstance(x, FuncCall):
            gen_FuncCall(x, state)
        else:
            raise Exception(x.__class__.__name__)
    state.outl('%include "src/stdlib.asm"')

    return "\n".join(state.output)

if __name__ == "__main__":
    source = """\
    function f0(int f0_param_0, int f0_param_1)
    {
        int f0_scope_0
    }

    function main()
    {
        int b := 1234
        int a123
        print(b)
        f0(b + 1, b + 2)
    }
    """

    print(source)
    print("-" * 80)
    tac = make_tac(source)
    for x in tac:
        print(x)
    print("-" * 80)
    out = gen_asm(tac)
    #print("----")
    #for lineno, line in enumerate(out.split("\n")):
    #    sys.stdout.write("{:02d}:{}\n".format(lineno + 1, line))
    #open("out.s", "w").write(out)
