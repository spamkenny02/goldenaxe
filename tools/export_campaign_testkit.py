"""Export exact recorded MD controls/approach writes without importing states."""
import hashlib,json,shutil
from pathlib import Path
from run_core import ROOT,compile_fixed_inputs
from assisted_prefix import recording

out=ROOT/'testkit';(out/'routes').mkdir(parents=True,exist_ok=True)
base=ROOT/'validation/c0046-campaign01/isolated/project/validation/natural-dungeon-combat'
manifest={'format':1,'routes':{},'roms':{}}
for version,relative in [(320,'versions/v0320-9e5b0abe/gaw-megadrive-v0320.bin'),(321,'versions/v0321-89c58333/gaw-megadrive-v0321.bin'),('sms','input/original.sms')]:
 raw=(ROOT/relative).read_bytes();manifest['roms'][str(version)]={'sha256':hashlib.sha256(raw).hexdigest(),'sha1':hashlib.sha1(raw).hexdigest()}
for region,name in [('ntsc','md-auto-c0046-cold-palace-ending01'),('pal','md-auto-palc0046-palace-ending01')]:
 folder=base/name;cap=json.loads((folder/'capture.json').read_bytes());assist,writes=recording(folder,cap);controls=json.loads((folder/'controls.json').read_bytes());end=cap['frames'];presses=list(map(tuple,cap['presses']))
 for i,row in enumerate(controls):
  stop=controls[i+1]['frame']-1 if i+1<len(controls) else end
  presses.extend((row['frame'],min(stop,end),key) for key in row['buttons'] if row['frame']<=end)
 masks=compile_fixed_inputs(presses,end);guards={f:int.from_bytes(data,'big') for f,address,data in writes}
 assert all(address==0x2b1a for _,address,_ in writes)
 rows=[];start=1;old=(masks[1],guards.get(1,-1))
 for frame in range(2,end+2):
  current=(masks[frame],guards.get(frame,-1)) if frame<=end else None
  if current!=old:rows.append((start,frame-1,*old));start=frame;old=current
 path=out/'routes'/('md_'+region+'.csv');path.write_bytes(('start,end,mask,guard\n'+''.join(','.join(map(str,r))+'\n' for r in rows)).encode())
 # Independent expansion checks every recorded frame and every write.
 recovered=[0]*(end+1);recovered_writes=[]
 for first,last,mask,guard in rows:
  recovered[first:last+1]=[mask]*(last-first+1)
  if guard!=-1:recovered_writes.extend((f,guard) for f in range(first,last+1))
 assert recovered[1:]==masks[1:] and recovered_writes==[(f,int.from_bytes(data,'big')) for f,_,data in writes]
 manifest['routes']['md_'+region]={'system':'md','region':region,'frames':end,'csv':path.name,'csv_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'rows':len(rows),'approach_writes':len(writes),'boss_assistance':False,'save_imports':0,'historical_recording_rom_sha256':cap['rom_sha256'],'source_files':{n:hashlib.sha256((folder/n).read_bytes()).hexdigest() for n in ['capture.json','controls.json','assistance.json']},'expected_final':{'game':0,'room':332,'crystals':9},'libretro_validated_rom_versions':[320],'bizhawk_runtime_validated':False}
for region in ['ntsc','pal']:
 path=out/'routes'/('sms_intro_'+region+'.csv');path.write_bytes(b'start,end,mask,guard\n1,7600,0,-1\n');manifest['routes']['sms_intro_'+region]={'system':'sms','region':region,'frames':7600,'csv':path.name,'csv_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'rows':1,'approach_writes':0,'full_campaign':False,'scope':'Cold boot intro/title only; not an SMS A-to-Z route.','bizhawk_runtime_validated':False}
(out/'manifest.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode())
print('Exported two complete MD routes and two SMS intro routes; every MD input/write verified.')
