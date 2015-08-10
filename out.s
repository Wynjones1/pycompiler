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
;------------------------------------| arg int a
;------------------------------------| arg int b
;------------------------------------| startfunc f0
f0:
	push ebp
	mov ebp, esp
;------------------------------------| endfunc f0
.end:
	pop ebp
	ret
;------------------------------------| startfunc main
main:
	push ebp
	mov ebp, esp
;------------------------------------| := b 10
	mov dword [esp + -4], 10
;------------------------------------| * _t0 b 10
	mov eax, [esp + -4]
	push ebx
	mov ebx, 10
	mul ebx
	pop ebx
;------------------------------------| := b _t0
	mov [esp + -4], eax
;------------------------------------| param 0
	push 0
;------------------------------------| CALL print
	call print
	add esp, 4
;------------------------------------| param 10
	push 10
;------------------------------------| CALL print
	call print
	add esp, 4
;------------------------------------| param 123
	push 123
;------------------------------------| CALL print
	call print
	add esp, 4
;------------------------------------| param 1234567
	push 1234567
;------------------------------------| CALL print
	call print
	add esp, 4
;------------------------------------| param 4294967295
	push 4294967295
;------------------------------------| CALL print
	call print
	add esp, 4
;------------------------------------| + _t2 b 1
	mov eax, [esp + -4]
	push ebx
	mov ebx, 1
	add eax, ebx
	pop ebx
;------------------------------------| param _t2
	push eax
;------------------------------------| + _t3 b 2
	mov eax, [esp + -4]
	push ebx
	mov ebx, 2
	add eax, ebx
	pop ebx
;------------------------------------| param _t3
	push eax
;------------------------------------| CALL f0
	call f0
	add esp, 8
;------------------------------------| endfunc main
.end:
	pop ebp
	ret
	%include "src/stdlib.asm"