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

; get the length of a null terminated string
strlen:
    mov esi, [esp + 4]
    xor ebx, ebx
.start:
    mov al, [esi + ebx]
    cmp al, 0
    jz .done
    add ebx, 1
    jmp .start
.done:
    mov eax, ebx
    ret

putc:
    mov edx, 1
    mov eax, 4
    mov ebx, 0
    push 0xa
    mov ecx, esp
    int 0x80
    add esp, 4
    ret

; print a string to stdout
prints:
    push dword [esp + 4]
    call strlen
    add esp, 4
    mov edx, eax       ; length of the string
    mov eax, 4         ; write syscall
    mov ebx, 0         ; stdout fd
    mov ecx, [esp + 4] ; location of string to print
    int 0x80
    push 0xa ;print a newline
    call putc
    add esp, 4
    ret

exit:
    mov ebx, [esp + 4]
	mov eax, 1
	int 0x80
