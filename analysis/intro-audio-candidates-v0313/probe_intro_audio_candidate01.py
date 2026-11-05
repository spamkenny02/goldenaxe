"""Natural first-track observation; each case runs in its own core process."""
import argparse,contextlib,io,json,sys
sys.path.insert(0,'tools')
from run_core import ROOT,run
from archive_lossless_evidence import sha
from validate_playable_sprite_limit import symbols

p=argparse.ArgumentParser()
p.add_argument('case',choices=['sms','baseline','candidate'])
p.add_argument('--pal',action='store_true')
a=p.parse_args()
project=ROOT/'validation/intro-audio-v0313/candidate01'
base=project if a.case=='candidate' else ROOT
rom=ROOT/'input/original.sms' if a.case=='sms' else base/'gaw-megadrive.bin'
sy=None if a.case=='sms' else symbols(base/'megadrive/out/release/symbol.txt')
region='pal' if a.pal else 'ntsc'
out=project/'validation'/f'{a.case}-{region}'
assert not out.exists()
rows=[];psg={}
def observe(frame,raw):
    if sy is None:
        sound=raw[0x1e00:0x1f90];track=None
    else:
        sound=bytes(raw[(sy['sound_ram']+i)^1] for i in range(0x190))
        track=int.from_bytes(bytes(raw[(sy['sound_current_track']+i)^1] for i in range(2)),'big')
    rows.append(dict(frame=frame,sound_hex=sound.hex(),track=track))
with contextlib.redirect_stdout(io.StringIO()):
    run(rom,160,out,{22,35,80,160},[],skip_intro=False,
        core=ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_libretro.dll',
        core_options={'genesis_plus_gx_region_detect':'pal' if a.pal else 'auto'},
        ram_observer=observe,psg_observer=lambda f,r:psg.update({f:list(r)}))
for r in rows:r['psg']=psg[r['frame']]
first=next(r['frame'] for r in rows if bytes.fromhex(r['sound_hex'])[0x40]&0x80)
report=dict(case=a.case,region=region,rom_sha256=sha(rom.read_bytes()),
    first_channel_activity=first,no_buttons=True,no_ram_mutations=True,rows=rows)
(out/'observations.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(a.case,region,'first music channel activity',first)
