#include "source_axe_terrain.h"

u8 source_axe_terrain_probes(u8 graphics_class,u8 phase,u8 direction,u8 x,u8 y,u8 *indices)
{
    u8 alignment=((x&8)>>3)|((y&8)>>2),count=1;
    signed char bx=0,cy=0,bx2=0,cy2=0;
    if(graphics_class || phase!=7 || direction>3) return 0;
    switch(direction*4+alignment)
    {
        case 0:if(y<24) return 0;bx=-16;cy=-32;bx2=0;cy2=-32;count=2;break;
        case 1:if(y<24) return 0;bx=-8;cy=-32;break;
        case 2:bx=-16;cy=-24;bx2=0;cy2=-24;count=2;break;
        case 3:bx=-8;cy=-24;break;
        case 4:if(y>=160) return 0;bx=-16;cy=0;bx2=0;cy2=0;count=2;break;
        case 5:if(y>=160) return 0;bx=-8;cy=0;break;
        case 9:bx=-24;cy=-16;break;
        case 10:bx=-16;cy=-24;bx2=-16;cy2=-8;count=2;break;
        case 11:bx=-24;cy=-24;bx2=-24;cy2=-8;count=2;break;
        case 13:bx=8;cy=-16;break;
        case 14:bx=0;cy=-24;bx2=0;cy2=-8;count=2;break;
        case 15:bx=8;cy=-24;bx2=8;cy2=-8;count=2;break;
        default:return 0;
    }
    indices[0]=((u8)(y+cy)&240)|((u8)(x+bx)>>4);
    if(count==2) indices[1]=((u8)(y+cy2)&240)|((u8)(x+bx2)>>4);
    return count;
}
