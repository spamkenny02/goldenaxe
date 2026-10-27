"""Bind missing source bridge script, native fix and current campaign evidence."""
import json
from run_core import ROOT
from rebase_natural_campaign import evidence
from archive_lossless_evidence import sha
from validate_playable_sprite_limit import symbols
from assisted_prefix import recording

def main():
 refs={}
 def read(n):raw=evidence(ROOT/n);refs[n]=sha(raw);return raw
 def load(n):return json.loads(read(n))
 rom=read('gaw-megadrive.bin');digest=sha(rom);assert digest==sha(read('versions/v0293-878a7f44/gaw-megadrive-v0293.bin'));sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
 policy=load('analysis/crystal_bridge_policy_v0293_report.json');assert policy['passed'] and policy['cases']==5120 and policy['source_sha256']==sha(read('input/original.sms')) and policy['native_c_sha256']==sha(read('megadrive/src/source_crystal_bridge.c'))
 game=load('analysis/crystal_bridge_game_v0293-current01_report.json');base=load('analysis/crystal_bridge_game_v0293-baseline01_report.json');pub=load('analysis/crystal_bridge_publication_v0293_report.json')
 assert game['passed'] and pub['passed'] and game['md_sha256']==pub['md_sha256']==digest and game['cases']==12 and all(r['fields_exact'] for r in game['results'])
 assert base['passed'] and base['baseline_missing'] and base['md_sha256']==sha(read('versions/v0292-6eeb5608/gaw-megadrive-v0292.bin')) and sum(r['missing_reproduced'] for r in base['results'])==4
 assert len(pub['cases'])==4 and sum(r['hardware_map_words'] for r in pub['cases'])==32
 stages=[]
 for family,name,kind in [('natural-dungeon-combat','md-auto-v0293-d5-rebase01','five_crystals_bridge'),('natural-dungeon-route','md-v0293-d6-route01','d6_entry')]:
  root='validation/'+family+'/'+name;c=load(root+'/capture.json');r=load(root+('/route_report.json' if kind=='d6_entry' else '/report.json'));p=load(root+f'-assisted-fixed-replay-{c["frames"]}/replay_report.json');a,w=recording(ROOT/root,c);read(root+'/assistance.json')
  assert c['rom_sha256']==p['rom_sha256']==digest and c['sram_input'] is None and p['passed'] and p['whole_ram_bytes']==65536 and p['final_png_exact'] and not p['feedback_reads'] and not p['boss_assistance']
  for n,h in p['evidence'].items():assert sha(read(root+'/'+n))==h
  assert not r['failure'] and not a['health_refills'] and not a['primary_state_imports'] and all(address==sy['hero_hurt'] for _,address,_ in w)
  raw=read(root+f'/ram_{c["frames"]:05d}.bin');read(root+f'/frame_{c["frames"]:05d}.png');data=lambda n,k:bytes(raw[(sy[n]+j)^1] for j in range(k));assert data('game_save_state',592)[0x1f:0x24]==bytes([128]*5) and data('hero_items',17)[12:15]==bytes([1]*3)
  if kind=='five_crystals_bridge':
   assert r['passed'] and r['full_dungeon_cleared'] and r['last_state']['health']==r['last_state']['max_health']==72 and r['last_state']['room']==0x49 and data('game_save_state',592)[0x99]&1
   cells=data('scratch',4096)[0x800:0x8a0];assert cells[0x4a]==0x0a and cells[0x5a]==0x6b
  else:assert r['reached_entrance'] and r['directional_probe_succeeded'] and r['last_state']['room']==0x187 and r['last_state']['health']==72 and a['boss_room']==0x196 and a['first_boss_entry'] is None
  stages.append(dict(trace=root,role=kind,frames=c['frames'],whole_ram_bytes=65536,final_png_exact=True,last_state=r['last_state']))
 d1root='validation/natural-dungeon-route/md-v0293-d1-exit01';d1=load(d1root+'/rebase_report.json');proof=load(d1root+'-fixed-replay/replay_report.json');c=load(d1root+'/capture.json');assert d1['passed'] and proof['passed'] and proof['rom_sha256']==digest and proof['whole_ram_bytes']==65536 and proof['final_png_exact'] and not c['test_ram_writes'] and not c['sram_input'];assert d1['states'][-1]['hero_health']==32 and d1['states'][-1]['first_crystal']==128
 stackroot='validation/stack-v0293-d5-bridge-all';s=load(stackroot+'/stack_report.json');assert s['md_sha256']==digest and s['all_instructions'] and s['frames']==117215 and not s['invalid_heap_examples'];low=min(x['sp'] for x in s['instruction_minima']);boundary=s['heap_changes'][-1]['end']+2;assert low>=boundary
 for stem,ext in [('ram','bin'),('frame','png')]:assert read(stackroot+f'/{stem}_117215.{ext}')==read('validation/natural-dungeon-combat/md-auto-v0293-d5-rebase01'+f'/{stem}_117215.{ext}')
 for n in ['megadrive/src/main.c','megadrive/src/source_crystal_bridge.h','tools/validate_crystal_bridge_policy.py','tools/validate_crystal_bridge_game.py','tools/validate_crystal_bridge_publication.py','tools/rebase_assisted_campaign.py','tools/replay_assisted_prefix.py','tools/natural_dungeon_route.py','tools/assisted_boss_route.py']:read(n)
 checksum=sum(int.from_bytes(rom[i:i+2],'big') for i in range(0x200,len(rom),2))&65535;assert checksum==int.from_bytes(rom[0x18e:0x190],'big')
 out=dict(passed=True,version=293,md_sha256=digest,bytes=len(rom),checksum=f'{checksum:04X}',original_script='AF4A door followed by698B..699B;193D flag-before-repeat;5E8B redraw/sound',policy_cases=5120,game_cases=12,baseline_missing_cases=4,published_bridge_map_words=32,natural_d1_unassisted=True,native_five_crystals_current_rom=True,dungeon6_entrance_reached=True,dungeon6_completed=False,stages=stages,stack=dict(frames=117215,all_instructions=True,minimum_sp=low,heap_boundary=boundary,observed_margin_bytes=low-boundary,heap_valid=True,final_whole_ram_png_exact=True),evidence=refs,full_game_validated=False,limits=['Policy intercepts only source redraw/sound sink; gameplay separately runs original and production loops with controlled starting state.','VDP comparison covers settled bridge words and referenced tile color indices. Physical redraw timing,all images,sprites and analogue audio are not proven.','Current native five-crystal campaign replays historical ordinary inputs with live approach guards and no boss assistance. The original SMS full campaign is not compared.','D1 is unassisted. D6 approach has logged hurt-counter help,no item/money/health fixture and stops before the sixth boss. D6-D10,ending and global fidelity remain unfinished.','Stack bound applies only to this cold five-crystal/bridge route,not all future paths.'])
 (ROOT/'analysis/crystal_bridge_v0293_report.json').write_text(json.dumps(out,indent=2)+'\n');print('v293 bridge restored;D1 and five crystals replayed;D6 entered;stack margin',low-boundary)

if __name__=='__main__':main()
