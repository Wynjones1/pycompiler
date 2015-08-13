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
	sub esp, 0
;------------------------------------| arg int f0_param_0
;------------------------------------| arg int f0_param_1
;------------------------------------| param f0_param_0
	mov eax, [ebp + 8]
	push eax
;------------------------------------| CALL print
	call print
	add esp, 4
;------------------------------------| endfunc f0
.end:
	mov esp, ebp
	pop ebp
	ret
;------------------------------------| startfunc main
main:
	push ebp
	mov ebp, esp
	sub esp, 4
;------------------------------------| := b 2
	mov dword [ebp + -4], 2
;------------------------------------| param 10
	push 10
;------------------------------------| * _t0 b b
	mov eax, [ebp + -4]
	push eax
	mov ebx, [ebp + -4]
	mul ebx
	pop ebx
;------------------------------------| param _t0
	push eax
;------------------------------------| CALL f0
	call f0
	add esp, 8
;------------------------------------| endfunc main
.end:
	mov esp, ebp
	pop ebp
	ret
	%include "src/stdlib.asm"