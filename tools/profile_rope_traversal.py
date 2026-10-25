"""Observe acquired-rope traversal state; distinguish motion timing from row cadence."""
import contextlib,io,json
from run_core import ROOT,run
from rebase_natural_campaign import evidence
from assisted_prefix import prefix_writes
from validate_playable_sprite_limit import symbols
from archive_lossless_evidence import sha

def main():
 results=[]
 for tag,name in [('sms','sms-v0287-rope41-04'),('md','md-v0287-rope41-02')]:
  base=ROOT/'validation/natural-rope-route'/name;c=json.loads((base/'capture.json').read_bytes());controls=json.loads((base/'controls.json').read_bytes());r=json.loads((base/'report.json').read_bytes());writes=prefix_writes(base,c,True);end=c['frames'];presses=list(map(tuple,c['presses']));start=r['rope_activation_frame']
  for i,row in enumerate(controls):
   stop=controls[i+1]['frame']-1 if i+1<len(controls) else end;presses.extend((row['frame'],min(stop,end),b) for b in row['buttons'] if row['frame']<=end)
  rom=ROOT/('input/original.sms' if tag=='sms' else 'versions/v0287-58068350/gaw-megadrive-v0287.bin');assert sha(rom.read_bytes())==c['rom_sha256'];sy=None if tag=='sms' else symbols(ROOT/'validation/v0287-d3-build/symbol.txt');rows=[]
  def observe(f,b):
   if not start-2<=f<=start+28:return
   if tag=='sms':
    word=lambda a:int.from_bytes(b[a:a+2],'little');rows.append(dict(frame=f,relative=f-start,state=b[0x301],counter=b[0x304],flags=b[0x303],hurt=b[0x305],x=word(0x312),y=word(0x310),dx=word(0x316),dy=word(0x314),terrain=b[0x41],global_68_6b=b[0x68:0x6c].hex(),work=b[0x98:0x9c].hex()))
   else:
    data=lambda n,k:bytes(b[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big');rows.append(dict(frame=f,relative=f-start,state=word('hero_state'),counter=word('hero_counter'),flags=word('hero_flags'),hurt=word('hero_hurt'),x=word('hero_x'),y=word('hero_y'),dx=word('hero_dx'),dy=word('hero_dy'),terrain=word('hero_terrain_context'),work=data('magic_rope_work',4).hex()))
  out=ROOT/f'validation/rope-motion-v0287-corrected/{tag}';assert not out.exists()
  with contextlib.redirect_stdout(io.StringIO()):run(rom,end,out,{end},presses,ram_writes=writes,skip_intro=False,ram_observer=observe,core_options=c['core_options'])
  for stem,ext in [('ram','bin'),('frame','png')]:assert (out/f'{stem}_{end:05d}.{ext}').read_bytes()==evidence(base/f'{stem}_{end:05d}.{ext}')
  (out/'observations.json').write_text(json.dumps(rows,indent=2)+'\n');results.append(dict(tag=tag,rom_sha256=c['rom_sha256'],trace=name,rows=rows,final_ram_png_exact=True))
  print(tag,[(v['relative'],v['y']>>8,v['counter'],v['terrain'],v['state']) for v in rows],flush=True)
 (ROOT/'analysis/rope_motion_v0287_report.json').write_text(json.dumps(dict(results=results,read_only_observer=True,limits=['Distinct original/native campaign states and encounters; motion duration differences require a controlled common initial state before attributing a bug.']),indent=2)+'\n')
if __name__=='__main__':main()
