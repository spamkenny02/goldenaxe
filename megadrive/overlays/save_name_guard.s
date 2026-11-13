.text
.extern save_name_valid
.global save_name_draw_guard,save_name_load_guard
save_name_draw_guard:
 movem.l %d0-%d1/%a0-%a1,-(%sp)
 move.l #1,-(%sp)
 pea -20(%a6)
 jsr save_name_valid
 addq.l #8,%sp
 tst.w %d0
 bne.s 1f
 clr.b -20(%a6)
1: movem.l (%sp)+,%d0-%d1/%a0-%a1
 /* Exact displaced terminator and first-name-byte load. */
 clr.b -12(%a6)
 move.b -20(%a6),%d0
 jmp 0x254bc
save_name_load_guard:
 movem.l %d0-%d1/%a0-%a1,-(%sp)
 move.l #2,-(%sp)
 move.l %a0,-(%sp)
 jsr save_name_valid
 addq.l #8,%sp
 tst.w %d0
 beq.s 2f
 movem.l (%sp)+,%d0-%d1/%a0-%a1
 move.b (%a0),%d0
 subq.b #1,%d0
 cmpi.b #-3,%d0
 jmp 0x49c68
2: movem.l (%sp)+,%d0-%d1/%a0-%a1
 /* Existing refusal path also disables SRAM before resuming the selector. */
 jmp 0x4a452
