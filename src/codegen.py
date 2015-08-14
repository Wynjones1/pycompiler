#!/usr/bin/env python2.7
from tac import *

class CodeGenState(object):
    def __init__(self):
        self.output = []
        self.param_count = 0
        self.pos = 0
        self.pos_stack = []

        # This will store the offsets for the
        # All of the frames
        self.decls        = [{}]
        self.param_offset = [0]
        self.arg_offset   = [0]

    def new_frame(self):
        self.decls.append({})
        self.param_offset.append(0)
        self.arg_offset.append(0)

    def delete_frame(self):
        self.decls.pop()
        self.param_offset.pop()
        self.arg_offset.pop()

    def add_decl(self, decl):
        self.decls[-1][decl.name] = -self.param_offset[-1] - 4
        self.param_offset[-1] += self.sizeof(decl.typename)

    def add_arg(self, arg):
        self.decls[-1][arg.identifier] = self.arg_offset[-1] + 8
        self.arg_offset[-1] += self.sizeof(arg.type)

    def sizeof(self, type):
        return 4


    def outl(self, line, *args, **kwargs):
        self.out("\t" + line, *args, **kwargs)

    def out(self, line, *args, **kwargs):
        self.output.append(str(line).format(*args, **kwargs))

    def load(self, var, register):
        pass

    def get_offset(self, identifier):
        return self.decls[-1][identifier]

    def get_register(self, temp):
        """ returns the current location of temp in registers
        """
        return "eax"

    def push(self, register):
        self.pos += 4
        self.outl("push {}", register)

    def pop(self, register):
        self.pos -= 4
        self.outl("pop {}", register)

    def add_stack(self, amount):
        self.pos += amount
        self.outl("sub esp, {}", amount)

    def sub_stack(self, amount):
        self.pos -= amount
        self.outl("add esp, {}", amount)

    def set_base_pointer(self):
        self.pos_stack.append(self.pos)
        self.outl("push ebp")
        self.outl("mov ebp, esp")
        self.pos = 0

    def unset_base_pointer(self):
        self.outl("mov esp, ebp")
        self.outl("pop ebp")
        self.pos = self.pos_stack.pop()
        

def gen_StartFunc(x, state):
    state.new_frame()
    state.out("{}:", x.identifier)
    state.set_base_pointer()

def gen_Decl(x, state):
    state.add_decl(x)

def gen_EndDecls(x, state):
    state.add_stack(state.param_offset[-1])

def gen_FuncCall(x, state):
    state.outl("call {}", x.identifier)
    state.sub_stack(state.param_count)
    state.param_count = 0

def gen_Param(x, state):
    if isinstance(x.value, ast.Literal):
        state.push(x.value)
    elif isinstance(x.value, ast.Identifier):
        offset = state.get_offset(x.value)
        state.outl("mov eax, [ebp + {}]", offset)
        state.push("eax")
    else:
        state.push(state.get_register(x.value))
    state.param_count += 4

def gen_Argument(x, state):
    state.add_arg(x)

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
    state.push("eax")
    if isinstance(x.rhs, ast.Identifier):
        offset = state.get_offset(x.rhs)
        state.outl("mov ebx, [ebp + {}]", offset)
    elif isinstance(x.rhs, ast.Literal):
        state.outl("mov ebx, {}", x.rhs)
    else:
        raise NotImplementedError()
    state.outl("{} ebx", instr)
    state.pop("ebx")

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
    state.unset_base_pointer()
    state.outl("ret")
    state.delete_frame()

def gen_Return(x, state):
    state.outl("jp .end")

def gen_JZ(x, state):
    if isinstance(x.var, ast.Literal):
        state.outl("mov eax, {}", x.var.value)
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
        elif isinstance(x, EndFunc):
            gen_EndFunc(x, state)
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
        elif isinstance(x, Return):
            gen_Return(x, state)
        elif isinstance(x, FuncCall):
            gen_FuncCall(x, state)
        elif isinstance(x, Decl):
            gen_Decl(x, state)
        elif isinstance(x, EndDecls):
            gen_EndDecls(x, state)
        elif isinstance(x, Label):
            state.out(x)
        else:
            raise Exception(x.__class__.__name__)
    state.outl('%include "src/stdlib.asm"')

    return "\n".join(state.output)

if __name__ == "__main__":
    source = """\
    function fib(int a) -> int
    {
        print(a)
    }

    function main()
    {
        print(fib(0))
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
