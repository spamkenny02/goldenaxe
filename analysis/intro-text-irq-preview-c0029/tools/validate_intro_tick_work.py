"""Validate semantic native intro callback work against source F32/F12 spans."""
import argparse
import contextlib
import io
import json
import re
from pathlib import Path
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from run_core import ROOT,run

def main():
    p=argparse.ArgumentParser();p.add_argument('--project',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();project=a.project.resolve();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
    sy={m[2].split('.lto_priv.')[0]:int(m[1],16)&65535 for line in(project/'out/release/symbol.txt').read_text().splitlines()if(m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))};cases=[]
    for region in ('ntsc','pal'):
        native=[]
        def observe(frame,raw):
            def word(name):return int.from_bytes(bytes(raw[(sy[name]+i)^1]for i in range(2)),'big')
            native.append(dict(frame=frame,clock=word('intro_logic_clock'),scene=word('intro_scene'),counter=word('intro_counter'),work=word('intro_tick_work')))
        with contextlib.redirect_stdout(io.StringIO()):run(project/'out/release/rom.bin',6500,out/region,set(),[],skip_intro=False,ram_observer=observe,core_options={'genesis_plus_gx_region_detect':'pal'if region=='pal'else'auto'})
        events=json.loads(evidence(ROOT/f'validation/menu-raster-v0316/irq-spans01/{region}/events.json'))
        source=json.loads(evidence(ROOT/f'validation/menu-raster-v0316/logical-clock26/{region}-sms/observations.json'));rows=[]
        for index,event in enumerate(events):
            if event['pc']!=0xf32 or event['frame']>len(source):continue
            end=next(e for e in events[index+1:]if e['pc']==0xf12);n=native[event['frame']-1];s=source[event['frame']-1];scene={0xf36:0,0xf37:1,0x1055:2,0x104a:3}.get(s['callback'])
            expected=((end['elapsed']-event['elapsed'])-(end['irq']-event['irq']))//15
            # A30T callback uniquely identifies F32->F36:RET, including a
            # frame whose ending DCEC has already switched to the next scene.
            if expected==30:scene=0
            if n['clock']!=event['clock']or n['counter']!=s['counter']or n['scene']!=scene:continue
            rows.append(dict(frame=event['frame'],scene=scene,source=expected,native=n['work']))
        different=[r for r in rows if r['source']!=r['native']]
        cases.append(dict(region=region,paired_calls=len(rows),mismatches=different,matched_by_scene={str(n):sum(r['scene']==n and r['source']==r['native']for r in rows)for n in range(4)}))
        (out/(region+'-native-work.json')).write_text(json.dumps(native,indent=2)+'\n')
        print(region,'paired callbacks',len(rows),'work mismatches',len(different),'examples',different[:6],flush=True)
    (out/'report.json').write_text(json.dumps(dict(passed=all(not r['mismatches']for r in cases),cases=cases,md_sha256=sha((project/'out/release/rom.bin').read_bytes()),source_sha256=sha((ROOT/'input/original.sms').read_bytes()),driver_sha256=sha(Path(__file__).read_bytes()),scope='Callback work at paired absolute-frame clock/counter/scene states. Does not certify unpaired states or IRQ loss scheduling.'),indent=2)+'\n')

if __name__=='__main__':main()
