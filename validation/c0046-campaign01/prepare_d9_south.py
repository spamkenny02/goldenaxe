"""Prepare an ordinary paid return south using the candidate's actual funds."""
from pathlib import Path
root=Path(__file__).resolve().parents[2]
project=root/'validation/c0046-campaign01/isolated/project'
text='''"""Pay the reverse1A passage after the actual eight-crystal exterior return."""
import json,shutil
import continue_d8_entry_c0046 as helper
from run_core import ROOT
from cold_replay_stream import ReplayStream
from archive_lossless_evidence import sha
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols

def main():
 prior=json.loads((ROOT/'analysis/d8_campaign_c0046_report.json').read_bytes())
 digest=sha((ROOT/'gaw-megadrive.bin').read_bytes())
 assert prior['passed'] and prior['eighth_crystal_and_exterior_return'] and prior['md_sha256']==digest
 source='md-auto-c0046-d8-exit01';helper.assert_canonical(helper.COMBAT,source)
 helper.EVIDENCE=ROOT/'validation/c0046-d9-south-sources';helper.EVIDENCE.mkdir(exist_ok=False)
 index={}
 for name in ['continue_d9_south_c0046.py','continue_d8_entry_c0046.py','assisted_boss_route.py','natural_dungeon_route.py','natural_paid_passage.py','assisted_prefix.py','cold_replay_stream.py','run_core.py']:
  p=helper.EVIDENCE/name;shutil.copyfile(ROOT/'tools'/name,p);index[name]=sha(p.read_bytes())
 (helper.EVIDENCE/'source_index.json').write_text(json.dumps(index,indent=2)+'\\n')
 helper.STREAM=ReplayStream(helper.EVIDENCE/'cold-stream');points=[]
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');refs={}
 def read(p):refs[p.relative_to(ROOT).as_posix()]=sha(p.read_bytes());return p.read_bytes()
 def verify(family,name,gate):
  helper.replay(family,name,gate)
  p=ROOT/'validation'/family/name;c=json.loads(read(p/'capture.json'));r=json.loads(read(p/('route_report.json' if family==helper.ROUTE else 'report.json')))
  a,w=recording(p,c);assert not a['primary_state_imports'] and not a['health_refills'] and not a['boss_assistance']
  assert all(addr==sy['hero_hurt'] for _,addr,_ in w)
  f=c['frames'];q=p.with_name(name+f'-assisted-fixed-replay-{f}');proof=json.loads(read(q/'replay_report.json'))
  assert proof['passed'] and proof['whole_ram_bytes']==65536 and proof['final_png_exact']
  for n,h in proof['evidence'].items():assert sha(read(p/n))==h
  for stem,ext in [('ram','bin'),('frame','png')]:assert read(p/f'{stem}_{f:05d}.{ext}')==read(q/f'{stem}_{f:05d}.{ext}')
  raw=read(p/f'ram_{f:05d}.bin');word=lambda n:int.from_bytes(bytes(raw[(sy[n]+j)^1] for j in range(2)),'big')
  save=bytes(raw[(sy['game_save_state']+j)^1] for j in range(592));assert save[0x1f:0x28]==bytes([128]*8+[0])
  assert word('hero_health')>0 and word('hero_max_health')==96 and not word('sound_unhandled_command')
  points.append(dict(trace=p.relative_to(ROOT).as_posix(),frames=f,room=word('room_id'),health=word('hero_health'),gold=word('hero_gold'),whole_ram_png_exact=True))
  return r
 try:
  trial='c0046-d9-south-route01'
  helper.run('assisted_boss_route.py',['--boss-room','0x1ac','--assisted-prefix','--world-route','--new-assistance-episode',
   '--prefix-combat',source,'--live-prefix-terrain','--live-room-replan','--axe-terrain','--rope-terrain','--preserve-floor-hurt',
   '--house-outside','0x1a','--house-target','0x9f','--frames',helper.budget(helper.COMBAT,source,12000),'--trial',trial])
  name='md-'+trial;r=verify(helper.ROUTE,name,lambda r:r['reached_entrance'] and r['directional_probe_succeeded'])
  assert r['last_state']['gold']>=10
  helper.run('natural_paid_passage.py',['--prefix',name,'--outside','0x1a','--assisted-prefix','--trial','c0046-d9-south-paid01'])
  name='md-c0046-d9-south-paid01';r=verify(helper.SERVICE,name,lambda r:r['passed'] and r['last_state']['room']==0x3c)
  assert r['price']==10 and r['first_state']['gold']-r['last_state']['gold']==10 and not r['currency_or_inventory_fixtures']
 finally:helper.STREAM.close()
 done=helper.EVIDENCE/'cold-stream/completed.json';d=json.loads(read(done));assert d['passed'] and len(d['checkpoints'])==2
 for p in helper.EVIDENCE.iterdir():
  if p.is_file():read(p)
 prefix=ROOT.relative_to(ROOT.parents[3]).as_posix()+'/'
 for p in points:p['trace']=prefix+p['trace']
 result=dict(passed=True,candidate='c0046',md_sha256=digest,stages=points,paid_south_return=True,real_price=10,
  current_campaign_trace=points[-1]['trace'],eight_crystals_preserved=True,full_game_validated=False,
  scope='Normal reverse passage1A to3C, paid with actual campaign gold. Approach hurt writes only, no death/Continue, resources, actors, progression or SRAM imports.',
  evidence={(k if k.startswith('analysis/') else prefix+k):v for k,v in refs.items()})
 (ROOT/'analysis/d9_south_c0046_report.json').write_text(json.dumps(result,indent=2)+'\\n')
 print('Eight-crystal paid return south verified',flush=True)
if __name__=='__main__':main()
'''
target=project/'tools/continue_d9_south_c0046.py';assert not target.exists();target.write_text(text)
print('D9 ordinary paid return prepared; no death or resources imported')
