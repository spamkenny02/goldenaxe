"""Floor4 damage through real game loops: timing, armor, protection and body contact."""
import argparse,contextlib,io,json
from shield_reference import hero_collision
from run_core import ROOT,run
from validate_actor_tick import PRESSES
from validate_playable_sprite_limit import symbols
from archive_lossless_evidence import sha

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--trial',default='02');args=parser.parse_args()
 template=(ROOT/'validation/sms-shield-detail/ram_03740.bin').read_bytes()[0x780:0x7b0];assert len(template)==48 and template[0]>=0x10
 original=(ROOT/'input/original.sms').read_bytes()
 cases=[dict(hp=hp,hurt=hurt,armor=armor,terrain=4,contact=False) for hp in [1,4,5,24,96] for hurt in [0,1,47,48,128,129] for armor in [1,5]]
 cases += [dict(hp=24,hurt=hurt,armor=armor,terrain=terrain,contact=True) for terrain in [0,4] for armor in [1,5] for hurt in [0,1]]
 cases += [dict(hp=24,hurt=0,armor=1,terrain=t,contact=True,reflect=True,shield=3) for t in [0,4]]
 for row in cases:row['span']=65 if row['hp']<=5 or row['contact'] else 144
 schedule=[];start=3101
 for i,row in enumerate(cases):schedule.append((start,start+row['span']-1,i));start+=row['span']
 end=start-1;sy=symbols(ROOT/'megadrive/out/release/symbol.txt');results=[]
 fields=['hero_health','hero_hurt','hero_state','hero_flags','hero_counter','hero_animation','hero_x','hero_y','hero_dx','hero_dy','hero_defense','hero_terrain_context']
 offsets=[(0x318,1),(0x305,1),(0x301,1),(0x303,1),(0x304,1),(0x30b,1),(0x312,2),(0x310,2),(0x316,2),(0x314,2),(0x31a,1),(0x41,1)]
 for region in ['auto','pal']:
  traces={};baseline=template
  for tag in ['sms','md']:
   writes=[];samples={};reflections=[];active=0;native_clock=0;folder=ROOT/f'validation/floor-damage-v0289-{args.trial}/{region}-{tag}';assert not folder.exists()
   def prepare(i,f):
    row=cases[i];m=bytes([127 if row['terrain']==4 else 0,0])*768;records=bytearray(768)
    if row['contact']:
     e=bytearray(baseline);e[3]=3;e[4]=96;e[5]=0;e[6]=0;e[0x10:0x18]=bytes([0,88,0,128,0,0,0,0]);e[10]=0;e[0x18]=24;e[0x19]=9
     if row.get('reflect'):e[3]=0x13;e[0x19]=3;e[0x14:0x16]=(384).to_bytes(2,'little')
     records[:48]=e
    if tag=='sms':
     writes[:]=[(f,0x2f,b'\xff'),(f,0x1600,m),(f,0x600,bytes(records)),(f,0x310,bytes([0,96,0,128,0,0,0,0])),(f,0x301,b'\1'),(f,0x303,b'\3'),(f,0x304,bytes([0,row['hurt']])),(f,0x30a,bytes(2)),(f,0x318,bytes([row['hp']])),(f,0xda,bytes([max(24,row['hp'])])),(f,0x31a,bytes([(row['armor']-1)*4+(row.get('shield',1)-1)*2])),(f,0x31b,bytes([hero_collision(original,0)])),(f,0x31d,b'\0'),(f,0x68,b'\0'),(f,0xee,b'\0'),(f,0xf1,bytes([row['armor']])),(f,0xf2,bytes([row.get('shield',1)])),(f,0xdf,b'\0')]
    else:
     values=dict(hero_x=0x8000,hero_y=0x6000,hero_dx=0,hero_dy=0,hero_counter=0,hero_hurt=row['hurt'],hero_state=1,hero_flags=3,hero_health=row['hp'],hero_max_health=max(24,row['hp']),hero_direction=0,hero_animation=0,hero_pending=0,hero_attack_speed=0,hero_armor_level=row['armor'],hero_shield_level=row.get('shield',1),hero_selected_item=0,hero_defense=(row['armor']-1)*4+(row.get('shield',1)-1)*2)
     writes[:]=[(f,sy[k],v.to_bytes(2,'big')) for k,v in values.items()]+[(f,sy['world_clock_shift'],((native_clock+1)&0xffffffff).to_bytes(4,'big')),(f,sy['sms_vram']+0x3800,m),(f,sy['world_actor_state'],bytes(records))]
   def observe(f,b):
    nonlocal active,baseline,native_clock
    if tag=='md':native_clock=int.from_bytes(bytes(b[(sy['vtimer']+i)^1] for i in range(4)),'big')
    if f==3100:
      prepare(0,3101)
    if f<3101:return
    first,last,i=schedule[active];assert first<=f<=last
    if tag=='sms':row=[int.from_bytes(b[a:a+n],'little') for a,n in offsets]
    else:row=[int.from_bytes(bytes(b[(sy[name]+n)^1] for n in range(2)),'big') for name in fields]
    if cases[i]['contact'] and not cases[i].get('reflect') and not cases[i]['hurt'] and f==first:
     expected=24-max(2,9-(cases[i]['armor']-1)*4)-(4 if cases[i]['terrain']==4 else 0)
     assert row[0]==expected,(tag,region,'actual body contact required',i,row[0],expected)
    if cases[i].get('reflect') and f==first:
     if tag=='sms':flags=b[0x603];velocity=int.from_bytes(b[0x614:0x616],'little')
     else:flags=b[(sy['world_actor_state']+3)^1];velocity=int.from_bytes(bytes(b[(sy['world_actor_state']+0x14+n)^1] for n in range(2)),'little')
     assert not flags&2 and velocity==(-384&65535),(tag,region,'reflection',flags,velocity)
     assert row[0]==(20 if cases[i]['terrain']==4 else 24),(tag,region,'reflected floor HP',row)
     reflections.append(dict(case=i,flags=flags,velocity=velocity,hero_health=row[0]))
    samples[i,f-first]=row
    if f==last and active+1<len(schedule):active+=1;prepare(active,f+1)
   with contextlib.redirect_stdout(io.StringIO()):run(ROOT/('input/original.sms' if tag=='sms' else 'gaw-megadrive.bin'),end,folder,{3101,end},([(200,220,0)] if tag=='sms' else [])+PRESSES[:8],ram_writes=writes,ram_observer=observe,core_options={'genesis_plus_gx_region_detect':region})
   assert len(samples)==end-3100
   (folder/'observations.json').write_text(json.dumps([dict(case=i,offset=f,values=v) for (i,f),v in samples.items()],indent=2)+'\n');traces[tag]=samples
   (folder/'reflections.json').write_text(json.dumps(reflections,indent=2)+'\n')
  diffs=[dict(case=i,setup=cases[i],offset=f,sms=traces['sms'][i,f],md=traces['md'][i,f]) for i,f in traces['sms'] if traces['sms'][i,f]!=traces['md'][i,f]]
  results.append(dict(region=region,cases=len(cases),frames=end-3100,differences=diffs));print(region,len(diffs),'differences',diffs[:3],flush=True)
 report=dict(passed=all(not r['differences'] for r in results),md_sha256=sha((ROOT/'gaw-megadrive.bin').read_bytes()),source_sha256=sha((ROOT/'input/original.sms').read_bytes()),fields=fields,cases=cases,results=results,controlled_ram_fixtures=True,limits=['Software terrain, initial hero/equipment and optional body-contact/reflection actor fixtures with aligned collision-clock parity. Real game loop classifies terrain, handles contact, protection, movement and HP loss.','No natural terrain acquisition/travel, full graphics/waveform or hardware timing claim.'])
 (ROOT/'analysis/floor_damage_v0289_game_report.json').write_text(json.dumps(report,indent=2)+'\n');assert report['passed']
if __name__=='__main__':main()
