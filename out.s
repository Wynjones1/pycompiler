[BITS 32]
section .data
section .bss
str0: resb 0x20
_stack_start:
	resb 0xffff
_stack_end:
section .text
	global _start
_start:
	mov esp, _stack_start
	mov ebp, esp
	call main
	mov ebx, 0
	mov eax, 1
	int 0x80
;------------------------------------| startfunc f0
f0:
	push ebp
	mov ebp, esp
	add esp, 12
;------------------------------------| arg int f0_param_0
;------------------------------------| arg int f0_param_1
;------------------------------------| JZ L0: f0_scope_0
	mov eax, [ebp + -4]
	cmp eax, 0
	jz L0
;------------------------------------| * _t0 10 a
	mov eax, 10
	push ebx
	mov ebx, [ebp + -12]
	mul ebx
	pop ebx
;------------------------------------| := a _t0
	mov [ebp + -12], eax
;------------------------------------| L0:
L0:
;------------------------------------| endfunc f0
.end:
	pop ebp
	ret
;------------------------------------| startfunc main
main:
	push ebp
	mov ebp, esp
	add esp, 12
;------------------------------------| := b 1234
	mov dword [ebp + -4], 1234
;------------------------------------| := c 123
	mov dword [ebp + -8], 123
;------------------------------------| + _t2 b 123
	mov eax, [ebp + -4]
	push ebx
	mov ebx, 123
	add eax, ebx
	pop ebx
;------------------------------------| param _t2
	push eax
;------------------------------------| CALL print
	call print
	add esp, 4
;------------------------------------| param c
	mov eax, [ebp + -8]
	push eax
;------------------------------------| CALL print
	call print
	add esp, 4
;------------------------------------| param a123
	mov eax, [ebp + -12]
	push eax
;------------------------------------| CALL print
	call print
	add esp, 4
;------------------------------------| + _t3 b 1
	mov eax, [ebp + -4]
	push ebx
	mov ebx, 1
	add eax, ebx
	pop ebx
;------------------------------------| param _t3
	push eax
;------------------------------------| + _t4 b 2
	mov eax, [ebp + -4]
	push ebx
	mov ebx, 2
	add eax, ebx
	pop ebx
;------------------------------------| param _t4
	push eax
;------------------------------------| CALL f0
	call f0
	add esp, 8
;------------------------------------| endfunc main
.end:
	pop ebp
	ret
	%include "src/stdlib.asm"