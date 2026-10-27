"""Current native D6 approach, Ice Bell and unopened-boss checkpoint."""
import json
from run_core import ROOT
from rebase_natural_campaign import evidence
from archive_lossless_evidence import sha
from validate_playable_sprite_limit import symbols
from assisted_prefix import recording

STAGES=[('east02','clear'),('key02','key'),('warp01','earth'),('key03','key'),('contact02','contact'),('key04','key'),('torch117-03','contact'),('outer01','clear'),('earth126-01','earth'),('middle135-01','cell'),('left135-01','earth'),('earth134-01','earth'),('key06','key'),('bell03','item'),('gate125-01','cell')]

def main():
 refs={}
 def read(n):raw=evidence(ROOT/n);refs[n]=sha(raw);return raw
 def load(n):return json.loads(read(n))
 digest=sha(read('gaw-megadrive.bin'));assert digest==sha(read('versions/v0293-878a7f44/gaw-megadrive-v0293.bin'));source=read('input/original.sms');assert source[0x3234e+0x115*8]==0x64;sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
 prior='validation/natural-dungeon-route/md-v0293-d6-route01';pc=load(prior+'/capture.json');raw=read(prior+f'/ram_{pc["frames"]:05d}.bin');data=lambda r,n,k:bytes(r[(sy[n]+j)^1] for j in range(k));word=lambda r,n:int.from_bytes(data(r,n,2),'big')
 keys=word(raw,'hero_keys');magic=word(raw,'hero_magic');assert keys==1 and magic==48;gained=spent=mana_gained=mana_spent=0;stages=[];reports={};states={};gate_assist=None
 for suffix,kind in STAGES:
  root='validation/natural-dungeon-combat/md-auto-v0293-d6-'+suffix;c=load(root+'/capture.json');r=load(root+'/report.json');p=load(root+f'-assisted-fixed-replay-{c["frames"]}/replay_report.json');a,w=recording(ROOT/root,c);read(root+'/assistance.json')
  assert c['rom_sha256']==p['rom_sha256']==digest and c['sram_input'] is None and p['passed'] and p['whole_ram_bytes']==65536 and p['final_png_exact'] and not p['feedback_reads'] and not p['boss_assistance']
  for n,h in p['evidence'].items():assert sha(read(root+'/'+n))==h
  assert r['failure'] is None and not r['deaths'] and r['last_state']['health']==r['last_state']['max_health']==72 and not r['last_state']['audio_error'] and r['last_state']['dungeon']==6 and r['last_state']['progress']==0
  assert a['first_boss_entry'] is None and a['first_boss_combat'] is None and a['release_write_frame'] is None and not a['primary_state_imports'] and not a['health_refills'] and all(address==sy['hero_hurt'] for _,address,_ in w)
  assert a['boss_room']==(0x115 if suffix=='gate125-01' else 0x196)
  if kind in ['clear','key','item']:assert r['room_cleared']
  if kind=='key':assert r['new_key_verified'] and r['last_state']['keys']==r['target_entry_keys']+1
  if kind in ['earth','cell']:assert r['passed'] and r['earth_route_passed'] and not r['earth_state_writes'] and r['earth_opened']['cell']==0
  if kind=='cell':assert r['earth_action_only_requested'] and r['earth_cell_cleared'] and not r['earth_passage_traversed']
  if kind=='contact':assert r['passed'] and r['contact_route_passed'] and not r['contact_state_writes'] and r['contact_opened']['flags']&4
  if kind=='item':assert r['collect_item_requested']==10 and r['last_state']['item_value']==1 and not r['last_state']['reward_active'] and not r['last_actors']
  events=load(root+'/events.json')
  for e in [*events,r['last_state']]:
   if 'room' in e:assert e['room'] not in [0x115,0x196]
   if 'keys' in e:delta=e['keys']-keys;gained+=max(0,delta);spent+=max(0,-delta);keys=e['keys']
   if 'magic' in e:delta=e['magic']-magic;mana_gained+=max(0,delta);mana_spent+=max(0,-delta);magic=e['magic']
  raw=read(root+f'/ram_{c["frames"]:05d}.bin');read(root+f'/frame_{c["frames"]:05d}.png');save=data(raw,'game_save_state',592);items=data(raw,'hero_items',17);assert save[0x1f:0x24]==bytes([128]*5) and save[0x24]==0 and items[12:15]==bytes([1]*3)
  if suffix=='middle135-01':assert not r['earth_passage_opened'] and data(raw,'scratch',4096)[0x857:0x859]==b'\0\0'
  if suffix=='left135-01':assert r['earth_cast_direction']==2 and r['earth_cast_position']==[96,80] and r['earth_before']['magic']==24 and r['earth_opened']['magic']==8 and r['last_state']['magic']==16
  if suffix=='torch117-03':assert r['mechanism_during_combat_requested'] and r['contact_opened']['active_enemies'] and r['contact_room']==0x117 and r['last_state']['room']==0x138
  if suffix=='gate125-01':
   gate_assist=a;assert r['last_state']['room']==0x125 and r['earth_cast_direction']==1 and not r['last_actors'] and items[10]==1
   cells=data(raw,'scratch',4096)[0x800:0x8a0];assert cells[0x7b]==cells[0x17]==cells[0x18]==0
   audit=a['retarget_audit'];assert audit==dict(from_room=0x196,to_room=0x115,checked_prefix_frame=142999,source_boss_kinds=[0x64],prefix_verified=True,no_prior_entry=True)
  stages.append(dict(trace=root,role=kind,frames=c['frames'],whole_ram_bytes=65536,final_png_exact=True,last_state=r['last_state']));reports[suffix]=r;states[suffix]=raw
 assert gained==spent==5 and keys==1 and mana_gained==32 and mana_spent==56 and magic==24
 opt=load('analysis/d6_prefix_optimization_v0293_report.json');assert opt['passed'] and opt['md_sha256']==digest and opt['whole_ram_bytes']==65536 and opt['controls_exact'] and opt['assistance_writes_exact'] and opt['final_png_exact']
 for n in ['natural_dungeon_combat.py','natural_contact_passage.py','natural_earth_passage.py','assisted_boss_route.py','replay_assisted_prefix.py','run_core.py','summarize_d6_prefix_optimization_v0293.py']:read('tools/'+n)
 for p in (ROOT/'validation/v0293-d6-drivers').glob('*.py'):
  raw=read(p.relative_to(ROOT).as_posix());assert sha(raw)==p.stem.rsplit('-',1)[1]
 out=dict(passed=True,version=293,md_sha256=digest,production_rom_unchanged=True,stages=stages,official_cold_replays=15,ice_bell_acquired=True,keys_gained=5,keys_spent=5,keys_remaining=keys,magic_recovered_by_ordinary_loot=mana_gained,magic_spent=mana_spent,magic_remaining=magic,health=72,max_health=72,planned_boss_room=0x115,boss_kind=0x64,retarget_audit=gate_assist['retarget_audit'],boss_entered=False,dungeon6_completed=False,full_game_validated=False,source_campaign_compared=False,evidence=refs,limits=['NTSC auto-region native progression with logged approach hurt-counter writes only. All items,keys,mana and doors are obtained by ordinary controls. No primary state imports or health/equipment/currency fixture.','Fifteen cold fixed replays compare entire65536 RAM bytes and final PNG,not every framebuffer or the original SMS full campaign.','The old pending approach target196 was not reached. The corrected target115 is verified against source boss64; its retarget audit replays every prior D6 prefix frame and forbids entry into either room. No boss has been entered at this checkpoint.','The preparatory Earth action in135 clears57/58 without claiming the left passage. Later left-facing casts clear44/43,then normal movement traverses to134. The last downward cast opens125 north before entering115.','The Ice Bell room includes actual proximity activation and defeat of mimic46; dormant mimic recognition,UP mechanism waits and mana-loot priorities change controller tools only.','Controller prefix optimization has separately identical controls,writes,full final RAM and PNG for its before/after route. No source SMS optimization or global timing claim.','Sixth boss/crystal/exit,remaining dungeons,ending,whole-game audio/visual/hardware timing and full fidelity remain unproven.'])
 (ROOT/'analysis/d6_progress_v0293_report.json').write_text(json.dumps(out,indent=2)+'\n');print('Native D6:15 replayed stages;Ice Bell;boss gate open at72/72HP,1key,24magic;no boss entered')

if __name__=='__main__':main()
