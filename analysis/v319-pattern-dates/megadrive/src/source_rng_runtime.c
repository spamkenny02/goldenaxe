#include "source_rng_runtime.h"
#include "source_rng.h"
/* SGDK tools.h ABI. Keep hardware headers out of this small state adapter. */
extern u16 random(void);
static u16 game_rng_seed;
void game_rng_reset(void) { game_rng_seed=0; }
u8 game_rng_read_refresh(void) { return (u8)random()&127; }
u8 game_rng_seeded(void)
{
    u16 next=source_rng_next_seed(game_rng_seed);
    u8 refresh=game_rng_read_refresh();
    game_rng_seed=next;
    return source_rng_value(next,refresh);
}
