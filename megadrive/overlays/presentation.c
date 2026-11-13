/* Boot-only native68000 splash. No game callback/timer or save state is run here. */
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned long u32;
#define B(a) (*(volatile u8*)(a))
#define W(a) (*(volatile u16*)(a))
#define L(a) (*(volatile u32*)(a))
extern const u32 presentation_tiles[];
extern const u16 presentation_map[],presentation_palette[];
extern const u8 presentation_ntsc[],presentation_ntsc_end[],presentation_pal[],presentation_pal_end[];
extern void presentation_pcm(const u8*,u32);
static void reg(u16 n,u16 value){W(0xc00004)=0x8000|(n<<8)|value;}
static void address(u16 value){L(0xc00004)=0x40000000UL|((u32)(value&0x3fff)<<16)|(value>>14);}
static void black(void){u16 i;L(0xc00004)=0xc0000000UL;for(i=0;i<64;i++)W(0xc00000)=0;}
static void palette(u16 level){u16 i;L(0xc00004)=0xc0000000UL;for(i=0;i<64;i++){u16 v=presentation_palette[i];u16 r=((v>>1)&7)*level>>3,g=((v>>5)&7)*level>>3,b=((v>>9)&7)*level>>3;W(0xc00000)=(r<<1)|(g<<5)|(b<<9);}}
static void blank(void){while(W(0xc00004)&8);while(!(W(0xc00004)&8));W(0xffe4c2)++;}
static void wait(u16 frames){while(frames--)blank();}
static void ym(u16 port,u8 index,u8 value){while(B(0xa04000)&128);B(0xa04000+port*2)=index;while(B(0xa04000)&128);B(0xa04001+port*2)=value;}
void presentation_show(void){
 const volatile u8*old=(const volatile u8*)0xff2b66;
 u16 i,x,y,pal=W(0xc00004)&1;
 u16 a=W(0xff4508),b=W(0xff450e),sprite=(old[5]&127)<<9;
 const u8*voice=pal?presentation_pal:presentation_ntsc;
 u32 count=pal?(u32)(presentation_pal_end-presentation_pal):(u32)(presentation_ntsc_end-presentation_ntsc);
 W(0xffe4c0)=1;W(0xffe4c2)=0;
 /* Hold the idleZ80 so YM port ownership is unambiguous during the voice. */
 W(0xa11100)=0x100;while(W(0xa11100)&0x100);
 reg(1,old[1]&~64);reg(12,old[12]&~0x81);reg(15,2);reg(7,0);
 black();address(0);for(i=0;i<8;i++)L(0xc00000)=0;
 address(32);for(i=0;i<896*8;i++)L(0xc00000)=presentation_tiles[i];
 address(a);for(i=0;i<2048;i++)W(0xc00000)=0;
 address(b);for(i=0;i<2048;i++)W(0xc00000)=0;
 address(sprite);L(0xc00000)=0;L(0xc00000)=0;
 for(y=0;y<28;y++){address(a+y*128);for(x=0;x<32;x++)W(0xc00000)=presentation_map[y*32+x];}
 reg(1,old[1]|64);W(0xffe4c0)=2;
 for(i=0;i<=8;i++){blank();palette(i);wait(pal?(i&1?1:2):2);}
 W(0xffe4c0)=3;
 ym(1,0xb6,0xc0);ym(0,0x2a,0x80);ym(0,0x2b,0x80);
 while(B(0xa04000)&128);B(0xa04000)=0x2a;
 presentation_pcm(voice,count);
 ym(0,0x2a,0x80);ym(0,0x2b,0);
 W(0xffe4c0)=4;
 for(i=8;i>0;i--){blank();palette(i-1);wait(pal?(i&1?1:2):2);}
 black();reg(1,old[1]&~64);
 address(a);for(i=0;i<2048;i++)W(0xc00000)=0;
 address(b);for(i=0;i<2048;i++)W(0xc00000)=0;
 W(0xa11100)=0;
 /* Restore cached SGDK register values in hardware before returning to main. */
 for(i=0;i<24;i++)if(i!=1)reg(i,old[i]);
 W(0xc00004);reg(1,old[1]);
 /* Restore the original virtual game epoch: the handoff otherwise contributes
  * one extra NTSC VInt or two PAL VInts before the original intro starts.
  * This keeps world_clock/RNG and existing fixed controller routes aligned. */
 L(0xffcb72)-=pal?2:1;
 W(0xffe4c0)=5;
}
