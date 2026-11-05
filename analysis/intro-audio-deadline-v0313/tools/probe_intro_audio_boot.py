"""Observe natural intro maps and PSG in one fresh process per system/region."""
import argparse,contextlib,io,json,struct
from pathlib import Path
from run_core import ROOT,run
from archive_lossless_evidence import sha
from validate_playable_sprite_limit import symbols


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project',type=Path,required=True)
    p.add_argument('--system',choices=['sms','md'],required=True)
    p.add_argument('--pal',action='store_true')
    a=p.parse_args()
    project=a.project.resolve()
    assert project.is_relative_to(ROOT/'validation')
    sms=a.system=='sms';region='pal' if a.pal else 'ntsc'
    rom=ROOT/'input/original.sms' if sms else project/'gaw-megadrive.bin'
    sy=None if sms else symbols(project/'megadrive/out/release/symbol.txt')
    out=project/'validation'/f'boot-{a.system}-{region}'
    assert not out.exists()
    channels=bytearray();tempo=bytearray();psg=bytearray()
    maps={};first_active=None;completion=None;closed=False;previous_line=0
    frames=6500;errors=set()
    def observe(frame,raw):
        nonlocal first_active,completion,closed,previous_line
        if sms:
            sound=raw[0x1e00:0x1f90];line=raw[0x1ce0]
            if line<previous_line:closed=True
            if line==65 and raw[0x1ce1] and completion is None:completion=frame
            ready=not raw[0x1ce1] and not closed
            tilemap=raw[0x1600:0x1c00]
        else:
            def data(n,k):return bytes(raw[(sy[n]+i)^1] for i in range(k))
            def word(n):return int.from_bytes(data(n,2),'big')
            sound=data('sound_ram',0x190);line=word('intro_line')
            running=word('intro_running')
            if not running and line>0:
                closed=True
                if completion is None:completion=frame
            ready=bool(running) and not closed
            tilemap=bytes(raw[(sy['sms_vram']+0x3800+i)^1] for i in range(0x600))
            errors.add(word('sound_unhandled_command'))
        previous_line=line
        channels.extend(sound[0x40:0x100]);tempo.extend(sound[1:5])
        if sound[0x40]&0x80 and first_active is None:first_active=frame
        if 1<=line<=65 and ready:
            entry=maps.setdefault(line,dict(first_frame=frame,last_frame=frame,sha256=set()))
            entry['last_frame']=frame;entry['sha256'].add(sha(tilemap))
    core=ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_libretro.dll'
    captures={20 if a.pal else 23,62 if a.pal else 69,5952 if a.pal else 5959,6031 if a.pal else 6045}
    with contextlib.redirect_stdout(io.StringIO()):
        run(rom,frames,out,captures,[],skip_intro=False,core=core,
            core_options={'genesis_plus_gx_region_detect':'pal' if a.pal else 'auto'},
            ram_observer=observe,
            psg_observer=lambda f,r:psg.extend(struct.pack('<8H',*r)))
    assert len(channels)==frames*192 and len(tempo)==frames*4 and len(psg)==frames*16
    assert not any(errors)
    for entry in maps.values():entry['sha256']=sorted(entry['sha256'])
    for name,raw in [('audio_channels.bin',channels),('audio_tempo.bin',tempo),('audio_psg.bin',psg)]:
        (out/name).write_bytes(raw)
    result=dict(system=a.system,region=region,frames=frames,rom_sha256=sha(rom.read_bytes()),
        core_sha256=sha(core.read_bytes()),first_active_channel_frame=first_active,
        story_completion_frame=completion,maps=maps,no_buttons=True,no_ram_mutations=True,
        unsupported_audio_commands=0,probe_sha256=sha(Path(__file__).read_bytes()))
    (out/'observations.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(a.system,region,'first music',first_active,'story completion',completion,'lines',len(maps),flush=True)


if __name__=='__main__':main()
