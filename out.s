[BITS 32]
section .bss
str0: resb 0x20
section .text
	global _start
_start:
	mov ebp, esp
	call main
	push eax
	call exit
;------------------------------------| startfunc fib
fib:
	push ebp
	mov ebp, esp
;------------------------------------| arg int a
;------------------------------------| decl _t2 int
;------------------------------------| decl _t1 int
;------------------------------------| decl _t3 int
;------------------------------------| decl _t5 int
;------------------------------------| decl _t4 int
;------------------------------------| decl _t6 int
;------------------------------------| end_decls
	sub esp, 24
;------------------------------------| _t1 := a < 2
	mov ecx, 1
	mov eax, [ebp + 8]
	mov ebx, 2
	cmp eax, ebx
	jl .L_0
	mov ecx, 0
.L_0:
	mov dword [ebp + -8], ecx
;------------------------------------| JZ .L0: _t1
	mov eax, [ebp + -8]
	cmp eax, 0
	jz .L0
;------------------------------------| return 1
	mov eax, 1
	jmp .end
;------------------------------------| .L0:
.L0:
;------------------------------------| _t2 := a - 1
	mov eax, [ebp + 8]
	mov ebx, 1
	sub eax, ebx
	mov [ebp + -4], eax
;------------------------------------| param _t2
	mov eax, [ebp + -4]
	push eax
;------------------------------------| _t3 = CALL fib
	call fib
	mov dword [ebp + -12], eax
	add esp, 4
;------------------------------------| _t4 := a - 2
	mov eax, [ebp + 8]
	mov ebx, 2
	sub eax, ebx
	mov [ebp + -20], eax
;------------------------------------| param _t4
	mov eax, [ebp + -20]
	push eax
;------------------------------------| _t5 = CALL fib
	call fib
	mov dword [ebp + -16], eax
	add esp, 4
;------------------------------------| _t6 := _t3 + _t5
	mov eax, [ebp + -12]
	mov ebx, [ebp + -16]
	add eax, ebx
	mov [ebp + -24], eax
;------------------------------------| return _t6
	mov eax, [ebp + -24]
	jmp .end
;------------------------------------| endfunc fib
.end:
	mov esp, ebp
	pop ebp
	ret
;------------------------------------| startfunc factorial
factorial:
	push ebp
	mov ebp, esp
;------------------------------------| arg int a
;------------------------------------| decl _t9 int
;------------------------------------| decl _t8 int
;------------------------------------| decl _t10 int
;------------------------------------| decl _t7 int
;------------------------------------| end_decls
	sub esp, 16
;------------------------------------| _t7 := a < 2
	mov ecx, 1
	mov eax, [ebp + 8]
	mov ebx, 2
	cmp eax, ebx
	jl .L_1
	mov ecx, 0
.L_1:
	mov dword [ebp + -16], ecx
;------------------------------------| JZ .L1: _t7
	mov eax, [ebp + -16]
	cmp eax, 0
	jz .L1
;------------------------------------| return 1
	mov eax, 1
	jmp .end
;------------------------------------| .L1:
.L1:
;------------------------------------| _t8 := a - 1
	mov eax, [ebp + 8]
	mov ebx, 1
	sub eax, ebx
	mov [ebp + -8], eax
;------------------------------------| param _t8
	mov eax, [ebp + -8]
	push eax
;------------------------------------| _t9 = CALL factorial
	call factorial
	mov dword [ebp + -4], eax
	add esp, 4
;------------------------------------| _t10 := a * _t9
	mov eax, [ebp + 8]
	mov ebx, [ebp + -4]
	mul ebx
	mov [ebp + -12], eax
;------------------------------------| return _t10
	mov eax, [ebp + -12]
	jmp .end
;------------------------------------| endfunc factorial
.end:
	mov esp, ebp
	pop ebp
	ret
;------------------------------------| startfunc return_string
return_string:
	push ebp
	mov ebp, esp
;------------------------------------| end_decls
	sub esp, 0
;------------------------------------| return "Hello, world"
	mov eax, strconst_0
	jmp .end
;------------------------------------| endfunc return_string
.end:
	mov esp, ebp
	pop ebp
	ret
;------------------------------------| startfunc main
main:
	push ebp
	mov ebp, esp
;------------------------------------| decl _t11 int
;------------------------------------| decl _t12 int
;------------------------------------| end_decls
	sub esp, 8
;------------------------------------| _t11 = CALL return_string
	call return_string
	mov dword [ebp + -4], eax
	add esp, 0
;------------------------------------| param _t11
	mov eax, [ebp + -4]
	push eax
;------------------------------------| _t12 = CALL prints
	call prints
	mov dword [ebp + -8], eax
	add esp, 4
;------------------------------------| return 0
	mov eax, 0
	jmp .end
;------------------------------------| endfunc main
.end:
	mov esp, ebp
	pop ebp
	ret
	%include "src/stdlib.asm"
section .data
strconst_0:
db "Hello, world", 0