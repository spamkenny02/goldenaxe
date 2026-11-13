.text
.global presentation_entry,presentation_pcm
.extern presentation_show
presentation_entry:
 move.w %sr,-(%sp)
 ori.w #0x0700,%sr
 movem.l %d0-%d7/%a0-%a6,-(%sp)
 jsr presentation_show
 movem.l (%sp)+,%d0-%d7/%a0-%a6
 move.w (%sp)+,%sr
 /* Displaced original main prologue, with its exact stack layout. */
 link.w %a6,#-192
 movem.l %d2-%d7/%a2-%a5,-(%sp)
 jmp 0x48772
/*12+4+(43*10+14)+8+10=47868000cycles/sample (taken branch). */
presentation_pcm:
 move.l %d2,-(%sp)
 movea.l 8(%sp),%a0
 move.l 12(%sp),%d0
 lea 0xa04001,%a1
 moveq #43,%d2
1: move.b (%a0)+,(%a1)
 move.w %d2,%d1
2: dbra %d1,2b
 subq.l #1,%d0
 bne.s 1b
 move.l (%sp)+,%d2
 rts
