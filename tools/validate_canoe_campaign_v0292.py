"""Acquired canoe, shallow-water travel and Earth-revealed warp in both games."""
import json
from run_core import ROOT
from rebase_natural_campaign import evidence
from validate_playable_sprite_limit import symbols
from archive_lossless_evidence import sha
from audit_item_reward_visuals import sms_pixels,md_pixels
from assisted_prefix import recording

def main():
 refs={}
 def read(path):raw=evidence(path);refs[path.relative_to(ROOT).as_posix()]=sha(raw);return raw
 def load(path):return json.loads(read(path))
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');stages=[];chests={};warps={};water=[]
 for tag,key,canoe,warp in [('sms','sms-auto-v0292-source-d4-a1-key03','sms-auto-v0292-source-d4-canoe07','sms-auto-v0292-source-d4-warp02'),('md','md-auto-v0292-d4-a1-key03','md-auto-v0292-d4-canoe06','md-auto-v0292-d4-warp02')]:
  expected=sha(read(ROOT/('input/original.sms' if tag=='sms' else 'gaw-megadrive.bin')))
  def extract(raw):
   if tag=='sms':return dict(cells=raw[0x1c00:0x1ca0],map=raw[0x1600:0x1b00],items=raw[0xe0:0xf1],flags=raw[0x100:0x200])
   data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k))
   return dict(cells=data('scratch',4096)[0x800:0x8a0],map=data('sms_vram',16384)[0x3800:0x3d00],items=data('hero_items',17),flags=data('game_save_state',592)[0x50:0x150])
  for name,kind in [(key,'key'),(canoe,'canoe'),(warp,'warp')]:
   root=ROOT/'validation/natural-dungeon-combat'/name;r=load(root/'report.json');c=load(root/'capture.json');proof=load(root.with_name(root.name+f'-assisted-fixed-replay-{c["frames"]}')/'replay_report.json');assert c['rom_sha256']==proof['rom_sha256']==expected and proof['passed'] and proof['whole_ram_bytes']==(8192 if tag=='sms' else 65536) and proof['final_png_exact'] and not proof['boss_assistance']
   assert c['sram_input'] is None and not r['failure'] and not r['deaths'];read(root/'controls.json');read(root/'assistance.json')
   assist,writes=recording(root,c);assert all(address==(0x305 if tag=='sms' else sy['hero_hurt']) for _,address,_ in writes)
   assert all(proof['evidence'][name]==sha(read(root/name)) for name in ['capture.json','controls.json','assistance.json'])
   if kind=='key':assert r['room_cleared'] and r['new_key_verified'] and r['last_state']['keys']==2
   if kind=='canoe':
    assert r['room_cleared'] and r['collect_item_requested']==12 and r['last_state']['item_value']==1 and r['last_state']['room_flags']==20
    final=extract(read(root/f'ram_{c["frames"]:05d}.bin'));assert final['items'][12]==1 and final['cells'][0x24]==0x4c;final['vram']=read(root/f'vram_{c["frames"]:05d}.bin');chests[tag]=final
   if kind=='warp':
    assert r['passed'] and r['earth_route_passed'] and r['earth_cell']==0x5c and r['last_state']['room']==0x192 and r['last_state']['magic']==40
    frame=r['earth_opened']['frame']+1;final=extract(read(root/f'ram_{frame:05d}.bin'));assert final['cells'][0x5c]==12 and final['flags'][0xa3]==21;final['vram']=read(root/f'vram_{frame:05d}.bin');warps[tag]=final
    wp=root.with_name(root.name+f'-assisted-fixed-replay-{c["frames"]}-water02');w=load(wp/'replay_report.json');samples=load(wp/'water_samples.json');assert w['passed'] and w['final_png_exact'] and w['water_observer'] and w['shallow_water_flag']==32 and w['water_moving_frames']>0 and w['rom_sha256']==expected and all(s['owned'] and s['water_flag']==32 for s in samples)
    water.append(dict(system=tag,frames=w['water_frames'],moving_frames=w['water_moving_frames'],terrain_classes=w['water_terrain_classes'],rooms=w['water_rooms']))
   stages.append(dict(trace=root.relative_to(ROOT).as_posix(),kind=kind,frames=c['frames'],rom_sha256=expected,whole_ram_png_replay=True,assisted_history=True,last_state=r['last_state']))
 results=[]
 for label,pair,index in [('canoe_chest',chests,0x24),('earth_warp',warps,0x5c)]:
  a,b=pair['sms'],pair['md']
  for field in ['cells','map','items']:assert a[field]==b[field],(label,field)
  tiles=set()
  for dy in range(2):
   for dx in range(2):
    y=(index>>4)*2+dy;x=(index&15)*2+dx;off=y*64+x*2;w=int.from_bytes(a['vram'][0x3800+off:0x3802+off],'little');assert a['vram'][0x3800+off:0x3802+off]==a['map'][off:off+2]
    translated=((w>>11)&1)<<13|((w>>12)&1)<<15|((w>>10)&1)<<12|((w>>9)&1)<<11|16+(w&511);p=0xe000+(y+2)*128+x*2;assert int.from_bytes(b['vram'][p:p+2],'little')==translated,(label,y,x);tiles.add(w&511)
  if label=='canoe_chest':
   for tile in tiles:assert sms_pixels(a['vram'],tile)==md_pixels(b['vram'],tile+16),tile
  results.append(dict(kind=label,cells=160,map_bytes=1280,inventory_bytes=17,hardware_map_words=4,static_chest_tile_pixels_exact=label=='canoe_chest'))
 report=dict(passed=True,version=292,md_sha256=sha(read(ROOT/'gaw-megadrive.bin')),production_rom_unchanged=True,stages=stages,shallow_water=water,cross_source_native=results,evidence=refs,full_game_validated=False,limits=['Cold normal boots with ordinary buttons and logged approach-only hurt guards; no equipment,keys,currency,position or primary state imports.','Six stages have independent whole-RAM/PNG replays. The A1 detour clears thieves and bats and obtains the extra key; the canoe is obtained in A2 and its room cleared.','Water observers read ownership and actual shallow-water tile flag20 during fixed replays,with positive ordinary walking on both systems. Terrain classification is recorded,not assumed to be3 (ship context). Paths and timing are not asserted equal.','Chest and revealed warp software maps/cells/inventories and changed VDP map words match. Static chest tile color indices match; animated warp pixels,actors,HP,gold,full image,audio and global clock/RNG are not cross-system equivalence claims.','Warp arrival192 is verified but its room is not declared cleared by that route. Boss4,exit and subsequent campaign require separate evidence.'])
 (ROOT/'analysis/canoe_campaign_v0292_report.json').write_text(json.dumps(report,indent=2)+'\n');print('Canoe/warp verified:',len(stages),'stages;water moving frames',[w['moving_frames'] for w in water])
if __name__=='__main__':main()
