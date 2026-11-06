import argparse,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,'tools')
from assisted_prefix import recording
from compare_fade_candidate_campaign import FIELDS
from run_core import ROOT,run,FrameWrites
from validate_playable_sprite_limit import symbols
from archive_lossless_evidence import sha
p=argparse.ArgumentParser()
p.add_argument('region',choices=['pal','ntsc'])
region=p.parse_args().region
V=ROOT/'validation'
preview=ROOT/'versions/candidates/c0039-aafa3255'
trial=V/'v318-d1-music-candidate02/out/release'
source=V/'natural-dungeon-combat/md-pal-pal318-d1-exit03' if region=='pal' else V/'c0039-ntsc-campaign-lab01/isolated/project/validation/natural-dungeon-combat/md-auto-c39-d1-exit01'
c=json.loads((source/'capture.json').read_bytes())
controls=json.loads((source/'controls.json').read_bytes())
a,writes=recording(source,c)
assert not a['boss_assistance'] and c['sram_input'] is None and not a['primary_state_imports']
presses=list(map(tuple,c['presses']))
end=c['frames']
for i,row in enumerate(controls):
 stop=min(end,controls[i+1]['frame']-1) if i+1<len(controls) else end
 presses.extend((row['frame'],stop,b) for b in row['buttons'] if row['frame']<=end)
pal=region=='pal'
base=(ROOT/'gaw-megadrive.bin',ROOT/'versions/v0318-b9e1f0a0/symbol.txt') if pal else (preview/'gaw-megadrive-c0039.bin',preview/'symbol.txt')
assert sha(base[0].read_bytes())==c['rom_sha256']
start_delay=4043 if pal else 1
first=4107 if pal else 4152
out=V/'v318-d1-music2-d1-replay01'/region
reference=[]
diff_count=0
first_diff=[]
runs=[]
for tag,rom,syfile,delay in [('baseline',*base,0),('trial',trial/'rom.bin',trial/'symbol.txt',3 if pal else 0)]:
 sy=symbols(syfile)
 inputs=[]
 for l,h,key in presses:
  if l<start_delay:inputs.append((l,min(h,start_delay-1),key))
  if h>=start_delay:inputs.append((max(l,start_delay)+delay,h+delay,key))
 mapped=FrameWrites((f+(delay if f>=start_delay else 0),sy['hero_hurt'],v) for f,_,v in writes)
 focus=[(k,sy[k],n) for k,n in FIELDS.items() if k not in ('sms_vram','sound_ram')]
 def values(raw):
  return tuple(raw[addr:addr+(n&~1)]+(bytes((raw[(addr+n-1)^1],)) if n&1 else b'') for _,addr,n in focus)
 def observe(f,raw):
  global diff_count
  if f-delay<first:return
  row=values(raw)
  if tag=='baseline':
   reference.append(row)
  else:
   old=reference[f-delay-first]
   if row!=old:
    diff_count+=1
    if len(first_diff)<12:first_diff.append(dict(frame=f-delay,fields=[field for (field,_,_),a,b in zip(focus,old,row) if a!=b]))
 folder=out/tag
 run(rom,end+delay,folder,{end+delay},inputs,skip_intro=False,ram_writes=mapped,ram_observer=observe,core_options=c['core_options'])
 image=(folder/f'frame_{end+delay:05d}.png').read_bytes()
 raw=(folder/f'ram_{end+delay:05d}.bin').read_bytes()
 word=lambda key:int.from_bytes(raw[sy[key]:sy[key]+2],'little')
 state=dict(room=word('room_id'),hero_health=word('hero_health'),hero_max_health=word('hero_max_health'),first_crystal=raw[(sy['game_save_state']+0x1f)^1],state=word('game_state'))
 if tag=='baseline':assert image==(source/f'frame_{end:05d}.png').read_bytes()
 runs.append(dict(rom_sha256=sha(rom.read_bytes()),delay=delay,frame=end+delay,image_sha256=sha(image),endpoint=state))
result=dict(region=region,first_compared_frame=first,last_compared_frame=end,compared_fields=[k for k,_,_ in focus],difference_frames=diff_count,
 first_differences=first_diff,final_image_exact=runs[0]['image_sha256']==runs[1]['image_sha256'],runs=runs)
(out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result),flush=True)
