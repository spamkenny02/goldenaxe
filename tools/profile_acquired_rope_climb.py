"""Observe a real acquired-rope climb beyond the previously verified landing."""
import contextlib,io,json
from run_core import ROOT,run
from rebase_natural_campaign import evidence
from assisted_prefix import prefix_writes,recording
from archive_lossless_evidence import sha

def main():
 source=ROOT/'validation/natural-rope-route/sms-v0287-rope41-04';capture=json.loads((source/'capture.json').read_bytes());old=json.loads((source/'controls.json').read_bytes());writes=prefix_writes(source,capture,True);start=capture['frames'];end=start+500;rom=ROOT/'input/original.sms';assert capture['rom_sha256']==sha(rom.read_bytes());folder=ROOT/'validation/natural-rope-route/sms-v0291-climb41-diagnostic01';assert not folder.exists();presses=[tuple(row) for row in capture['presses']]
 for i,row in enumerate(old):
  stop=old[i+1]['frame']-1 if i+1<len(old) else start;presses.extend((row['frame'],min(stop,start),button) for button in row['buttons'] if row['frame']<=start)
 presses.append((start+1,end,4));rows=[];prior=None;captures={start,end}
 def observe(f,r):
  nonlocal prior
  if f<start:return
  if f==start:assert r==evidence(source/f'ram_{start:05d}.bin')
  state=dict(frame=f,room=int.from_bytes(r[0xb9:0xbb],'little'),game=r[0x1d],hero=r[0x301],counter=r[0x304],x=r[0x313],y=r[0x311],health=r[0x318],terrain=r[0x41],rope=list(r[0x98:0x9c]))
  if f%10==0 or state['room']!=prior:rows.append(state)
  if state['room']!=prior:captures.add(f+1);prior=state['room']
 with contextlib.redirect_stdout(io.StringIO()):run(rom,end,folder,captures,presses,skip_intro=False,ram_writes=writes,ram_observer=observe,core_options=capture['core_options'])
 (folder/'observations.json').write_bytes((json.dumps(rows,indent=2)+'\n').encode());(folder/'assistance.json').write_bytes((source/'assistance.json').read_bytes());controls=list(old)+[dict(frame=start+1,buttons=[4])];(folder/'controls.json').write_bytes((json.dumps(controls,indent=2)+'\n').encode());recording(folder,json.loads((folder/'capture.json').read_bytes()));print(rows[-10:])
if __name__=='__main__':main()
