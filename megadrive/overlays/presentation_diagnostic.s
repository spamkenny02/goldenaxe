.text
.extern presentation_diag
.macro show_stage number
 movem.l %d0-%d7/%a0-%a6,-(%sp)
 move.l #\number,-(%sp)
 jsr presentation_diag
 addq.l #4,%sp
 movem.l (%sp)+,%d0-%d7/%a0-%a6
.endm
.global presentation_diag_audio,presentation_diag_irq,presentation_diag_sram,presentation_diag_intro
presentation_diag_audio:
 show_stage 6
 /* Displaced region test; preserve the resulting flags for the caller. */
 move.w (%a0),%d0
 btst #0,%d0
 rts
presentation_diag_irq:
 show_stage 7
 jmp 0x4bfc
presentation_diag_sram:
 jsr 0x32054
 show_stage 8
 rts
presentation_diag_intro:
 show_stage 9
 jmp 0x9b6e
