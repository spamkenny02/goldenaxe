/* SMS 05B2..05D0 dispatches terminator/space/FF/$ before width checking.
 * Preserve V321 layout; only empty native word runs bypass wrapping.
 * Nonempty width and every live game register retain their old semantics.
 */
    .text
    .global dialogue_empty_width,dialogue_empty_terminator
dialogue_empty_width:
    tst.l %d2
    bne.s old_compare
    cmpi.w #31,0xe0ff28b4
    bne.s old_compare
    tst.w 0xe0ffe404
    bne.s no_wrap
old_compare:
    cmpi.l #207,%d5
    jmp 0x29626
no_wrap:
    jmp 0x2939c
/* Scoped Saylun room31 correction for active house/service text.
 * Opening-story timing and other rooms retain the published behavior.
 */
dialogue_empty_terminator:
    cmpi.w #31,0xe0ff28b4
    bne.s old_terminator
    tst.w 0xe0ffe404
    bne.s empty_end
old_terminator:
    cmpi.w #207,%d7
    bls.s empty_end
    jmp 0x29b46
empty_end:
    jmp 0x29be0
