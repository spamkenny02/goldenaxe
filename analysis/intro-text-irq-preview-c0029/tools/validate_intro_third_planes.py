"""Compare final source third-scene bitmap against native SMS-VRAM mirrors."""
import argparse
import contextlib
import io
import json
import re
from pathlib import Path
from run_core import ROOT,run
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence

def main():
    p=argparse.ArgumentParser();p.add_argument('--project',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);cases=[]
    systems=[('sms',ROOT/'input/original.sms',None),('before',ROOT/'validation/menu-raster-v0316/candidate22/out/release/rom.bin',ROOT/'validation/menu-raster-v0316/candidate22'),('after',a.project.resolve()/'out/release/rom.bin',a.project.resolve())]
    for region in ('ntsc','pal'):
        patterns={}
        for tag,rom,project in systems:
            if not rom.exists():
                staged=out/'before-candidate22.bin'
                if not staged.exists():staged.write_bytes(evidence(rom))
                assert sha(staged.read_bytes())==sha(evidence(rom));rom=staged
            folder=out/(region+'-'+tag)
            with contextlib.redirect_stdout(io.StringIO()):run(rom,4100,folder,{4100},[],skip_intro=False,core_options={'genesis_plus_gx_region_detect':'pal'if region=='pal'else'auto'})
            if project is None:patterns[tag]=(folder/'vram_04100.bin').read_bytes()[:0x2400]
            else:
                sy={m[2].split('.lto_priv.')[0]:int(m[1],16)&65535 for line in(project/'out/release/symbol.txt').read_text().splitlines()if(m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))}
                raw=(folder/'ram_04100.bin').read_bytes();patterns[tag]=bytes(raw[(sy['sms_vram']+i)^1]for i in range(0x2400))
        counts={tag:sum(x!=y for x,y in zip(patterns['sms'],patterns[tag]))for tag in ('before','after')}
        cases.append(dict(region=region,different_pattern_bytes=counts,pattern_sha256={k:sha(v)for k,v in patterns.items()}))
        print(region,'final third-scene pattern byte differences:',counts,flush=True)
    result=dict(passed=all(r['different_pattern_bytes']['before']>0 and r['different_pattern_bytes']['after']==0 for r in cases),cases=cases,
        md_sha256=sha((a.project/'out/release/rom.bin').read_bytes()),source_sha256=sha((ROOT/'input/original.sms').read_bytes()),driver_sha256=sha(Path(__file__).read_bytes()),ram_writes=0,sram_imports=0,
        scope='At frame4100 only: all9216 source picture-pattern bytes compared to native SMS mirror. Before is candidate22. Does not prove transient mask publication, SAT or MD conversion.')
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':main()
