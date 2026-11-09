/* DIAGNOSTIC CANDIDATE, NOT SELECTED IN V321.
 * Original038E: OUTI16T, NOP4T, JR NZ12T =32T per byte.
 * One SMS map word takes64T =960 master clocks. A 68000 cycle is7
 * master clocks: five136-cycle and two140-cycle intervals per7 words
 * approximate that period (exact total across each seven-word group).
 * The454-NOP lead-in is an experimental calibration, NOT a complete
 * source IRQ/foreground timing model. It must not become a release
 * constant solely from one successful image comparison.
 * Trial03 still differs by20 pixels from SMS NTSC frame6358.
 * Hook replaces only the64-byte memcpy in the8-row logo reveal.
 * The normal shadow-map conversion remains afterwards. V321 still
 * uses title_publication.s and is not changed by this experiment.
 */
.text
.global title_copy_logo_row
 title_copy_logo_row:
 movem.l %a2-%a3,-(%sp)
 movea.l 12(%sp),%a0
 movea.l 16(%sp),%a1
 lea 0x000abb96,%a2
 lea 0x00c00000,%a3
 move.l %a0,%d0
 sub.l #0xe0ffc41c,%d0
 and.l #0x0000ffff,%d0
 add.w %d0,%d0
 add.w #0x2100,%d0
 swap %d0
 move.w #3,%d0
 or.l #0x40000000,%d0
 move.w #0x8f02,4(%a3)
 move.l %d0,4(%a3)
 .rept 454
 nop
 .endr

 /* Expands to the same straight-line code as the measured trial03. */
 .macro title_word gap
 moveq #0,%d0
 move.w (%a1)+,%d0
 move.w %d0,(%a0)+
 add.l %d0,%d0
 move.w (%a2,%d0.l),(%a3)
 .if \gap
 bra.w 1f
 nop
1:
 exg %d0,%d1
 .rept \gap
 nop
 .endr
 .endif
 .endm
 title_word 18
 title_word 18
 title_word 19
 title_word 18
 title_word 18
 title_word 19
 title_word 18
 title_word 18
 title_word 18
 title_word 19
 title_word 18
 title_word 18
 title_word 19
 title_word 18
 title_word 18
 title_word 18
 title_word 19
 title_word 18
 title_word 18
 title_word 19
 title_word 18
 title_word 18
 title_word 18
 title_word 19
 title_word 18
 title_word 18
 title_word 19
 title_word 18
 title_word 18
 title_word 18
 title_word 19
 title_word 0
 move.l 12(%sp),%d0
 movem.l (%sp)+,%a2-%a3
 rts
