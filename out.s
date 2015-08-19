[BITS 32]
section .data
section .bss
str0: resb 0x20
section .text
	global _start
_start:
	mov ebp, esp
	call main
	mov ebx, 0
	mov eax, 1
	int 0x80
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
;------------------------------------| startfunc main
main:
	push ebp
	mov ebp, esp
;------------------------------------| decl _t18 int
;------------------------------------| decl _t11 int
;------------------------------------| decl _t13 int
;------------------------------------| decl i int
;------------------------------------| decl _t15 int
;------------------------------------| decl _t17 int
;------------------------------------| decl _t14 int
;------------------------------------| decl _t16 int
;------------------------------------| decl _t12 int
;------------------------------------| end_decls
	sub esp, 36
;------------------------------------| i := 0
	mov eax, 0
	mov dword [ebp + -16], eax
;------------------------------------| JP .L3:
	jmp .L3
;------------------------------------| .L2:
.L2:
;------------------------------------| param i
	mov eax, [ebp + -16]
	push eax
;------------------------------------| _t11 = CALL factorial
	call factorial
	mov dword [ebp + -8], eax
	add esp, 4
;------------------------------------| param _t11
	mov eax, [ebp + -8]
	push eax
;------------------------------------| _t12 = CALL print
	call print
	mov dword [ebp + -36], eax
	add esp, 4
;------------------------------------| i := i + 1
	mov eax, [ebp + -16]
	mov ebx, 1
	add eax, ebx
	mov [ebp + -16], eax
;------------------------------------| .L3:
.L3:
;------------------------------------| _t13 := i < 10
	mov ecx, 1
	mov eax, [ebp + -16]
	mov ebx, 10
	cmp eax, ebx
	jl .L_2
	mov ecx, 0
.L_2:
	mov dword [ebp + -12], ecx
;------------------------------------| JNZ .L2: _t13
	mov eax, [ebp + -12]
	cmp eax, 0
	jnz .L2
;------------------------------------| _t14 := 10 * 10
	mov eax, 10
	mov ebx, 10
	mul ebx
	mov [ebp + -28], eax
;------------------------------------| _t15 := _t14 / 2
	mov eax, [ebp + -28]
	mov ebx, 2
	div ebx
	mov [ebp + -20], eax
;------------------------------------| _t16 := 1 + _t15
	mov eax, 1
	mov ebx, [ebp + -20]
	add eax, ebx
	mov [ebp + -32], eax
;------------------------------------| _t17 := _t16 + 1
	mov eax, [ebp + -32]
	mov ebx, 1
	add eax, ebx
	mov [ebp + -24], eax
;------------------------------------| param _t17
	mov eax, [ebp + -24]
	push eax
;------------------------------------| _t18 = CALL print
	call print
	mov dword [ebp + -4], eax
	add esp, 4
;------------------------------------| endfunc main
.end:
	mov esp, ebp
	pop ebp
	ret
	%include "src/stdlib.asm"