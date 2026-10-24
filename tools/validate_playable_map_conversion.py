"""Read-only old/new playable map conversion and natural UI regression."""
import contextlib,ctypes as c,io,json,re,statistics,subprocess
from run_core import ROOT,run
from archive_lossless_evidence import sha
from validate_actor_tick import PRESSES

def symbols(path):
 return {m[2].split('.lto_priv.')[0]:int(m[1],16) for line in path.read_text().splitlines() if (m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))}

def main():
 root=ROOT/'validation/map-conversion-v0276';baseline=root/'baseline'
 old=baseline/'rom.bin';new=ROOT/'gaw-megadrive.bin'
 assert sha(old.read_bytes())=='02b597b346e3518670f93e1cfc5281a9db6a6cfbfbe2a70139ef18b11f05a5c5'
 core=ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_clock_libretro.dll';dll=c.CDLL(str(core))
 dll.gaw_md_config.argtypes=[c.c_uint,c.POINTER(c.c_uint)];dll.gaw_md_event_count.restype=c.c_uint;dll.gaw_md_event_data.restype=c.POINTER(c.c_uint)
 routes=[('exterior',PRESSES[:8]),('first_house',PRESSES[:11]+[(2950,2958,7),(3000,3020,4)]),('second_house',PRESSES[:11]+[(2950,2965,5),(3000,3023,6),(3050,3061,4),(3100,3110,4)]),('vertical_scroll',PRESSES)]
 scalar=['game_state','room_id','hero_x','hero_y','hero_health','hero_magic','hero_gold','inventory_slot','resume_phase','sound_current_track']
 arrays={'md_map':1536,'sms_vram':16384,'sound_ram':400,'world_actor_state':768,'game_save_state':592}
 records=[]
 version=next(e['version'] for e in json.loads((ROOT/'versions/index.json').read_bytes()) if e['sha256']==sha(new.read_bytes()))
 for region,lines in [('auto',262),('pal',313)]:
  for label,route in routes:
   results={}
   for tag,rom,folder in [('old',old,baseline),('new',new,ROOT/'megadrive/out/release')]:
    sy=symbols(folder/'symbol.txt');function=next(n for n in (folder/'symbol.txt').read_text().splitlines() if ' draw_map' in n).split()[2]
    assembly=subprocess.check_output([str(ROOT.parents[1]/'work/sgdk/bin/objdump.exe'),'-d','--disassemble='+function,str(folder/'rom.out')],text=True)
    stop=next(int(m[1],16) for line in assembly.splitlines() if 'map_queue' in line and (m:=re.match(r'\s*([0-9a-f]+):',line)))
    pcs=(c.c_uint*2)(sy['draw_map'],stop);dll.gaw_md_config(2,pcs);events=[];states=[];video=[]
    def observe(f,r):
     total=dll.gaw_md_event_count();assert total<8192;ptr=dll.gaw_md_event_data()
     events.extend([int(ptr[n*3]),(f-1)*lines*3420+int(ptr[n*3+1]),int(ptr[n*3+2])] for n in range(total));dll.gaw_md_config(2,pcs)
     if f<2900:return
     data=lambda n,size:bytes(r[((sy[n]&65535)+i)^1] for i in range(size))
     states.append(dict(frame=f,**{n:int.from_bytes(data(n,2),'big') for n in scalar},**{n:sha(data(n,size)) for n,size in arrays.items()}))
    def picture(f,v):
     if f>=2900:video.append(dict(frame=f,sha256=sha(v)))
    dest=root/(region+'-'+label+'-'+tag)
    captures={2900,3100,3300,3349,3353,3360,3370,3399,3403,3410,3420,3440,3470}
    with contextlib.redirect_stdout(io.StringIO()):run(rom,3470,dest,captures,route+[(3350,3355,0),(3400,3405,0)],core=core,ram_observer=observe,vram_observer=picture,core_options={'genesis_plus_gx_region_detect':region})
    spans=[];pending=None
    for pc,t,sp in events:
     if pc==sy['draw_map']:assert pending is None;pending=(t,sp)
     else:
      assert pending,(tag,hex(pc),sp)
      spans.append(t-pending[0]);pending=None
    assert spans and not pending
    result=dict(rom_sha256=sha(rom.read_bytes()),entry=sy['draw_map'],conversion_end=stop,conversion_master_cycles=spans,states=states,video=video)
    (dest/'observations.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());results[tag]=result
   state_differences=[dict(frame=a['frame'],fields=[k for k in a if a[k]!=b[k]]) for a,b in zip(results['old']['states'],results['new']['states']) if a!=b]
   video_differences=[a['frame'] for a,b in zip(results['old']['video'],results['new']['video']) if a!=b]
   image_differences=[f for f in sorted(captures) if (root/(region+'-'+label+'-old')/f'frame_{f:05d}.png').read_bytes()!=(root/(region+'-'+label+'-new')/f'frame_{f:05d}.png').read_bytes()]
   before=statistics.median(results['old']['conversion_master_cycles']);after=statistics.median(results['new']['conversion_master_cycles'])
   item=dict(region=region,route=label,previous_median_master_cycles=before,current_median_master_cycles=after,reduction_percent=round((before-after)*100/before,2),observed_frames=len(results['new']['states']),state_differences=state_differences,vram_difference_frames=video_differences,png_difference_frames=image_differences)
   required=set(scalar+list(arrays))-{'resume_phase','sound_current_track','md_map','sms_vram','sound_ram'}
   item['gameplay_difference_frames']=[v for v in state_differences if required.intersection(v['fields'])]
   def commands(rows):
    out=[]
    for row in rows:
     command=row['sound_current_track']
     if not out or out[-1]!=command:out.append(command)
    return out
   item['previous_music_commands']=commands(results['old']['states']);item['current_music_commands']=commands(results['new']['states'])
   item['observed_png_frames']=sorted(captures)
   records.append(item);print(region,label,'conversion reduction',item['reduction_percent'],'state/VRAM/PNG differences',len(state_differences),len(video_differences),len(image_differences),flush=True)
 report=dict(md_sha256=sha(new.read_bytes()),reference_sha256=sha(old.read_bytes()),passed=all(not r['gameplay_difference_frames'] and r['previous_music_commands']==r['current_music_commands'] and r['current_median_master_cycles']<r['previous_median_master_cycles'] for r in records),cases=records,limits=['Actual playable binaries, ordinary controller boot and route/menu controls; no RAM writes. All selected gameplay/progression fields match per frame and the music command order is retained. Complete VRAM and selected PNG differences are retained as diagnostics, not claimed equivalent: faster hidden loading changes some publication and animation/audio phases. Inventory black windows, resume and silence are separately compared directly with SMS by validate_menu_transitions. Timing isolates draw_map CPU preparation before transfer, including any IRQ overlap. It is not a whole-game speedup percentage, complete campaign or SMS raster/audio fidelity proof.'])
 (ROOT/f'analysis/playable_map_conversion_v{version:04d}_report.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
 assert report['passed'],[(v['region'],v['route'],v['gameplay_difference_frames'][:3]) for v in records]

if __name__=='__main__':main()
