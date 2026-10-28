"""Compile old/current production masking and compare final sprite pixels."""
import argparse
import ctypes as c
import json
import os
import subprocess
from run_core import ROOT
from archive_lossless_evidence import sha


def body(text, prefix):
    begin=text.index('static void mask_world_sms_sprite_rows(u16 count,u8 *used)')
    if 'static inline __attribute__((always_inline)) u8 count_world_sprite_rows' in text:
        begin=text.index('static inline __attribute__((always_inline)) u8 count_world_sprite_rows')
    end=text.index('\nstatic u16 dungeon_bitmap_pending;',begin)
    text=text[begin:end]
    for name in ['count_world_sprite_rows','mask_world_sms_sprite_rows','terminate_world_sprite_list','prepare_world_sms_sprite_overflow']:
        text=text.replace(name,prefix+name)
    return text


def main():
    p=argparse.ArgumentParser();p.add_argument('--label',default='v0296');p.add_argument('--unbuilt',action='store_true');a=p.parse_args()
    assert a.label and all(c.isalnum() or c=='-' for c in a.label)
    old=subprocess.check_output(['git','show','ff1d245:megadrive/src/main.c'],cwd=ROOT).decode().replace('\r\n','\n')
    new=(ROOT/'megadrive/src/main.c').read_text()
    folder=ROOT/f'validation/sprite-mask-cache-host-{a.label}';folder.mkdir(exist_ok=True)
    code=r'''
#include <stdint.h>
#include <string.h>
typedef uint8_t u8;typedef int8_t s8;typedef uint16_t u16;typedef int16_t s16;typedef uint32_t u32;typedef u8 bool;
#define TRUE 1
#define FALSE 0
typedef struct {u16 y,x,size_link,attribut;u8 link;} Sprite;
typedef struct {const u32 *source;u16 tile,count;} WorldTileJob;
static Sprite vdpSpriteCache[64];static WorldTileJob world_tile_jobs[68];
static u32 world_clone_tiles[65][8],patterns[512*8],vram[2048][8];
static u16 world_tile_job_count,world_video_next_overflow,world_sms_sprite_prepared_overflow,upload_count;
static u8 world_video_preparing;static volatile u32 control;static volatile u32 port_data=0xa55aa55a;
#define VDP_DATA_PORT (&port_data)
#define VDP_CTRL_PORT (&control)
#define VDP_READ_VRAM_ADDR(x) (x)
static void VDP_setAutoInc(u16 n) {(void)n;}
static void VDP_setSpriteTile(u16 n,u16 tile) {vdpSpriteCache[n].attribut=(vdpSpriteCache[n].attribut&0xf800)|tile;}
static void world_tile_upload(const u32 *source,u16 tile,u16 count) {
 WorldTileJob *j=world_tile_jobs+world_tile_job_count++;j->source=source;j->tile=tile;j->count=count;upload_count++;
 memcpy(vram[tile],source,count*32);
}
static void world_clone_upload(const u32 *source,u16 tile,u16 index) {
 upload_count++;memcpy(vram[tile],source,32);
 if(world_video_preparing) {WorldTileJob *j=world_tile_jobs+world_tile_job_count++;memcpy(world_clone_tiles[index],source,32);j->source=world_clone_tiles[index];j->tile=tile;j->count=1;}
}
'''+body(old,'old_')+body(new,'new_')+r'''
unsigned cases,failure,reused_cases,saved_uploads;
unsigned check(void) {
 Sprite initial[64],expected[64];u32 expected_rows[64][8];
 unsigned count,raw,layout,mode,i,j,k,old_count=0,of=0,prepared=0,base_jobs;
 for(i=0;i<512*8;i++)patterns[i]=0x12345678u^(i*0x10204081u);
 cases=failure=reused_cases=saved_uploads=0;
 for(count=0;count<=64;count++)for(raw=0;raw<256;raw++)for(layout=0;layout<4;layout++)for(mode=0;mode<2;mode++) {
  memset(initial,0,sizeof(initial));
  for(i=0;i<64;i++) {
   unsigned y=layout==0?raw:layout==1?(raw+i%5)&255:layout==2?(raw*31+i*13+(i*i)%29)&255:(i==count/2?208:raw);
   initial[i].y=145+y;initial[i].x=128+(i*17)%256;
   initial[i].attribut=0xa000|(16+(layout==0?i%2:layout==1?i%4:(i*13)%512));initial[i].link=i+1;
  }
  base_jobs=raw%5;
  for(k=0;k<2;k++) {
   memcpy(vdpSpriteCache,initial,sizeof(initial));memset(world_tile_jobs,0,sizeof(world_tile_jobs));world_video_preparing=mode;upload_count=0;
   for(i=0;i<2048;i++)for(j=0;j<8;j++)vram[i][j]=0xa55aa55a;
   world_tile_job_count=base_jobs;world_sms_sprite_prepared_overflow=0x33;
   for(i=0;i<base_jobs;i++){world_tile_jobs[i].source=patterns+i*16;world_tile_jobs[i].tile=16+i*13;world_tile_jobs[i].count=2;}
   if(!k)old_prepare_world_sms_sprite_overflow(count);else new_prepare_world_sms_sprite_overflow(count);
   if(mode)for(i=0;i<base_jobs;i++)memcpy(vram[world_tile_jobs[i].tile],world_tile_jobs[i].source,world_tile_jobs[i].count*32);
   if(!k) {
    memcpy(expected,vdpSpriteCache,sizeof(expected));old_count=upload_count;of=world_video_next_overflow;prepared=world_sms_sprite_prepared_overflow;
    for(i=0;i<64;i++)memcpy(expected_rows[i],vram[vdpSpriteCache[i].attribut&2047],32);
   } else {
    cases++;
    for(i=0;i<64;i++) {
     Sprite a=expected[i],b=vdpSpriteCache[i];a.attribut&=0xf800;b.attribut&=0xf800;
     if(a.y!=b.y || a.x!=b.x || a.size_link!=b.size_link || a.attribut!=b.attribut || a.link!=b.link || memcmp(expected_rows[i],vram[vdpSpriteCache[i].attribut&2047],32)){failure=cases;return 0;}
    }
    if(of!=world_video_next_overflow || prepared!=world_sms_sprite_prepared_overflow || upload_count>old_count){failure=cases;return 0;}
    if(upload_count<old_count){reused_cases++;saved_uploads+=old_count-upload_count;}
   }
  }
 }
 return cases;
}
'''
    source=folder/'mask.c';source.write_text(code)
    env=dict(os.environ);env['PATH']='C:/msys64/ucrt64/bin;'+env['PATH']
    result=subprocess.run(['C:/msys64/ucrt64/bin/gcc.exe','-std=c99','-O2','-Wall','-Wextra','-Werror','-shared',str(source),'-o',str(folder/'mask.dll')],env=env,capture_output=True,text=True)
    (folder/'compile.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
    dll=c.CDLL(str(folder/'mask.dll'));cases=dll.check();assert cases==65*256*4*2,c.c_uint.in_dll(dll,'failure').value
    report=dict(passed=True,md_sha256=None if a.unbuilt else sha((ROOT/'gaw-megadrive.bin').read_bytes()),compiled_c_cases=cases,reused_cases=c.c_uint.in_dll(dll,'reused_cases').value,
                saved_uploads=c.c_uint.in_dll(dll,'saved_uploads').value,reference_commit='ff1d245',
                production_source_sha256=sha((ROOT/'megadrive/src/main.c').read_bytes()),
                limits=['Actual production masking/overflow bodies compiled with SDK IO stubs. Final sprite metadata,all eight tile rows and overflow status match. SAT tile identities and DMA counts may differ because identical masked tiles are reused.',
                        'VRAM port reads return a constant word; queued source tiles vary by row. All0..64 counts,256 Y values,four layouts,two preparation modes and0..4 base jobs are checked. Native VDP integration and cadence require separate evidence.'])
    assert report['reused_cases']>0
    (ROOT/f'analysis/sprite_mask_cache_host_{a.label}_report.json').write_text(json.dumps(report,indent=2)+'\n');print(report)


if __name__=='__main__':main()
