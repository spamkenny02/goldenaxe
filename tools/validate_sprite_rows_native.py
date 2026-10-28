"""Run the exact production assembly row helper on the emulated68000."""
import argparse
import contextlib
import io
import json
import sys
from run_core import ROOT,run
from archive_lossless_evidence import sha
from validate_playable_sprite_limit import symbols


def extract():
    text=(ROOT/'megadrive/src/main.c').read_text()
    begin=text.index('static inline __attribute__((always_inline)) u8 count_world_sprite_rows')
    start=text.index('{',begin);end=start+1;depth=1
    while depth:
        depth+=(text[end]=='{')-(text[end]=='}');end+=1
    return text[begin:end].encode()+b'\n\n'


def main():
    p=argparse.ArgumentParser();p.add_argument('--label',default='v0300');p.add_argument('--generate',action='store_true');a=p.parse_args()
    assert a.label and all(c.isalnum() or c=='-' for c in a.label)
    folder=ROOT/f'validation/sprite-rows-{a.label}';folder.mkdir(exist_ok=True)
    helper=extract()
    if a.generate:
        (folder/'helper.inc').write_bytes(helper);print('Exact production row helper extracted');return
    build=ROOT.parents[1]/'work/sprite-rows-harness'
    assert (build/'src/helper.inc').read_bytes()==helper
    sy=symbols(build/'out/release/symbol.txt');results=[]
    for region in ['auto','pal']:
        observed={}
        def observe(f,r):
            def value(n,size):return int.from_bytes(bytes(r[(sy[n]+i)^1] for i in range(size)),'big')
            observed.update(frame=f,done=value('harness_done',2),failed=value('harness_failed',2),cases=value('harness_cases',4))
        with contextlib.redirect_stdout(io.StringIO()):
            run(build/'out/release/rom.bin',3000,folder/region,set(),[],skip_intro=False,
                ram_observer=observe,stop_when=lambda:bool(observed.get('done')),
                core_options={'genesis_plus_gx_region_detect':region})
        assert observed['done'] and not observed['failed'] and observed['cases']==8192,observed
        results.append(dict(region=region,**observed));print(region,observed,flush=True)
    report=dict(passed=True,md_sha256=sha((ROOT/'gaw-megadrive.bin').read_bytes()),
                production_source_sha256=sha((ROOT/'megadrive/src/main.c').read_bytes()),
                helper_sha256=sha(helper),harness_sha256=sha((build/'out/release/rom.bin').read_bytes()),results=results,
                limits=['Exact production inline68000 ADD/ADDX helper,with reference mask and byte shifts computed separately in the harness. All256 availability patterns with eight legal unary phases,all256 byte values in each position,and two byte alignments. Guard bytes detect outside writes.',
                        'This isolates the row helper. Whole sprite masking,pixels and actual game cadence require separate tests.'])
    (ROOT/f'analysis/sprite_rows_native_{a.label}_report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
