#include <genesis.h>
#include "helper.inc"

volatile u16 harness_done,harness_failed;
volatile u32 harness_cases;

static void check_rows(u8 *rows)
{
    u8 expected[8],mask=0,actual;u16 n;
    for(n=0;n<8;n++)
    { if(rows[n]&128) mask|=1<<n;expected[n]=rows[n]+rows[n]; }
    actual=count_world_sprite_rows(rows);
    if(actual!=mask || rows[-1]!=0xa7 || rows[8]!=0xa7) harness_failed=1;
    for(n=0;n<8;n++) if(rows[n]!=expected[n]) harness_failed=2;
    harness_cases++;
}

int main(bool hardReset)
{
    u8 storage[12];u16 offset,pattern,phase,n;
    (void)hardReset;
    for(offset=1;offset<=2;offset++)
    {
        for(pattern=0;pattern<256;pattern++) for(phase=0;phase<8;phase++)
        {
            memset(storage,0xa7,sizeof(storage));
            for(n=0;n<8;n++) storage[offset+n]=(pattern&(1<<n))?(u8)(255<<((phase+n)&7)):0;
            check_rows(storage+offset);
        }
        for(pattern=0;pattern<256;pattern++) for(phase=0;phase<8;phase++)
        {
            memset(storage,0xa7,sizeof(storage));
            for(n=0;n<8;n++) storage[offset+n]=(n&1)?0xff:0x80;
            storage[offset+phase]=pattern;check_rows(storage+offset);
        }
    }
    harness_done=1;
    while(TRUE) SYS_doVBlankProcess();
    return 0;
}
