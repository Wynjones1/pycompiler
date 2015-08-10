#!/usr/bin/env python2.7
from tac import *

class CodeGenState(object):
    def __init__(self):
        self._output = []
        self._param_count = 0

    def outl(self, line, *args, **kwargs):
        self.out("\t" + line, *args, **kwargs)

    def out(self, line, *args, **kwargs):
        self._output.append(line.format(*args, **kwargs))

    def load(self, var, register):
        pass

    def get_offset(self, identifier):
        return - 4

    def get_register(self, temp):
        """ returns the current location of temp in registers
        """
        return "eax"

def gen_StartFunc(x, state):
    state.out("{}:", x._identifier)
    state.outl("push ebp")
    state.outl("mov ebp, esp")

def gen_FuncCall(x, state):
    state.outl("call {}", x._identifier)
    state.outl("add esp, {}", state._param_count * 4)
    state._param_count = 0

def gen_Param(x, state):
    if isinstance(x._value, ast.Literal):
        state.outl("push {}", x._value)
    else:
        state.outl("push {}", state.get_register(x._value))
    state._param_count += 1

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
    instr = instructions[x._op]

    # load the lhs into eax
    if isinstance(x._lhs, ast.Identifier):
        offset = state.get_offset(x._lhs)
        state.outl("mov eax, [esp + {}]", offset)
    elif isinstance(x._lhs, ast.Literal):
        state.outl("mov eax, {}", x._lhs)
    else:
        raise NotImplementedError()

    # load the rhs into ebx
    state.outl("push ebx")
    if isinstance(x._rhs, ast.Identifier):
        offset = state.get_offset(x._rhs)
        state.outl("mov ebx, [esp + {}]", offset)
    elif isinstance(x._rhs, ast.Literal):
        state.outl("mov ebx, {}", x._rhs)
    else:
        raise NotImplementedError()
    state.outl("{} ebx", instr)
    state.outl("pop ebx")

def gen_Assign(x, state):
    offset = state.get_offset(x._identifier)
    if isinstance(x._var, ast.Literal):
        state.outl("mov dword [esp + {}], {}", offset, x._var)
    elif isinstance(x._var, ast.Identifier):
        raise NotImplementedError()
    else:
        register = state.get_register(x._var)
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

    return "\n".join(state._output)

if __name__ == "__main__":
    source = """\
    function f0(int a, int b)
    {
    }

    function main()
    {
        int b := 10
        b := b * 10
        print(0)
        print(10)
        print(123)
        print(1234567)
        print(4294967295)
        f0(b + 1, b + 2)
    }
    """

    tac = make_tac(source)
    for x in tac:
        print(x)
    out = gen_asm(tac)
    print("----")
    for lineno, line in enumerate(out.split("\n")):
        sys.stdout.write("{:02d}:{}\n".format(lineno + 1, line))
    open("out.s", "w").write(out)
