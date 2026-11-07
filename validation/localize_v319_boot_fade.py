"""Localize known NTSC-only boot pixel differences on immutable V319 and SMS."""
import contextlib,io,json,sys
from pathlib import Path
sys.path.insert(0,'tools')
from run_core import ROOT,run
from archive_lossless_evidence import sha
from validate_playable_sprite_limit import symbols
work=ROOT/'validation/v319-boot-fade-localize01';assert not work.exists();work.mkdir()
sy=symbols(ROOT/'megadrive/out/release/symbol.txt');frames={65,66,67,68,69,70,3651,3652,3653,3670,3691,3692}
for region in ('ntsc','pal'):
 for tag,rom in [('md',ROOT/'gaw-megadrive.bin'),('sms',ROOT/'input/original.sms')]:
  folder=work/(region+'-'+tag)
  with contextlib.redirect_stdout(io.StringIO()):run(rom,3700,folder,frames,[],skip_intro=False,core_options={'genesis_plus_gx_region_detect':'pal' if region=='pal' else 'auto'})
  rows=[]
  for f in sorted(frames):
   raw=(folder/f'ram_{f:05d}.bin').read_bytes()
   if tag=='md':
    word=lambda n:int.from_bytes(bytes(raw[(sy[n]+i)^1] for i in range(2)),'big')
    rows.append(dict(frame=f,**{n:word(n) for n in ('intro_scene','intro_counter','intro_line','intro_logic_clock','intro_running','title_phase') if n in sy}))
   else:rows.append(dict(frame=f,game=raw[0x1d],clock=raw[0x2f],callback=int.from_bytes(raw[0x1cec:0x1cee],'little')))
  (folder/'phase.json').write_text(json.dumps(rows,indent=2)+'\n')
  print(region,tag,'localized',flush=True)
print('Known boot discrepancy captures complete; no cartridge changes',flush=True)
