"""Replay the measured glyph-entry cases on a private 68000 candidate."""
import argparse
import contextlib
import io
import json
from pathlib import Path

from archive_lossless_evidence import sha
from run_core import ROOT,run
from validate_playable_sprite_limit import symbols


def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--symbols',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    out=a.out.resolve();assert out.is_relative_to(ROOT/'validation');out.mkdir(parents=True,exist_ok=False)
    sy=symbols(a.symbols);reference=ROOT/'validation/menu-audio-v0316/name-map-model02'
    source=json.loads((reference/'report.json').read_bytes());assert source['correct_unambiguous_cases']==len(source['cases'])==210
    cases=[]
    for case in source['cases']:
        region=case['region'];cursor=case['cursor'];typed=case['typed_frame'];tag=region+'-'+str(cursor)+'-'+str(typed)
        moves=[(1110+2*i,1110+2*i,5)for i in range(cursor//12)]
        moves += [(1110+2*(cursor//12+i),1110+2*(cursor//12+i),7)for i in range(cursor%12)]
        rows={}
        def observe(frame,raw):
            def data(name,size):return bytes(raw[(sy[name]+i)^1]for i in range(size))
            def word(name):return int.from_bytes(data(name,2),'big')
            assert not word('sound_unhandled_command'),(tag,frame,'audio or scheduler error')
            if typed-1<=frame<=typed+2:
                rows[frame]=dict(audio=data('sound_ram',400),cursor=word('name_cursor'),position=word('name_position'),pending_effect=word('sound_effect_request'))
        folder=out/tag
        with contextlib.redirect_stdout(io.StringIO()):run(a.rom,typed+2,folder,{typed+2},
            [(200,220,0),(920,935,0),(1050,1065,0)]+moves+[(typed,typed+2,8)],skip_intro=False,
            ram_observer=observe,core_options={'genesis_plus_gx_region_detect':'pal'if region=='pal'else'auto'})
        mismatches=[];raw_mismatches=[]
        for frame,row in rows.items():
            expected=(reference/tag/f'ram_{frame:05d}.bin').read_bytes()
            audio=expected[0x1e00:0x1f90]
            native=bytearray(row['audio']);assert row['pending_effect']<=255
            raw_indices=[i for i,(s,m)in enumerate(zip(audio,native))if s!=m]
            if raw_indices:raw_mismatches.append(dict(frame=frame,audio_indices=raw_indices))
            if row['pending_effect']:native[8]=row['pending_effect']
            differing=[i for i,(s,m)in enumerate(zip(audio,native))if s!=m]
            if differing:mismatches.append(dict(frame=frame,audio_indices=differing))
        assert rows[typed-1]['cursor']==cursor and rows[typed+2]['position']==1,(tag,'name input')
        (folder/'audio-observations.bin').write_bytes(b''.join(row['audio']for row in rows.values()))
        (folder/'pending-effects.json').write_text(json.dumps({f:r['pending_effect']for f,r in rows.items()})+'\n')
        cases.append(dict(region=region,cursor=cursor,typed_frame=typed,audio_mismatches=mismatches,
                          raw_audio_mismatches=raw_mismatches,source_irq_lost=case['actual_loss'],name_input_succeeded=True))
    result=dict(passed=all(not row['audio_mismatches']for row in cases),md_sha256=sha(a.rom.read_bytes()),cases=cases,
                source_report_sha256=sha((reference/'report.json').read_bytes()),ram_writes=0,sram_imports=0,
                compared_logical_audio_bytes_per_frame=400,normalization='Native pending effect request supplies source DE08 while queued; raw bytes are retained separately.',frames_per_case=4,driver_sha256=sha(Path(__file__).read_bytes()),
                scope='210 natural first-glyph cases and the surrounding four audio states; simultaneous direction plus typing and a full campaign remain separate.')
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Natural name-input cases:',sum(not r['audio_mismatches']for r in cases),'/',len(cases),'logical400-byte states exact.',flush=True)
    print('First mismatches:',[r for r in cases if r['audio_mismatches']][:3],flush=True)


if __name__=='__main__':main()
