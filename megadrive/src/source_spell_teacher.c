#include "source_spell_teacher.h"

u16 source_spell_teacher(u8 teacher,u8 accepted,u8 *s,u16 *prompt)
{
    u16 text=0;u8 learn=0,n,cost=0;
    *prompt=0;
    if(teacher==0)
    {
        if(!s[0])
        {
            if(!s[5]) { s[5]=1;return 0xAD89; }
            if(!s[4]) return 0xADDA;
            s[4]=0;text=0xAE39;learn=1;
        }
        else if(s[0]==1) { text=s[8]<72?0xAF95:0xAFD6;learn=s[8]>=72; }
        else text=0xB04A;
    }
    else if(teacher==1)
    {
        if(s[1]>=2) text=0xB333;
        else if(s[1]==1 && s[8]<72) text=0xB225;
        else
        {
            if(!s[1]) { *prompt=s[6]?0xB165:0xB06F;s[6]=1;cost=50;text=0xB35D; }
            else { *prompt=0xB233;cost=100;text=0xB3E5; }
            if(!accepted) return 0xB3A0;
            if(s[11]<cost) return 0x8BCD;
            s[11]-=cost;learn=1;
        }
    }
    else if(teacher==2)
    {
        if(!s[2])
        {
            if(s[8]<72) return 0xB431;
            text=0xB457;learn=1;
        }
        else if(s[2]==1)
        {
            for(n=0;n<9;n++) if(!(s[12+n]&128)) break;
            text=n<9?0xB5EB:0xB621;
            if(n==9) { s[7]=1;learn=1; }
        }
        else text=0xB747;
    }
    else if(teacher==3) { text=s[3]?0xB8CA:0xB77E;learn=!s[3]; }
    else return 0;
    if(learn)
    {
        u8 previous=s[teacher]++;
        if(!previous) { u8 capacity=(u8)(s[9]+24);if(capacity<128) s[9]=capacity; }
    }
    s[10]=s[9]; /* 7B2A is bypassed by the early dialogue branches. */
    return text;
}
