/* Native68000 overlay for auditedV319. Runs only on credits entry/exit.
 * Preserve every pre-credits instruction and all source ring arithmetic.
 * MD layout:BG_B=C000,64columns; bottom screen rows26/27. */
.text
.global credits_border_enter,credits_border_exit
credits_border_enter:
 move.w %sr,-(%sp)
 ori.w #0x0700,%sr
 movem.l %d0-%d1/%a0-%a1,-(%sp)
 move.w #0xe001,%d0
 bsr credits_border_fill
 movem.l (%sp)+,%d0-%d1/%a0-%a1
 move.w (%sp)+,%sr
 /* Replaced original LEA; CCR and stack argument remain unchanged. */
 lea 0x00037bd6,%a3
 rts
credits_border_exit:
 move.w %sr,-(%sp)
 ori.w #0x0700,%sr
 movem.l %d0-%d1/%a0-%a1,-(%sp)
 moveq #0,%d0
 bsr credits_border_fill
 movem.l (%sp)+,%d0-%d1/%a0-%a1
 move.w (%sp)+,%sr
 /* Replaced original CLR,including its original CCR side effects. */
 clr.b 0xe0ff2b78
 rts
credits_border_fill:
 lea 0x00c00004,%a0
 lea 0x00c00000,%a1
 move.w #0x8f02,(%a0)
 move.l #0xc0620000,(%a0)
 move.w #0,(%a1)
 move.w %d0,%d1
 swap %d0
 move.w %d1,%d0
 move.l #0x4d000003,(%a0)
 moveq #15,%d1
1: move.l %d0,(%a1)
 dbra %d1,1b
 move.l #0x4d800003,(%a0)
 moveq #15,%d1
2: move.l %d0,(%a1)
 dbra %d1,2b
 rts
