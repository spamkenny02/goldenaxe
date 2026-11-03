#ifndef GAW_SOURCE_RNG_RUNTIME_H
#define GAW_SOURCE_RNG_RUNTIME_H
#include <types.h>
/* Cold-reset seed C028. New Game/Continue do not reset this stream. */
void game_rng_reset(void);
/* 04E1: update only the SMS seed,then XOR its low byte with sampled R.
 * Refresh sampling remains provisional until the source clock is integrated. */
u8 game_rng_seeded(void);
/* Direct LD A,R. R7 is zero after reset and the provided ROM has no LD R,A.
 * This is a domain-correct provisional input,not reconstructed SMS timing. */
u8 game_rng_read_refresh(void);
#endif
