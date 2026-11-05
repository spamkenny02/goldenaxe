"""Recover the eight-crystal campaign by normal Continue, free healing and a real gift."""
import json,shutil
import continue_d8_entry_v0314 as helper
from continue_d8_entry_v0314 import ROOT,ROUTE,SERVICE,COMBAT,load,budget,run,assert_canonical
from cold_replay_stream import ReplayStream
from archive_lossless_evidence import sha
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols
helper.EVIDENCE=ROOT/'validation/v0314-d9-recovery-sources'

def main():
 prior=json.loads((ROOT/'analysis/d8_campaign_v0314_report.json').read_bytes())
 digest=sha((ROOT/'gaw-megadrive.bin').read_bytes());assert prior['passed']and prior['md_sha256']==digest
 helper.EVIDENCE.mkdir(exist_ok=False);snapshot=helper.EVIDENCE/'sources';snapshot.mkdir()
 names=['continue_d9_recovery_v0314.py','natural_death_continue.py','natural_dungeon_route.py','natural_free_healer.py','natural_house_service.py','assisted_boss_route.py','assisted_prefix.py','cold_replay_stream.py','run_core.py']
 index={}
 for name in names:
  target=snapshot/name;shutil.copyfile(ROOT/'tools'/name,target);index[name]=sha(target.read_bytes())
 (snapshot/'source_index.json').write_text(json.dumps(index,indent=2)+'\n')
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');points=[];stream=ReplayStream(helper.EVIDENCE/'cold-stream')
 original=ROOT/prior['current_campaign_trace'];oc=json.loads((original/'capture.json').read_bytes());ow=recording(original,oc)[1]
 original_raw=(original/f'ram_{oc["frames"]:05d}.bin').read_bytes();base=lambda n,k:bytes(original_raw[(sy[n]+i)^1]for i in range(k))
 def canonical(family,name,gate,unchanged=False):
  root=ROOT/'validation'/family/name;c=load(family,name,'capture.json');r=load(family,name,'route_report.json'if family==ROUTE else'report.json');a,w=recording(root,c)
  assert r['failure']is None and gate(r),r
  assert c['rom_sha256']==digest and c['sram_input']is None and not a['primary_state_imports']and not a['health_refills']and not a['boss_assistance']
  if unchanged:assert w==ow
  assert w[:len(ow)]==ow and all(addr==sy['hero_hurt']and data in(b'\0\0',b'\0\x81')for _,addr,data in w)
  stream.prove(family+'/'+name);assert_canonical(family,name)
  raw=(root/f'ram_{c["frames"]:05d}.bin').read_bytes();data=lambda n,k:bytes(raw[(sy[n]+i)^1]for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
  assert data('hero_items',17)==base('hero_items',17) and data('game_save_state',592)[0x1f:0x28]==bytes([128]*8+[0])
  assert word('hero_max_health')==96 and word('hero_keys')==1 and word('hero_health')>0 and not word('sound_unhandled_command')
  point=dict(trace=root.relative_to(ROOT).as_posix(),frames=c['frames'],room=word('room_id'),health=word('hero_health'),max_health=word('hero_max_health'),magic=word('hero_magic'),gold=word('hero_gold'),keys=word('hero_keys'),whole_ram_png_exact=True)
  points.append(point);(helper.EVIDENCE/'verified_endpoints.json').write_text(json.dumps(points,indent=2)+'\n');return r,point
 try:
  death='md-v0314-d9-death-continue01'
  r,p=canonical(SERVICE,death,lambda r:r['passed']and r['normal_deaths']==r['normal_continues']==1,True)
  assert p['room']==0x95 and p['health']==p['magic']==24 and p['gold']==6
  assert r['death']['frame']<r['death_menu']['frame']<r['resumed']['frame']and r['resumed']['items']==r['first_state']['items']
  route='v0314-d9-healer94-route01'
  run('natural_dungeon_route.py',['--prefix-service',death,'--assisted-prefix','--house-outside','0x94','--house-target','0','--trial',route,'--frames',budget(SERVICE,death,6000),'--axe-terrain','--live-prefix-terrain','--live-room-replan'])
  canonical(ROUTE,'md-'+route,lambda r:r['reached_entrance']and r['directional_probe_succeeded'],True)
  heal='v0314-d9-healer94-service01'
  run('natural_free_healer.py',['--prefix','md-'+route,'--assisted-prefix','--trial',heal])
  r,p=canonical(SERVICE,'md-'+heal,lambda r:r['passed']and r['normal_health_refill'],True)
  assert p['health']==96 and p['gold']==6 and p['magic']==24
  gift_route='v0314-d9-gold-a6-route02'
  world=['--boss-room','0x1ac','--assisted-prefix','--world-route','--live-prefix-terrain','--live-room-replan','--axe-terrain','--rope-terrain','--preserve-floor-hurt']
  run('assisted_boss_route.py',[*world,'--new-assistance-episode','--completed-exit-proof',COMBAT+'/md-auto-v0314-d8-exit01','--prefix-service','md-'+heal,'--house-outside','0xa6','--house-target','0x3f','--frames',budget(SERVICE,'md-'+heal,16000),'--trial',gift_route])
  canonical(ROUTE,'md-'+gift_route,lambda r:r['reached_entrance']and r['directional_probe_succeeded'])
  gift='v0314-d9-gold-a6-service01'
  run('natural_house_service.py',['--assisted-prefix','--prefix','md-'+gift_route,'--outside','0xa6','--kind','gold','--gold-gain','10','--trial',gift])
  r,p=canonical(SERVICE,'md-'+gift,lambda r:r['passed']and not r['new_assistance_writes'])
  assert not r['first_state']['outside_flags']&2 and r['last_state']['gold']-r['first_state']['gold']==10 and p['gold']>=10
  result=dict(passed=True,version=314,md_sha256=digest,production_rom_unchanged=True,normal_death_continue=True,normal_free_healing=True,real_gold_gift=10,currency_or_inventory_fixtures=False,primary_state_imports=0,eight_crystals_preserved=True,stages=points,current_campaign_trace=points[-1]['trace'],campaign_frames=p['frames'],full_game_validated=False,source_index=index,scope='Current eight-crystal branch uses ordinary death/Continue, free healer and previously unclaimed A6 gift. No resources,actors,progression or SRAM imported. Approach protection resumes only after real recovery; all checkpoints cold-replayed in whole RAM and PNG.')
  (ROOT/'analysis/d9_recovery_v0314_report.json').write_text(json.dumps(result,indent=2)+'\n');print('D9 REAL RECOVERY AND FUNDS VERIFIED',flush=True)
 finally:stream.close()
if __name__=='__main__':main()
