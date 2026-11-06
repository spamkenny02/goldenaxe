"""Bind the native source-work text IRQ forecast to the original cold boot."""
import argparse
import contextlib
import io
import json
import re
from pathlib import Path
from archive_lossless_evidence import sha
from run_core import ROOT,run

def main():
    p=argparse.ArgumentParser();p.add_argument('--project',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();project=a.project.resolve();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
    sy={m[2].split('.lto_priv.')[0]:int(m[1],16)&65535 for line in(project/'out/release/symbol.txt').read_text().splitlines()if(m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))}
    measured=json.loads((ROOT/'validation/menu-raster-v0316/text-irq-model01/report.json').read_bytes());cases=[]
    for region in ('ntsc','pal'):
        rows=[];previous=0;skips=0
        def observe(frame,raw):
            nonlocal previous,skips
            def word(name,size=2):return int.from_bytes(bytes(raw[(sy[name]+i)^1]for i in range(size)),'big')
            count=word('intro_text_predictions');current=word('intro_text_irq_skips');assert not word('sound_unhandled_command')
            if count!=previous:
                assert count==previous+1
                rows.append(dict(line=count,frame=frame,predicted_miss=current>skips,total_lower_bound=word('intro_text_prediction_total',4)));previous=count;skips=current
        with contextlib.redirect_stdout(io.StringIO()):run(project/'out/release/rom.bin',6500,out/region,set(),[],skip_intro=False,ram_observer=observe,core_options={'genesis_plus_gx_region_detect':'pal'if region=='pal'else'auto'})
        expected=[r for r in measured['cases']if r['region']==region];assert len(rows)==len(expected)==65
        mismatches=[dict(source=s,native=n)for s,n in zip(expected,rows)if (s['line'],s['frame'],s['actual_loss'])!=(n['line'],n['frame'],n['predicted_miss'])]
        cases.append(dict(region=region,lines=65,predicted_skip_frames=[r['frame']+1 for r in rows if r['predicted_miss']],mismatches=mismatches,rows=rows))
        print(region,'text predictions65; inserted audio-only slots',cases[-1]['predicted_skip_frames'],'mismatches',len(mismatches),flush=True)
    (out/'report.json').write_text(json.dumps(dict(passed=all(not r['mismatches']for r in cases),cases=cases,md_sha256=sha((project/'out/release/rom.bin').read_bytes()),source_measurements_sha256=sha((ROOT/'validation/menu-raster-v0316/text-irq-model01/report.json').read_bytes()),driver_sha256=sha(Path(__file__).read_bytes()),ram_writes=0,sram_imports=0,scope='65 first text-map forecasts per region, cold no-input boot. All-phase lower bound handles certain misses; ambiguous phases and attract-loop reentry remain unproven.'),indent=2)+'\n')

if __name__=='__main__':main()
