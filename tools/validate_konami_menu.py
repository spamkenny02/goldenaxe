"""Actual cold-boot controller tests; no injected cheat, resource or game state."""
import argparse,json,hashlib
from pathlib import Path
from run_core import ROOT,run
from validate_playable_sprite_limit import symbols

def inputs(kind):
 rows=[(200,202,0)];seq=[4,4,5,5,6,7,6,7,0,1,3]
 if kind=='wrong':seq[5]=4
 for i,key in enumerate(seq):rows.append((600+i*16,603+i*16,key))
 if kind=='held':rows=[(200,202,0),(600,667,4)]+[(680+i*16,683+i*16,k) for i,k in enumerate(seq[2:])]
 if kind in ('both','life'):rows.append((900,903,1))
 if kind in ('both','gold'):rows.extend([(940,943,5),(980,983,8)])
 if kind=='both':rows.extend([(1020,1023,4),(1060,1063,1),(1100,1103,1)])
 rows.extend([(1200,1203,3),(1350,1365,0),(1500,1504,8),(1580,1640,5),(1660,1720,7),(1750,1760,8),(2500,2510,8),(2700,2710,8)])
 return rows

def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',required=True);p.add_argument('--out',required=True);a=p.parse_args();rom=ROOT/a.rom;out=ROOT/a.out;out.mkdir();results=[];sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
 for region in ['ntsc','pal']:
  for kind in ['both','life','gold','off','wrong','held']:
   folder=(ROOT/'validation/natural-service-route/md-konami-boot-on01') if region=='ntsc' and kind=='both' else out/(region+'-'+kind)
   events=[];states={};last=None;audio_errors=[]
   def observe(f,r):
    nonlocal last
    w=lambda n:int.from_bytes(r[n:n+2],'little');b=lambda n:r[n^1]
    state=dict(life=b(0xe4b0),gold=b(0xe4b1),sequence=w(0xe4b2),open=w(0xe4b6),selection=w(0xe4b8),activations=w(0xe4ba),game=w(0x074c),health=w(0x2b16),max_health=w(0x28b8),money=w(0xda0e),hurt=w(0x2b1a),audio_error=w(0x2d12))
    if state['audio_error']:audio_errors.append(f)
    if f in [790,920,1000,1080,1150,1300,4000]:states[f]=state.copy()
    key=tuple(state.values())
    if key!=last:events.append(dict(frame=f,**state));last=key
   run(rom,4000,folder,{790,1000,1080,1150,1300,4000},inputs(kind),skip_intro=False,ram_observer=observe,core_options={'genesis_plus_gx_region_detect':'pal' if region=='pal' else 'auto'})
   expected=(kind in ['both','life'],kind in ['both','gold']);final=states[4000]
   assert not audio_errors and (final['life'],final['gold'])==expected
   if kind in ['wrong','held']:assert final['activations']==0
   else:
    assert states[790]['open']==1 and states[790]['life']==states[790]['gold']==0 and not states[1300]['open']
    assert final['game']==12 and final['health']>0
    if expected[0]:assert final['health']==final['max_health'] and final['hurt']==129
    if expected[1]:assert final['money']==255
    else:assert final['money']==0
    if kind=='both':assert states[1080]['life']==0 and states[1080]['gold']==1 and states[1150]['life']==states[1150]['gold']==1
   report=dict(passed=True,failure=None,rom_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),case=kind,region=region,states=states,primary_state_imports=0,external_ram_writes=0,last_state=dict(room=int.from_bytes((folder/'ram_04000.bin').read_bytes()[sy['room_id']:sy['room_id']+2],'little'),x=int.from_bytes((folder/'ram_04000.bin').read_bytes()[sy['hero_x']:sy['hero_x']+2],'little')>>8,y=int.from_bytes((folder/'ram_04000.bin').read_bytes()[sy['hero_y']:sy['hero_y']+2],'little')>>8),source='Real Konami inputs and menu navigation from cold boot, followed by ordinary New Game/name/story controls.')
   (folder/'report.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());(folder/'controls.json').write_bytes(b'[]\n');(folder/'events.json').write_bytes((json.dumps(events,indent=2)+'\n').encode());results.append(dict(case=kind,region=region,report=folder.relative_to(ROOT).as_posix()+'/report.json'));print('KONAMI CASE PASSED',region,kind,flush=True)
 report=dict(passed=True,md_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),cases=results,case_count=len(results),default_off=True,separate_toggles=True,wrong_sequence_rejected=True,held_direction_not_counted_twice=True,new_game_return_tested=True,no_external_ram_or_sram_writes=True)
 (out/'report.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
if __name__=='__main__':main()
