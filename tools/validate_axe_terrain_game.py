"""Original/native axe phase7 cutting: cells, paired cells, metadata and map."""
import argparse,contextlib,ctypes as c,io,json
from run_core import ROOT,run
from rebase_natural_campaign import evidence
from validate_playable_sprite_limit import symbols
from validate_actor_tick import PRESSES
from validate_key_door_gameplay import maps
from archive_lossless_evidence import sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--trial',required=True);p.add_argument('--rom');p.add_argument('--symbols');p.add_argument('--expect-missing',action='store_true');a=p.parse_args();rom=ROOT/a.rom if a.rom else ROOT/'gaw-megadrive.bin';sy=symbols(ROOT/a.symbols if a.symbols else ROOT/'megadrive/out/release/symbol.txt');original=(ROOT/'input/original.sms').read_bytes();dll_path=ROOT/'validation/axe-terrain-probes-v0291-02/probes.dll'
 if not dll_path.exists():dll_path.write_bytes(evidence(dll_path))
 library=c.CDLL(str(dll_path));fn=library.source_axe_terrain_probes;fn.argtypes=[c.c_ubyte]*5+[c.POINTER(c.c_ubyte)];fn.restype=c.c_ubyte
 cases=[]
 for direction in range(4):
  for alignment in range(4):
   x=128+(8 if alignment&1 else 0);y=96+(8 if alignment&2 else 0);indices=(c.c_ubyte*2)();count=fn(0,7,direction,x,y,indices)
   if not count:continue
   for n in range(5):
    record=list(original[0x3620+n*4:0x3624+n*4]);cases.append(dict(direction=direction,x=x,y=y,kind=0,record=record,indices=list(indices[:count]),metadata=False,prior=0,room=0x95))
 for prior in [0,1]:cases.append(dict(direction=0,x=72,y=88,kind=0,record=[0x84,0x32,0x29,0],indices=[0x44],metadata=True,prior=prior,room=0x13))
 for kind in [1,2]:cases.append(dict(direction=0,x=136,y=104,kind=kind,record=[0x82,0x32,0,0],indices=[0x58],metadata=False,prior=0,room=0x95))
 results=[];span=40;end=3100+len(cases)*span
 for region in ['auto','pal']:
  traces={};visible={}
  for tag in ['sms','md']:
   folder=ROOT/f'validation/axe-terrain-game-{a.trial}/{region}-{tag}';assert not folder.exists();pending=[];rows=[];case_cells={};case_maps={};first_changes={};no_changes=[]
   def prepare(i,f,r):
    case=cases[i];cells=bytearray(160)
    for index in case['indices']:
     cells[index]=case['record'][0]
     if index+16<160:cells[index+16]=case['record'][2]
    if case['metadata'] and case['prior']:cells[0x44]=4
    if tag=='sms':meta=r[0x900:0x1100]
    else:meta=bytes(r[(sy['scratch']+n)^1] for n in range(2048))
    tilemap=maps(cells,meta)[0]+bytes(256);items=bytes([1,1]+[0]*15);metadata=bytes([0x44,0x44,4]) if case['metadata'] else bytes([255,255,0]);flag=case['prior'];case_cells[i]=bytes(cells)
    if tag=='sms':
     pending[:]=[(f,0xb9,case['room'].to_bytes(2,'little')),(f,0x100+case['room'],bytes([flag])),(f,0x40,bytes([case['kind']])),(f,0x6e,metadata),(f,0x1600,tilemap),(f,0x1c00,bytes(cells)),(f,0x600,bytes(768)),(f,0xe0,items),(f,0xdf,b'\1'),(f,0xee,b'\0'),(f,0x301,b'\1'),(f,0x303,bytes([3,0,129])),(f,0x30a,bytes([case['direction'],0])),(f,0x30e,b'\0'),(f,0x310,bytes([0,case['y'],0,case['x']])+bytes(4)),(f,0x318,b'\x18')]
    else:
     values=dict(room_id=case['room'],world_graphics_class=case['kind'],hero_selected_item=1,hero_weapon_level=1,hero_basic_level=1,hero_attack_speed=0,hero_attack_phase=0,hero_state=1,hero_flags=3,hero_counter=0,hero_hurt=129,hero_direction=case['direction'],hero_animation=0,hero_pending=0,hero_health=24,hero_x=case['x']<<8,hero_y=case['y']<<8,hero_dx=0,hero_dy=0)
     pending[:]=[(f,sy[k],v.to_bytes(2,'big')) for k,v in values.items()]+[(f,sy['game_save_state']+0x50+case['room'],bytes([flag])),(f,sy['room_metadata'],metadata),(f,sy['sms_vram']+0x3800,tilemap),(f,sy['scratch']+0x800,bytes(cells)),(f,sy['world_actor_state'],bytes(768)),(f,sy['hero_items'],items)]
   def observe(f,r):
    if f==3100:prepare(0,3101,r)
    if f<3101:return
    i=(f-3101)//span;offset=(f-3101)%span;case=cases[i]
    if tag=='sms':cells=bytes(r[0x1c00:0x1ca0]);m=bytes(r[0x1600:0x1b00]);flag=r[0x100+case['room']];state=[r[n] for n in [0x301,0x30a,0x30b,0x30e]]
    else:
     data=lambda n,k:bytes(r[(sy[n]+j)^1] for j in range(k));word=lambda n:int.from_bytes(data(n,2),'big');cells=data('scratch',4096)[0x800:0x8a0];m=data('sms_vram',16384)[0x3800:0x3d00];flag=data('game_save_state',592)[0x50+case['room']];state=[word(n) for n in ['hero_state','hero_direction','hero_animation','hero_attack_phase']]
    rows.append(dict(case=i,offset=offset,cells=cells.hex(),map=m.hex(),flag=flag,state=state))
    if cells!=case_cells[i] and i not in first_changes:first_changes[i]=offset
    if offset==span-1:
     changed=cells!=case_cells[i];expected=case['kind']==0 and not case['prior'];assert changed==(False if a.expect_missing and tag=='md' else expected),(tag,region,i,case,'actual cut required',changed)
     if case['metadata']:assert flag==1 if not a.expect_missing or tag=='sms' else flag==case['prior']
     if i+1<len(cases):prepare(i+1,f+1,r)
   presses=([(200,220,0)] if tag=='sms' else [])+PRESSES[:8]+[(3101+i*span,3102+i*span,8) for i in range(len(cases))]+[(3101+i*span,3102+i*span,4+case['direction']) for i,case in enumerate(cases)]
   captures={3101+i*span+span-1 for i in range(len(cases))}
   with contextlib.redirect_stdout(io.StringIO()):run(ROOT/'input/original.sms' if tag=='sms' else rom,end,folder,captures,presses,ram_writes=pending,ram_observer=observe,core_options={'genesis_plus_gx_region_detect':region})
   (folder/'observations.json').write_bytes((json.dumps(rows,indent=2)+'\n').encode());traces[tag]=rows
  if not a.expect_missing:assert traces['sms']==traces['md'],(region,next((a,b) for a,b in zip(traces['sms'],traces['md']) if a!=b))
  results.append(dict(region=region,cases=len(cases),frames=len(traces['sms']),software_fields_exact=not a.expect_missing));print(region,'completed',len(cases),flush=True)
 report=dict(passed=True,md_sha256=sha(rom.read_bytes()),source_sha256=sha(original),cases=cases,results=results,missing_cut_reproduced=a.expect_missing,controlled_fixture=True,limits=['Original/native loops receive explicit room, cells, equipment, protection and initial hero fixtures. Actual axe input, animation phase, mutations, paired cells and metadata flag execute.','Full campaign, natural chopping, intermediate hardware transfer phase, sprite pixels and audio waveforms require separate proof.'])
 (ROOT/f'analysis/axe_terrain_game_{a.trial}_report.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print('passed',sum(r['cases'] for r in results))
if __name__=='__main__':main()
