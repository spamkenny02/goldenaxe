"""Read-only audio/IRQ phase observations across name, story and first room."""
import argparse
import contextlib
import io
import json
from pathlib import Path

from archive_lossless_evidence import sha
from run_core import ROOT, run
from validate_actor_tick import PRESSES
from validate_playable_sprite_limit import symbols


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--rom',type=Path,required=True)
    parser.add_argument('--symbols',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--pal',action='store_true')
    args=parser.parse_args()
    out=args.out.resolve();assert out.is_relative_to(ROOT/'validation')
    out.mkdir(exist_ok=False)
    sy=symbols(args.symbols); results={}
    for tag,rom in [('sms',ROOT/'input/original.sms'),('md',args.rom)]:
        rows=[]
        def observe(frame,raw):
            if frame<0:return
            if tag=='sms':
                audio=raw[0x1e00:0x1f00];clock=raw[0x2f]
            else:
                audio=bytes(raw[(sy['sound_ram']+i)^1]for i in range(256))
                def long(name):return int.from_bytes(bytes(raw[(sy[name]+i)^1]for i in range(4)),'big')
                clock=(long('vtimer')-long('world_clock_shift'))&255
            rows.append(dict(frame=frame,clock=clock,tempo=list(audio[1:5]),
                             fade=list(audio[11:14]),channels=audio[64:256].hex()))
        folder=out/tag
        with contextlib.redirect_stdout(io.StringIO()):
            run(rom,2520,folder,set(),[(200,220,0)]+PRESSES[:8],skip_intro=False,
                ram_observer=observe,core_options={'genesis_plus_gx_region_detect':'pal' if args.pal else 'auto'})
        (folder/'observations.json').write_text(json.dumps(rows,indent=2)+'\n')
        results[tag]=rows
    changes=[];previous=None
    for sms,md in zip(results['sms'],results['md']):
        phase=(md['tempo'][3]-sms['tempo'][3])%6
        if phase!=previous:
            changes.append(dict(frame=sms['frame'],mod6_difference=phase,
                                source_tempo=sms['tempo'],native_tempo=md['tempo'],
                                source_clock=sms['clock'],native_clock=md['clock']))
            previous=phase
    result=dict(rom_sha256=sha(args.rom.read_bytes()),region='pal' if args.pal else 'ntsc',
                phase_changes=changes,ram_writes=0,sram_imports=0,
                driver_sha256=sha(Path(__file__).read_bytes()),
                scope='Diagnostic observations; no assertion of complete audio equivalence.')
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
