"""Observe two attract loops and original/native intro state without writes."""
import argparse
import contextlib
import io
import json
import re
import shutil
from pathlib import Path
from archive_lossless_evidence import sha
from run_core import ROOT,run

def main():
    p=argparse.ArgumentParser();p.add_argument('--project',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--frames',type=int,default=14000);a=p.parse_args();project=a.project.resolve();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);shutil.copyfile(Path(__file__),out/'driver.py')
    sy={m[2].split('.lto_priv.')[0]:int(m[1],16)&65535 for line in(project/'out/release/symbol.txt').read_text().splitlines()if(m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))};cases=[]
    for region in('ntsc','pal'):
        systems={}
        for tag,rom in [('sms',ROOT/'input/original.sms'),('md',project/'out/release/rom.bin')]:
            rows=[];audio=bytearray();palette=bytearray();video_flags=bytearray();errors=set()
            def observe(frame,raw):
                if tag=='sms':
                    row=dict(frame=frame,clock=raw[0x2f],counter=raw[0x1ce2],line=raw[0x1ce0],callback=int.from_bytes(raw[0x1cec:0x1cee],'little'),timer=raw[0x30]);sound=raw[0x1e00:0x1f90];colors=raw[0x1ca0:0x1cc0];video_flags.extend([raw[0x10],raw[0x1a]])
                else:
                    def data(name,size):return bytes(raw[(sy[name]+i)^1]for i in range(size))
                    def word(name):return int.from_bytes(data(name,2),'big')
                    row=dict(frame=frame,clock=word('intro_logic_clock'),counter=word('intro_counter'),line=word('intro_line'),scene=word('intro_scene'),running=word('intro_running'),timer=word('intro_timer'),track=word('sound_current_track'),track_started=word('sound_track_started_frame'),palette_pending=word('intro_palette_pending'),sprite_pending=word('intro_sprite_pending'),pending_track=word('sound_request'),pending_delay=word('sound_request_delay'),pending_effect=word('sound_effect_request'));sound=data('sound_ram',400);errors.add(word('sound_unhandled_command'))
                    colors=bytes(int.from_bytes(data('sms_palette',64)[n:n+2],'big')for n in range(0,64,2))
                rows.append(row);audio.extend(sound);palette.extend(colors)
            folder=out/(region+'-'+tag)
            with contextlib.redirect_stdout(io.StringIO()):run(rom,a.frames,folder,set(),[],skip_intro=False,ram_observer=observe,core_options={'genesis_plus_gx_region_detect':'pal'if region=='pal'else'auto'})
            assert not any(errors),(region,tag,errors)
            if video_flags:(folder/'source-video-flags.bin').write_bytes(video_flags)
            (folder/'observations.json').write_text(json.dumps(rows,indent=2)+'\n');(folder/'audio.bin').write_bytes(audio);(folder/'palette.bin').write_bytes(palette)
            starts=[r for old,r in zip(rows,rows[1:])if old['line']>0 and r['line']==0];systems[tag]=dict(reentry_line_resets=starts,rows=rows)
        first_scene_starts=[r for old,r in zip(systems['sms']['rows'],systems['sms']['rows'][1:])if r['callback']==0xf37 and old['callback']!=0xf37]
        case=dict(region=region,source_first_scene_starts=first_scene_starts,source_line_resets=systems['sms']['reentry_line_resets'],native_line_resets=systems['md']['reentry_line_resets']);cases.append(case);print(region,json.dumps(case),flush=True)
    (out/'report.json').write_text(json.dumps(dict(cases=cases,md_sha256=sha((project/'out/release/rom.bin').read_bytes()),source_sha256=sha((ROOT/'input/original.sms').read_bytes()),frames=a.frames,unsupported_audio_commands=0,ram_writes=0,sram_imports=0,driver_sha256=sha(Path(__file__).read_bytes()),scope='No-input attract-loop observation; these are measurements, not a passing timing gate.'),indent=2)+'\n')

if __name__=='__main__':main()
