[BITS 32]
section .bss
section .text
global _start
_start:
    call main
    mov ebx, 0
    mov eax, 1
    int 0x80
main:
    ret
