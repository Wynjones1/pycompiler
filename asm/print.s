[BITS 64]
section .data:
hello:
    message db 'Hello, world', 0xa
hello_len: equ $ - hello

section .text
