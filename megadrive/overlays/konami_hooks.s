.text
.global konami_boot,konami_system
.extern konami_poll
konami_boot:
 clr.l 0xffe4b0
 clr.l 0xffe4b4
 clr.l 0xffe4b8
 clr.l 0xffe4bc
 clr.l 0xffe4c0
 clr.l 0xffe4c4
 clr.l 0xffe4c8
 clr.l 0xffe4cc
 move.l #0xe0ffe4d1,%d1
 rts
konami_system:
 jsr 0x47fb4
 movem.l %d0-%d1/%a0-%a1,-(%sp)
 jsr konami_poll
 movem.l (%sp)+,%d0-%d1/%a0-%a1
 rts
.global konami_title_pointer,konami_title_flash
konami_title_pointer:
 lea konami_system,%a2
 move.b #1,0xe0ff447d
 jmp 0x48982
konami_title_flash:
 jsr konami_system
 move.w (%a5),%d0
 jmp 0x4b16e
