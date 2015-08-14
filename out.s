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
;------------------------------------| end_decls
	sub esp, 0
;------------------------------------| param a
	mov eax, [ebp + 8]
	push eax
;------------------------------------| CALL print
	call print
	add esp, 4
;------------------------------------| endfunc fib
.end:
	mov esp, ebp
	pop ebp
	ret
;------------------------------------| startfunc main
main:
	push ebp
	mov ebp, esp
;------------------------------------| end_decls
	sub esp, 0
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