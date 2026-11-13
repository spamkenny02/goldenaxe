/* Optional native68000 extension to the immutableV322RC1 image.
 *32bytes reserved ahead of SGDK heap by the boot trampoline. Never SRAM. */
typedef unsigned char u8;typedef unsigned short u16;typedef unsigned long u32;
#define W(a) (*(volatile u16*)(a))
#define B(a) (*(volatile u8*)(a))
#define L(a) (*(volatile u32*)(a))
#define DATA W(0xc00000)
#define CTRL W(0xc00004)
#define LIFE B(0xffe4b0)
#define GOLD B(0xffe4b1)
#define STEP W(0xffe4b2)
#define PREV W(0xffe4b4)
#define OPEN W(0xffe4b6)
#define SELECT W(0xffe4b8)
#define COUNT W(0xffe4ba)
#define JOY W(0xff446c)
#define INPUT W(0xff447e)
#define TITLE B(0xff447d)
#define REQUEST B(0xff447c)
#define UP 1
#define DOWN 2
#define LEFT 4
#define RIGHT 8
#define A 64
#define BB 16
#define C 32
#define START 128
#include "konami_font.inc"
static void address(u16 a){L(0xc00004)=0x40000000UL|((u32)(a&0x3fff)<<16)|(a>>14);}
static void color(u16 n,u16 v){L(0xc00004)=0xc0000000UL|((u32)(n*2)<<16);DATA=v;}
static u16 plane(u16 which){return W(which?0xff450e:0xff4508);}
static void tile(u16 p,u16 x,u16 y,u16 value){address(plane(p)+y*128+x*2);DATA=value;}
static void rect(u16 p,u16 x,u16 y,u16 w,u16 h,u16 value){u16 i,j;for(j=0;j<h;j++){address(plane(p)+(y+j)*128+x*2);for(i=0;i<w;i++)DATA=value;}}
static void text(u16 x,u16 y,const char*s,u16 tone){while(*s && x<32)tile(0,x++,y,0x6000+700+tone*100+(u8)*s++-32);}
static void patterns(void){u16 c,y,x,t;u32 pixels;for(t=0;t<3;t++){address((700+100*t)*32);for(c=0;c<96;c++)for(y=0;y<8;y++){pixels=0;for(x=0;x<8;x++)pixels=(pixels<<4)|((font[c*8+y]&(128>>x))?(t==2?4:t+1):0);L(0xc00000)=pixels;}}address(1100*32);for(y=0;y<8;y++)L(0xc00000)=y==0?0x00022222UL:y==1?0x00233333UL:y==2?0x02355555UL:0x23555555UL;for(y=0;y<8;y++)L(0xc00000)=y==0?0x22222222UL:y==1?0x33333333UL:0x55555555UL;for(y=0;y<8;y++)L(0xc00000)=0x23555555UL;for(y=0;y<8;y++)L(0xc00000)=0x55555555UL;for(y=0;y<8;y++)L(0xc00000)=0x33333333UL;}
static void box(void){u16 x,y;rect(1,2,12,28,11,0x6000+1103);for(x=2;x<30;x++){tile(0,x,11,0x6000+1101);tile(0,x,23,0x7000+1101);}for(y=12;y<23;y++){tile(0,1,y,0x6000+1102);tile(0,30,y,0x6800+1102);}tile(0,1,11,0x6000+1100);tile(0,30,11,0x6800+1100);tile(0,1,23,0x7000+1100);tile(0,30,23,0x7800+1100);}
static void choices(void){text(3,15,SELECT==0?">":" ",1);text(3,18,SELECT==1?">":" ",1);text(5,15,"VIE INFINIE",SELECT==0?1:0);text(5,18,"ARGENT INFINI",SELECT==1?1:0);text(25,15,LIFE?"OUI":"NON",LIFE?2:0);text(25,18,GOLD?"OUI":"NON",GOLD?2:0);}
static void blank(void){((void(*)(void))0x47fb4)();}
static u16 convert(u16 sms){const u16 levels[4]={0,3,5,7};return (levels[sms&3]<<1)|(levels[(sms>>2)&3]<<5)|(levels[(sms>>4)&3]<<9);}
static void display(u16 enabled){CTRL=0x8100|(B(0xff2b67)&~64)|(enabled?64:0);}
static void cheat_frame(void){u32 old=L(0xffe4bc);if(old)((void(*)(void))old)();if(LIFE && W(0xff28b8)){W(0xff2b16)=W(0xff28b8);W(0xff2b1a)=129;}if(GOLD)W(0xffda0e)=255;}
static void install(void){if(L(0xffcb6a)!=(u32)cheat_frame)L(0xffe4bc)=L(0xffcb6a);if(LIFE||GOLD)L(0xffcb6a)=(u32)cheat_frame;else L(0xffcb6a)=L(0xffe4bc);}
static void show(void){u16 x,y,k,previous=JOY,pressed,now;const u8*logo=(const u8*)0xffd400;OPEN=1;COUNT++;SELECT=0;display(0);CTRL=0x8f02;patterns();rect(0,0,0,64,32,0);rect(1,0,0,64,32,0x6000+1104);address((B(0xff2b6b)&0x7f)<<9);L(0xc00000)=0;L(0xc00000)=0;for(k=0;k<32;k++)color(k,convert(((const u8*)0xe5480)[k&15]));color(0,0);color(48,0);color(49,0xeee);color(50,0x6ae);color(51,0x200);color(52,0x4c4);color(53,0x422);for(y=0;y<8;y++)for(x=0;x<32;x++){u16 v=logo[(y*32+x)*2]|((u16)logo[(y*32+x)*2+1]<<8);tile(0,x,y+2,16+(v&511)|((v&0x800)?0x2000:0)|((v&0x200)?0x800:0)|((v&0x400)?0x1000:0));}text(6,0,"- OPTIONS SECRETES -",1);box();text(6,12,"CODE KONAMI ACTIVE",1);text(4,21,"OPTIONS POUR CETTE SESSION",0);text(5,25,"HAUT/BAS : CHOISIR",0);text(1,26,"A/C : CHANGER  START : VALIDER",1);choices();display(1);for(;;){blank();now=JOY;pressed=now&~previous;previous=now;if(pressed&START)break;if(pressed&(UP|DOWN)){SELECT^=1;choices();}else if(pressed&(LEFT|RIGHT|A|C)){if(SELECT)GOLD^=1;else LIFE^=1;choices();}}while(JOY)blank();display(0);rect(0,0,0,64,32,0);rect(1,0,0,64,32,0);rect(1,0,2,32,24,0xe001);for(y=0;y<24;y++){address(plane(0)+(y+2)*128);for(x=0;x<32;x++)DATA=((const u16*)0xff451a)[y*32+x];}for(k=0;k<32;k++)color(k,convert(((const u16*)0xff44c0)[k]));color(0,0);color(33,0x6a6);for(k=48;k<64;k++)color(k,0);display(1);install();OPEN=0;STEP=0;PREV=0;JOY=INPUT=0;REQUEST=1;}
void konami_poll(void){static const u16 code[11]={UP,UP,DOWN,DOWN,LEFT,RIGHT,LEFT,RIGHT,BB,A,START};u16 raw=JOY,edge=raw&~PREV;PREV=raw;if(!TITLE || W(0xffd310) || W(0xff0004)!=0x3900){STEP=0;return;}if(edge){if(edge==code[STEP]){STEP++;if(STEP==11){show();return;}}else STEP=edge==UP?1:0;}if(STEP>=9)JOY=raw&~(A|BB|START);}
