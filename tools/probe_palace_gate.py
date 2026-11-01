"""Controlled post-nine-crystal gate probe; never a natural campaign proof."""
import contextlib,io,json,sys
from pathlib import Path
from run_core import ROOT,run
from validate_actor_tick import PRESSES
from validate_playable_sprite_limit import symbols
from archive_lossless_evidence import sha


def main():
    trial=sys.argv[1];source=(ROOT/'input/original.sms').read_bytes();sy=symbols(ROOT/'megadrive/out/release/symbol.txt');results=[]
    for complete in [False,True]:
        for tag in ['sms','md']:
            folder=ROOT/f'validation/palace-gate-{trial}-{tag}-{int(complete)}';assert not folder.exists()
            gems=bytes([128]*8+[128 if complete else 0]);rows=[]
            if tag=='sms':
                writes=[(2800,0xb9,b'\x9b\x00'),(2800,0xa4,source[0xb762+0x9b*2:0xb764+0x9b*2]),(2800,0x310,(8<<8).to_bytes(2,'little')+(136<<8).to_bytes(2,'little')),(2800,0xcf,gems),(2800,0xf8,b'\x00')]
            else:
                def word(name,value):return (2800,sy[name],value.to_bytes(2,'big'))
                writes=[word('room_id',0x9b),word('hero_y',8<<8),word('hero_x',136<<8),(2800,sy['game_save_state']+0x1f,gems),(2800,sy['game_save_state']+0x48,b'\x00')]
            def observe(frame,raw):
                if frame<2799:return
                if tag=='sms':
                    state=dict(room=int.from_bytes(raw[0xb9:0xbb],'little'),game=raw[0x1d],hero=raw[0x301],seen=raw[0xf8],flags=raw[0x100+0x8b],scroll=raw[0x18],clock=raw[0x2f],sat=raw[0x1d80:0x1dc0].hex(),cells=raw[0x1c30:0x1c31].hex())
                else:
                    data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));w=lambda n:int.from_bytes(data(n,2),'big');save=data('game_save_state',592)
                    state=dict(room=w('room_id'),game=w('game_state'),hero=w('hero_state'),seen=save[0x48],flags=save[0x50+0x8b],cells=data('scratch',4096)[0x830:0x831].hex(),scroll=int.from_bytes(data('world_hscroll',448)[32:34],'big',signed=True)&255,clock=(int.from_bytes(data('vtimer',4),'big')-int.from_bytes(data('world_clock_shift',4),'big'))&255)
                if frame==2799:
                    assert state['game']==12 and state['hero']!=0, ('Controlled fixture requires completed playable boot',tag,state)
                    return
                if not rows or any(state.get(n)!=rows[-1].get(n) for n in ['room','game','hero','seen','flags','scroll','cells']):rows.append(dict(frame=frame,**state))
            captures={2800,2836,2850,2882,2914,2946,2978,3010,3042,3074,3106,3140,3200,3300,3500}
            with contextlib.redirect_stdout(io.StringIO()):run(ROOT/('input/original.sms' if tag=='sms' else 'gaw-megadrive.bin'),3500,folder,captures,([(200,220,0)] if tag=='sms' else [])+PRESSES[:8]+[(2801,2820,4)],ram_writes=writes,ram_observer=observe,skip_intro=True)
            assert rows[-1]['room']==0x8b and rows[-1]['game']==12
            (folder/'observations.json').write_bytes((json.dumps(rows,indent=2)+'\n').encode());print(tag,complete,'last',rows[-1],flush=True)
            results.append(dict(platform=tag,complete=complete,trace=folder.relative_to(ROOT).as_posix(),event_frame=next((r['frame'] for r in rows if r['seen']),None),first_room8b=next((r['frame'] for r in rows if r['room']==0x8b),None),last=rows[-1]))
    report=dict(md_sha256=sha((ROOT/'gaw-megadrive.bin').read_bytes()),source_sha256=sha(source),cases=results,controlled_fixtures=True,boot_playable_verified=True,natural_campaign_proof=False)
    (ROOT/f'analysis/palace_gate_{trial}_probe.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())

if __name__=='__main__':main()
