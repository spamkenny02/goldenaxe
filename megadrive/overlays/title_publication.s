/* V320 native 68000 overlay: title-only queued map rows become immediate.
 * Called with the DMA_queueDmaFast C ABI, only DMA_VRAM callers.
 * Reuse the unchanged SGDK DMA_doCPUCopyDirect at 28B28. The title's
 * foreground updates run just after its fresh VBlank wait. No game DMA
 * routine, IRQ, wait counter, map data or credits code is replaced.
 */
.text
.global title_publish_row
title_publish_row:
 move.l 12(%sp),%d0
 and.l #0x0000ffff,%d0
 move.l %d0,%d1
 and.l #0x00003fff,%d0
 swap %d0
 lsr.l #8,%d1
 lsr.l #6,%d1
 or.l %d1,%d0
 or.l #0x40000000,%d0
 /* Forward step, word count, source, command (four 32-bit ABI slots). */
 move.l 20(%sp),-(%sp)
 move.l 20(%sp),-(%sp)
 move.l 16(%sp),-(%sp)
 move.l %d0,-(%sp)
 jsr 0x00028b28
 lea 16(%sp),%sp
 moveq #1,%d0
 rts
