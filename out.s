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
	add esp, 0
	pop ebp
	ret
;------------------------------------| startfunc main
main:
	push ebp
	mov ebp, esp
	sub esp, 4
;------------------------------------| := b 2
	mov dword [ebp + -4], 2
;------------------------------------| + _t0 b 21
	mov eax, [ebp + -4]
	push ebx
	mov ebx, 21
	add eax, ebx
	pop ebx
;------------------------------------| param _t0
	push eax
;------------------------------------| * _t1 b b
	mov eax, [ebp + -4]
	push ebx
	mov ebx, [ebp + -4]
	mul ebx
	pop ebx
;------------------------------------| * _t2 _t1 b
	push ebx
	mov ebx, [ebp + -4]
	mul ebx
	pop ebx
;------------------------------------| * _t3 _t2 b
	push ebx
	mov ebx, [ebp + -4]
	mul ebx
	pop ebx
;------------------------------------| param _t3
	push eax
;------------------------------------| CALL f0
	call f0
	add esp, 8
;------------------------------------| endfunc main
.end:
	add esp, 4
	pop ebp
	ret
	%include "src/stdlib.asm"