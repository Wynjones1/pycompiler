#!/usr/bin/env python2.7
from tac import *

class CodeGenState(object):
    def __init__(self):
        self.output = []
        self.param_count = 0
        self.pos = 0
        self.pos_stack = []
        self.strings = []

        # This will store the offsets for the
        # All of the frames
        self.decls        = [{}]
        self.param_offset = [0]
        self.arg_offset   = [0]
        self.label_count  = 0

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

    def load(self, register, var):
        if isinstance(var, (ast.Literal, str)):
            if isinstance(var, ast.String):
                self.outl("mov {}, strconst_{}", register, var.count)
                self.strings.append(var)
            else:
                self.outl("mov {}, {}", register, var)
        elif isinstance(var, ast.Identifier):
            self.outl("mov {}, [ebp + {}]",register, self.get_offset(var))

    def store(self, loc, val):
        offset0 = self.get_offset(loc)
        if isinstance(val, ast.Literal):
            self.outl("mov dword [ebp + {}], {}", offset, val)
        elif isinstance(val, ast.Identifier):
            self.load("eax", val)
            self.outl("mov dword [ebp + {}], eax", offset0)
        elif isinstance(val, str):
            self.outl("mov dword [ebp + {}], {}", offset0, val)

    def get_offset(self, identifier):
        return self.decls[-1][identifier]

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
        self.pop("ebp")
        self.pos = self.pos_stack.pop()

    def make_label(self):
        t = self.label_count
        self.label_count += 1
        return t
        

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
    state.store(x.retval, "eax")
    state.sub_stack(state.param_count)
    state.param_count = 0

def gen_Param(x, state):
    state.load("eax", x.value)
    state.push("eax")
    state.param_count += 4

def gen_Argument(x, state):
    state.add_arg(x)

def gen_Op(x, state):
    """
        <op> <result> <lhs> <rhs>
    """
    cmp_list = ["<", ">", "<=", ">=", "=="]

    if x.op in cmp_list:
        return gen_CMP(x, state)
    instructions = {
        "+" : "add eax,",
        "-" : "sub eax,",
        "*" : "mul"     ,
        "<" : "cmp eax,",
        "/" : "div"
    }
    instr = instructions[x.op]

    state.load("eax", x.lhs)
    state.load("ebx", x.rhs)

    state.outl("{} ebx", instr)
    state.outl("mov [ebp + {}], eax",  state.get_offset(x.assign))

def gen_CMP(x, state):
    state.load("ecx", "1")
    state.load("eax", x.lhs)
    state.load("ebx", x.rhs)
    state.outl("cmp eax, ebx")
    label = state.make_label()
    jump_table = { "<"  : "jl",
                   ">"  : "jg",
                   "<=" : "jle",
                   ">=" : "jge",
                   "==" : "je",
                   "!=" : "jne"}
    state.outl("{} .cmp{}", jump_table[x.op], label)
    state.load("ecx", "0")
    state.out(".cmp{}:", label)
    state.store(x.assign, "ecx")
    pass

def gen_Assign(x, state):
    offset = state.get_offset(x.identifier)
    state.load("eax", x.var)
    state.store(x.identifier, "eax")

def gen_EndFunc(x, state):
    state.out(".end:")
    state.unset_base_pointer()
    state.outl("ret")
    state.delete_frame()

def gen_Return(x, state):
    if x.value:
        state.load("eax", x.value)
    state.outl("jmp .end")

def gen_JZ(x, state):
    state.load("eax", x.var)
    state.outl("cmp eax, 0")
    state.outl("jz .L{}", x.label.value)

def gen_JP(x, state):
    state.outl("jmp .L{}", x.label.value)

def gen_JNZ(x, state):
    state.load("eax", x.var)
    state.outl("cmp eax, 0")
    state.outl("jnz .L{}", x.label.value)


def output_print(state):
    state.outl("mov eax, 4")
    state.outl("mov ebx, 1")
    state.outl("mov ecx, print")
    state.outl("mov edx, print_len")
    state.outl("int 80h")

def gen_asm(tac):

    state = CodeGenState()
    state.out("[BITS 32]")


    state.out("section .bss")
    state.out("str0: resb 0x20")
    setup_stack = False
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
    state.push("eax")
    state.outl("call exit")

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

    state.outl('%include "stdlib/stdlib.asm"')
    state.out("section .data")
    for x in state.strings:
        state.out("strconst_{}:", x.count)
        state.out("db {}, 0", str(x))

    return "\n".join(state.output)

def main():
    source = """\
    function fib(int a) -> int
    {
        if(a < 2)
        {
            return 1
        }
        return fib(a - 1) + fib(a - 2)
    }

    function factorial(int a) -> int
    {
        if(a < 2)
        {
            return 1
        }
        return a * factorial(a - 1)
    }

    function return_string() -> string
    {
        return "Hello, world"
    }

    function main() -> int
    {
        prints(return_string())

        return 0
    }
    """

    print(source)
    print("-" * 80)
    t = make_tac(source)
    for x in t:
        print(x)
    print("-" * 80)
    out = gen_asm(t)
    print_asm = True
    if print_asm:
        print("-" * 80)
        for lineno, line in enumerate(out.split("\n")):
            sys.stdout.write("{:02d}:{}\n".format(lineno + 1, line))
    open("out.s", "w").write(out)

if __name__ == "__main__":
    main()
