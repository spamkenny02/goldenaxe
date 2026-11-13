/* Flashkit-only investigation. Deliberate visible stops, not a release build. */
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned long u32;
#define W(a) (*(volatile u16*)(a))
#define L(a) (*(volatile u32*)(a))
extern const u32 presentation_diagnostic_font[];
static void reg(u16 n,u16 v){W(0xc00004)=0x8000|(n<<8)|v;}
static void address(u16 v){L(0xc00004)=0x40000000UL|((u32)(v&0x3fff)<<16)|(v>>14);}
static void text(u16 y,const char*s){address(0xe000+y*128+4);while(*s)W(0xc00000)=512+(u8)*s++-32;}
void presentation_diag(u16 stage){
 static const char*const names[]={"", "FADE FINISHED", "PLANES CLEARED", "FIFO DRAINED", "VDP RESTORED", "RETURNED TO MAIN", "AUDIO INIT OK", "VBLANK WAIT OK", "BEFORE SRAM READ", "SRAM READ OK"};
 u16 sr,i;
 __asm__ volatile("move.w %%sr,%0\n\tori.w #0x0700,%%sr":"=d"(sr)::"cc","memory");
 W(0xffe4c4)=stage;
 reg(1,0x34);reg(0,4);reg(2,0x38);reg(3,0x34);reg(4,6);
 reg(5,0x7a);reg(7,0);reg(11,0);reg(12,0);reg(13,0x3c);
 reg(15,2);reg(16,1);reg(17,0);reg(18,0);
 L(0xc00004)=0xc0000000UL;for(i=0;i<64;i++)W(0xc00000)=i==1?0xeee:0;
 address(512*32);for(i=0;i<96*8;i++)L(0xc00000)=presentation_diagnostic_font[i];
 address(0xe000);for(i=0;i<2048;i++)W(0xc00000)=512;
 address(0xc000);for(i=0;i<2048;i++)W(0xc00000)=512;
 address(0xf400);for(i=0;i<4;i++)W(0xc00000)=0;

 text(7,"GAW HARDWARE DIAGNOSTIC");text(10,"V326 - STAGE");address(0xe000+10*128+28);W(0xc00000)=512+16+stage;text(13,names[stage]);
 text(17,"REPORT THE LAST STAGE");text(20,"TEST ROM - NOT A RELEASE");
 reg(1,0x74);
 /* Poll the VDP, so even a broken CPU VInt cannot hide the last stage. */
 for(i=0;i<90;i++){while(W(0xc00004)&8);while(!(W(0xc00004)&8));}
 __asm__ volatile("move.w %0,%%sr"::"d"(sr):"cc","memory");
}
