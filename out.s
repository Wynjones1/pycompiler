[BITS 32]
section .data
print:
	message db 'Hello, world', 0xa
print_len: equ $ - print
section .bss
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
main:
	push ebp
	mov ebp, esp
	push 10
	call print
.end:
	pop ebp
	ret