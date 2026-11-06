"""Measure native stage entry/return PCs on the unchanged c0044 PAL trace."""
import contextlib
import ctypes as c
import io
import json
from pathlib import Path
import re
import subprocess
import sys
sys.path.insert(0,'tools')
from run_core import ROOT,FrameWrites,run
from assisted_prefix import recording
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from validate_playable_sprite_limit import symbols

control_mode='--control' in sys.argv
control_root=ROOT/'validation/c0044-burst-stages03-control'
work=control_root if control_mode else ROOT/'validation/c0044-burst-stages03-profile'
assert not work.exists()
work.mkdir(parents=True)
release=ROOT/'versions/candidates/c0044-cc4c9830'
rom=release/'gaw-megadrive-c0044.bin'
symbol_file=release/'symbol.txt'
elf=ROOT/'validation/v318-dungeon-pattern-ram01/out/release/rom.out'
sy=symbols(symbol_file)
native={m[2]:int(m[1],16) for line in symbol_file.read_text().splitlines()
        if (m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))}
wanted=['world_vint','tick_world_simulation','tick_world_actors',
        'prepare_hero_patterns','update_hero_sprites_for_frame',
        'add_world_sprite_scene','mask_world_sms_sprite_rows']
watched={}
for name in wanted:
    full=next(n for n in native if n.split('.')[0]==name)
    asm=subprocess.check_output([str(ROOT.parents[1]/'work/sgdk/bin/objdump.exe'),
        '-d','--disassemble='+full,str(elf)],text=True)
    (work/(name+'.asm')).write_text(asm)
    assert re.search(r'^'+format(native[full],'08x')+r' <',asm,re.M)
    watched[native[full]]=(name,'enter')
    exits=[int(m[1],16) for line in asm.splitlines()
           if (m:=re.match(r'\s*([0-9a-f]+):\s+.*\brts\b',line))]
    assert exits,(name,'no return PC')
    for pc in exits:watched[pc]=(name,'leave')
assert len(watched)<=32,len(watched)
trace=ROOT/'validation/natural-dungeon-combat/md-pal-pal318-d8-midboss01'
cap=json.loads(evidence(trace/'capture.json'))
aid,writes=recording(trace,cap)
assert cap['sram_input'] is None and not aid['primary_state_imports']
controls=json.loads(evidence(trace/'controls.json'))
presses=list(map(tuple,cap['presses']))
for i,row in enumerate(controls):
    stop=controls[i+1]['frame']-1 if i+1<len(controls) else 80012
    if row['frame']<=80012:
        presses += [(row['frame'],min(stop,80012),b) for b in row['buttons']]
core=ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_clock_libretro.dll'
dll=c.CDLL(str(core))
dll.gaw_md_config.argtypes=[c.c_uint,c.POINTER(c.c_uint)]
dll.gaw_md_event_count.restype=c.c_uint
dll.gaw_md_event_data.restype=c.POINTER(c.c_uint)
pcs=(c.c_uint*len(watched))(*watched)
events=[]
def observe(frame,raw):
    count=dll.gaw_md_event_count();assert count<8192
    p=dll.gaw_md_event_data()
    if frame>=79990:
        for i in range(count):
            pc,cycles,sp=[int(p[i*3+j]) for j in range(3)]
            name,kind=watched[pc]
            events.append(dict(frame=frame,master_cycles=cycles,sp=sp&65535,name=name,event=kind))
    dll.gaw_md_config(len(watched),pcs)
if control_mode:
    with contextlib.redirect_stdout(io.StringIO()):
        dll.gaw_md_config(0,pcs)
        run(rom,80012,work/'capture',{80012},presses,skip_intro=False,
            ram_writes=FrameWrites((f,sy['hero_hurt'],v) for f,_,v in writes),
            core_options=cap['core_options'],core=core)
    print('Fresh-process control captured',flush=True)
    sys.exit(0)
dll.gaw_md_config(len(watched),pcs)
with contextlib.redirect_stdout(io.StringIO()):
    run(rom,80012,work/'capture',{80012},presses,skip_intro=False,
        ram_writes=FrameWrites((f,sy['hero_hurt'],v) for f,_,v in writes),
        ram_observer=observe,core_options=cap['core_options'],core=core)
for stem,ext in [('ram','bin'),('frame','png')]:
    name=f'{stem}_80012.{ext}'
    assert (work/'capture'/name).read_bytes()==(control_root/'capture'/name).read_bytes()
assert (work/'capture/frame_80012.png').read_bytes()==evidence(ROOT/'validation/v318-dungeon-pattern-ram01/candidate/frame_80012.png')
period=3420*313
spans=[];open_calls={}
for e in events:
    key=(e['name'],e['sp'])
    t=e['frame']*period+e['master_cycles']
    if e['event']=='enter':open_calls[key]=(e,t)
    elif key in open_calls:
        start,begin=open_calls.pop(key)
        spans.append(dict(name=e['name'],begin_frame=start['frame'],begin_cycles=start['master_cycles'],
                          end_frame=e['frame'],end_cycles=e['master_cycles'],master_cycles=t-begin))
report=dict(rom_sha256=sha(rom.read_bytes()),core_sha256=sha(core.read_bytes()),
            elf_sha256=sha(elf.read_bytes()),symbols_sha256=sha(symbol_file.read_bytes()),
            driver_sha256=sha(Path(__file__).read_bytes()),observer_read_only=True,
            final_whole_ram_png_exact=True,control_is_independent_cold_boot_of_same_rom=True,
            events=events,spans=spans,
            limits=['Controlled observer on recorded native PAL input. Stage spans include interrupts. No SMS timing equivalence claim.'])
(work/'report.json').write_text(json.dumps(report,indent=2)+'\n')
for row in spans:
    if row['begin_frame'] in [80000,80001,80002] and row['name']!='world_vint':print(row,flush=True)
