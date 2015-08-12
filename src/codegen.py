#!/usr/bin/env python2.7
from tac import *
import symbol_table

class CodeGenState(object):
    def __init__(self):
        self.output = []
        self.param_count = 0
        self.frame = None

    def outl(self, line, *args, **kwargs):
        self.out("\t" + line, *args, **kwargs)

    def out(self, line, *args, **kwargs):
        self.output.append(str(line).format(*args, **kwargs))

    def load(self, var, register):
        pass

    def get_offset(self, identifier):
        if self.frame == None:
            raise Exception("Cannot find {}, not in a stack frame".format(identifier))
        return self.frame[identifier]

    def get_register(self, temp):
        """ returns the current location of temp in registers
        """
        return "eax"

def sizeof(type):
    return 4

class StackFrame(object):
    def __init__(self):
        self.size    = 0
        self.offset  = 8 # account for the return address
        self.symbols = {}

    def __getitem__(self, key):
        return self.symbols[key]

def gen_stackframe(table, frame = None):
    if frame == None:
        frame = StackFrame()
        for name, type in table.data.items():
            size = sizeof(type)
            frame.symbols[name] = frame.offset
            frame.offset += size
        frame.offset = -4
    else:
        for name, type in table.data.items():
            if isinstance(type, ast.Type):
                size = sizeof(type)
                frame.symbols[name] = frame.offset
                frame.offset -= size
                frame.size += size
    for x in table.children:
        if isinstance(x, symbol_table.SubTable):
            frame = gen_stackframe(x, frame)
    return frame

def gen_StartFunc(x, state):
    state.frame = gen_stackframe(x.symbol_table)
    print(state.frame.symbols)
    state.out("{}:", x.identifier)
    state.outl("push ebp")
    state.outl("mov ebp, esp")
    state.outl("sub esp, {}", state.frame.size)

def gen_FuncCall(x, state):
    state.outl("call {}", x.identifier)
    state.outl("add esp, {}", state.param_count * 4)
    state.param_count = 0

def gen_Param(x, state):
    if isinstance(x.value, ast.Literal):
        state.outl("push {}", x.value)
    elif isinstance(x.value, ast.Identifier):
        offset = state.get_offset(x.value)
        state.outl("mov eax, [ebp + {}]", offset)
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
        state.outl("mov eax, [ebp + {}]", offset)
    elif isinstance(x.lhs, ast.Literal):
        state.outl("mov eax, {}", x.lhs)
    else:
        pass

    # load the rhs into ebx
    state.outl("push ebx")
    if isinstance(x.rhs, ast.Identifier):
        offset = state.get_offset(x.rhs)
        state.outl("mov ebx, [ebp + {}]", offset)
    elif isinstance(x.rhs, ast.Literal):
        state.outl("mov ebx, {}", x.rhs)
    else:
        raise NotImplementedError()
    state.outl("{} ebx", instr)
    state.outl("pop ebx")

def gen_Assign(x, state):
    offset = state.get_offset(x.identifier)
    if isinstance(x.var, ast.Literal):
        state.outl("mov dword [ebp + {}], {}", offset, x.var)
    elif isinstance(x.var, ast.Identifier):
        raise NotImplementedError()
    else:
        register = state.get_register(x.var)
        state.outl("mov [ebp + {}], {}", offset, register)

def gen_EndFunc(x, state):
    state.out(".end:")
    state.outl("add esp, {}", state.frame.size)
    state.outl("pop ebp")
    state.outl("ret")
    pass

def gen_Return(x, state):
    state.outl("jp .end")

def gen_JZ(x, state):
    if isinstance(x.var, ast.Literal):
        state.outl("mov eax, {}", offset, x.var)
    elif isinstance(x.var, ast.Identifier):
        offset = state.get_offset(x.var)
        state.outl("mov eax, [ebp + {}]", offset)
    else:
        raise NotImplementedError()
    state.outl("cmp eax, 0")
    state.outl("jz L{}", x.label.value)

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
        elif isinstance(x, Label):
            state.out(x)
        else:
            raise Exception(x.__class__.__name__)
    state.outl('%include "src/stdlib.asm"')

    return "\n".join(state.output)

if __name__ == "__main__":
    source = """\
    function f0(int f0_param_0, int f0_param_1)
    {
        print(f0_param_0)
    }

    function main()
    {
        int b := 2
        f0((b + 1) * (b + 2), b + 21)
    }
    """

    print(source)
    print("-" * 80)
    tac = make_tac(source)
    for x in tac:
        print(x)
    print("-" * 80)
    out = gen_asm(tac)
    print_asm = True
    if print_asm:
        print("----")
        for lineno, line in enumerate(out.split("\n")):
            sys.stdout.write("{:02d}:{}\n".format(lineno + 1, line))
    open("out.s", "w").write(out)
