#!/usr/bin/env python2.7
from tac import *

class CodeGenState(object):
    def __init__(self):
        self._output = []

    def outl(self, line, *args, **kwargs):
        self.out("\t" + line, *args, **kwargs)

    def out(self, line, *args, **kwargs):
        self._output.append(line.format(*args, **kwargs))

    def load(self, var, register):
        pass

    def get_offset(self, identifier):
        return - 4

    def get_register(self, temp):
        return "eax"

def gen_StartFunc(x, state):
    state.out("{}:", x._identifier)
    state.outl("push ebp")
    state.outl("mov ebp, esp")

def gen_FuncCall(x, state):
    state.outl("call {}", x._identifier)

def gen_Param(x, state):
    if isinstance(x._value, ast.Literal):
        state.outl("push {}", x._value)
    else:
        raise NotImplemented()

def gen_Op(x, state):
    instructions = {
        "+" : "add",
        "-" : "sub",
        "*" : "mul"
    }
    instr = instructions[x._op]
    if isinstance(x._lhs, ast.Identifier):
        offset = state.get_offset(x._lhs)
        state.outl("mov eax, [eps + {}]", offset)
    elif isinstance(x._lhs, ast.Literal):
        state.outl("mov eax, {}", x._lhs)
    if isinstance(x._rhs, ast.Identifier):
        offset = state.get_offset(x._rhs)
        state.outl("{} eax, [esp + {}]", instr, offset)

def gen_Assign(x, state):
    offset = state.get_offset(x._identifier)
    register = state.get_register(x._var)
    state.outl("mov [esp + {}], {}", offset, register)
    pass

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
    state.out("print:")
    state.outl("message db 'Hello, world', 0xa")
    state.out("print_len: equ $ - print")

    setup_stack = True
    if setup_stack:
        state.out("section .bss")
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

    return "\n".join(state._output)

if __name__ == "__main__":
    source = """\
    function main()
    {
        print(10)
    }
    """

    tac = make_tac(source)
    for x in tac:
        print(x)
    out = gen_asm(tac)
    print("----")
    print(out)
    open("out.s", "w").write(out)
