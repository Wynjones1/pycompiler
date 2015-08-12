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
;------------------------------------| arg int a
;------------------------------------| arg int b
;------------------------------------| endfunc f0
.end:
	pop ebp
	ret
;------------------------------------| startfunc main
main:
	push ebp
	mov ebp, esp
;------------------------------------| := b 1234
	mov dword [esp + -4], 1234
;------------------------------------| param b
	mov eax, [esp + -4]
	push eax
;------------------------------------| CALL print
	call print
	add esp, 4
;------------------------------------| + _t0 b 1
	mov eax, [esp + -4]
	push ebx
	mov ebx, 1
	add eax, ebx
	pop ebx
;------------------------------------| param _t0
	push eax
;------------------------------------| + _t1 b 2
	mov eax, [esp + -4]
	push ebx
	mov ebx, 2
	add eax, ebx
	pop ebx
;------------------------------------| param _t1
	push eax
;------------------------------------| CALL f0
	call f0
	add esp, 8
;------------------------------------| endfunc main
.end:
	pop ebp
	ret
	%include "src/stdlib.asm"