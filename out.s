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
;------------------------------------| startfunc fib
fib:
	push ebp
	mov ebp, esp
;------------------------------------| arg int a
;------------------------------------| decl t0 int
;------------------------------------| decl t1 int
;------------------------------------| end_decls
	sub esp, 8
;------------------------------------| < _t0 a 2
	mov eax, [ebp + 8]
	push eax
	mov ebx, 2
	cmp eax, ebx
	pop ebx
;------------------------------------| JZ .L0: _t0
	mov eax, eax
	cmp eax, 0
	jz .L0
;------------------------------------| return 1
	jp .end
;------------------------------------| .L0:
.L0:
;------------------------------------| - _t1 a 1
	mov eax, [ebp + 8]
	push eax
	mov ebx, 1
	sub eax, ebx
	pop ebx
;------------------------------------| param _t1
	push eax
;------------------------------------| CALL fib
	call fib
	add esp, 4
;------------------------------------| := t0 _t1
	mov [ebp + -4], eax
;------------------------------------| - _t2 a 2
	mov eax, [ebp + 8]
	push eax
	mov ebx, 2
	sub eax, ebx
	pop ebx
;------------------------------------| param _t2
	push eax
;------------------------------------| CALL fib
	call fib
	add esp, 4
;------------------------------------| := t1 _t2
	mov [ebp + -8], eax
;------------------------------------| + _t3 t0 t1
	mov eax, [ebp + -4]
	push eax
	mov ebx, [ebp + -8]
	add eax, ebx
	pop ebx
;------------------------------------| return _t3
	jp .end
;------------------------------------| endfunc fib
.end:
	mov esp, ebp
	pop ebp
	ret
;------------------------------------| startfunc main
main:
	push ebp
	mov ebp, esp
;------------------------------------| decl a' int
;------------------------------------| end_decls
	sub esp, 4
;------------------------------------| param 0
	push 0
;------------------------------------| CALL fib
	call fib
	add esp, 4
;------------------------------------| param 0
	push 0
;------------------------------------| CALL print
	call print
	add esp, 4
;------------------------------------| endfunc main
.end:
	mov esp, ebp
	pop ebp
	ret
	%include "src/stdlib.asm"