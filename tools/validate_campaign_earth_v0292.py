"""Compare the real acquired-Earth D4 mutation, without importing game state."""
import json
from run_core import ROOT
from rebase_natural_campaign import evidence
from validate_playable_sprite_limit import symbols
from archive_lossless_evidence import sha
from audit_item_reward_visuals import sms_pixels,md_pixels

def main():
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');traces={};refs={}
 def read(path):raw=evidence(path);refs[path.relative_to(ROOT).as_posix()]=sha(raw);return raw
 for tag,name in [('sms','sms-auto-v0292-source-d4-earth06'),('md','md-auto-v0292-d4-earth01')]:
  folder=ROOT/'validation/natural-dungeon-combat'/name;r=json.loads(read(folder/'report.json'));c=json.loads(read(folder/'capture.json'));p=json.loads(read(folder.with_name(folder.name+f'-assisted-fixed-replay-{c["frames"]}')/'replay_report.json'))
  assert r['passed'] and r['earth_route_passed'] and r['earth_passage_opened'] and p['passed'] and p['final_png_exact'] and not p['boss_assistance']
  assert r['earth_opened']['magic']==r['earth_before']['magic']-8 and r['earth_opened']['cell']==0 and r['earth_opened']['flags']&4
  frame=r['earth_opened']['frame']+1;ram=read(folder/f'ram_{frame:05d}.bin');vram=read(folder/f'vram_{frame:05d}.bin')
  events=json.loads(read(folder/'earth_events.json'));precast=max(e['frame'] for e in events if e['frame']<r['earth_opened']['frame'] and e['magic']==r['earth_before']['magic'] and e['selected']==5 and not e['flags']&4)
  before_frame=precast+1;before=read(folder/f'ram_{before_frame:05d}.bin')
  if tag=='sms':cells=ram[0x1c00:0x1ca0];old=before[0x1c00:0x1ca0];m=ram[0x1600:0x1b00];items=ram[0xe0:0xf1];flag=ram[0x1e1]
  else:
   data=lambda raw,n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));cells=data(ram,'scratch',4096)[0x800:0x8a0];old=data(before,'scratch',4096)[0x800:0x8a0];m=data(ram,'sms_vram',16384)[0x3800:0x3d00];items=data(ram,'hero_items',17);flag=data(ram,'game_save_state',592)[0x131]
  traces[tag]=dict(cells=cells,old=old,map=m,items=items,flag=flag,vram=vram,rom=c['rom_sha256'])
 a,b=traces['sms'],traces['md']
 for field in ['cells','old','map','items','flag']:assert a[field]==b[field],field
 changed=[i for i,(x,y) in enumerate(zip(a['old'],a['cells'])) if x!=y];assert changed==[0x36,0x37,0x38,0x39,0x58]
 tiles=set();words=0
 for index in changed:
  for dy in range(2):
   for dx in range(2):
    y=(index>>4)*2+dy;x=(index&15)*2+dx;off=y*64+x*2;w=int.from_bytes(a['vram'][0x3800+off:0x3802+off],'little');assert a['vram'][0x3800+off:0x3802+off]==a['map'][off:off+2]
    translated=((w>>11)&1)<<13|((w>>12)&1)<<15|((w>>10)&1)<<12|((w>>9)&1)<<11|16+(w&511);p=0xe000+(y+2)*128+x*2;assert int.from_bytes(b['vram'][p:p+2],'little')==translated,(index,y,x);tiles.add(w&511);words+=1
 for tile in tiles:assert sms_pixels(a['vram'],tile)==md_pixels(b['vram'],tile+16),tile
 report=dict(passed=True,md_sha256=b['rom'],source_sha256=a['rom'],changed_cells=changed,software_cells_bytes=160,software_map_bytes=1280,inventory_bytes=17,persistent_flag=a['flag'],hardware_map_words=words,referenced_tiles=len(tiles),evidence=refs,scope='Separate cold campaigns with acquired rope/axe/Earth,real teacher payment and ordinary inventory/cast inputs. Identical D4-E1 mutation/map/inventory/flag and changed VDP cells/tiles. HP,currency,actors,global clock,full framebuffer and audio are not asserted equal. Approach assistance is explicit; destination D1 is entered,not cleared.')
 (ROOT/'analysis/campaign_earth_v0292_report.json').write_text(json.dumps(report,indent=2)+'\n');print('Acquired Earth D4 cells/map/inventory/VDP exact:',changed)
if __name__=='__main__':main()
