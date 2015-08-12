%define ASCII_A       0x41
%define ASCII_0       0x30
%define ASCII_NEWLINE 0xa
%define BUFSIZE 10
; print the integer pointed to by the first argument
print:
    push ebp
        mov ebp, esp
        mov eax, [ebp + 8]
        mov ebx, 10
        mov ecx, 0
        sub esp, BUFSIZE; reserve space for the integer

        mov esi, BUFSIZE - 1
        sub esi, ecx
        mov byte [ebp - 1], ASCII_NEWLINE
        add ecx, 1         ; adjust length

.loop:
        ; push character on the stack
        ; store length in ecx

        mov edx, 0       ; zero upper bits of EDX:EAX
        div ebx          ; divide by 10
        add edx, ASCII_0 ; adjust to ascii

        mov esi, BUFSIZE - 1
        sub esi, ecx
        mov [esp + esi], dl; store in the buffer

        add ecx, 1       ; adjust length
        cmp eax, 0       ; see if we are done
        jnz .loop


        mov eax, 4   ; write syscall
        mov ebx, 0   ; stdout fd
        mov edx, ecx ; length of string
        mov ecx, ebp
        sub ecx, edx ; location of output string
        int 0x80
        mov esp, ebp
    pop ebp
    ret
