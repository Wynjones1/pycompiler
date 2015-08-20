[BITS 32]
section .bss
section .text
global _start
extern return_10
_start:
    call return_10
    mov ebx, eax
    mov eax, 1
    int 0x80
