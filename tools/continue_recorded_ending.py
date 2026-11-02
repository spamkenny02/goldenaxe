"""Continue a verified real final-boss victory through credits using ordinary input."""
import argparse
import contextlib
import io
import json
from run_core import ROOT, run, FrameWrites
from assisted_prefix import recording, prefix_writes, controlled_sram_input
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from validate_playable_sprite_limit import symbols


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--trace',required=True)
    p.add_argument('--trial',required=True)
    p.add_argument('--controlled-sram-prefix',action='store_true')
    p.add_argument('--extra-frames',type=int,default=14000)
    a=p.parse_args()
    source=(ROOT/'validation'/a.trace).resolve()
    assert source.is_relative_to(ROOT/'validation')
    cap=json.loads((source/'capture.json').read_bytes())
    rom=ROOT/'gaw-megadrive.bin'
    assert sha(rom.read_bytes())==cap['rom_sha256']
    old=json.loads((source/'report.json').read_bytes())
    assert old['ending_handoff_passed'] and old['unassisted_extension'] and old['new_assistance_writes']==0
    assist,writes=recording(source,cap)
    initial=controlled_sram_input(source,cap,a.controlled_sram_prefix)
    assert prefix_writes(source,cap,True,controlled=a.controlled_sram_prefix)==writes
    start=cap['frames']
    assert writes[-1][0]==assist['release_write_frame']<start and writes[-1][2]==b'\0\0'
    expected=evidence(source/f'ram_{start:05d}.bin')
    sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
    controls=json.loads((source/'controls.json').read_bytes())
    timeline=[()]*(start+1)
    for i,row in enumerate(controls):
        stop=controls[i+1]['frame']-1 if i+1<len(controls) else start
        timeline[row['frame']:stop+1]=[tuple(row['buttons'])]*(stop-row['frame']+1)
    folder=ROOT/'validation/natural-dungeon-combat'/('md-auto-'+a.trial)
    assert not folder.exists()
    end=start+a.extra_frames
    captures={start,end}
    state={};events=[];music=[];last_key=None;observed=0
    held=credits_started=completed=returned=ack=None

    def observe(frame,raw):
        nonlocal held,credits_started,completed,returned,observed,last_key
        observed=frame
        if frame<start:return
        if frame==start:assert raw==expected
        data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k))
        word=lambda n:int.from_bytes(data(n,2),'big')
        credit=data('ending_credits',9);actors=data('world_actor_state',768)
        state.update(frame=frame,room=word('room_id'),game=word('game_state'),health=word('hero_health'),
                     hurt=word('hero_hurt'),descriptor=word('ending_hero_descriptor'),
                     credits_done=bool(credit[1]),credit_row=int.from_bytes(credit[4:6],'big'),
                     credit_text=int.from_bytes(credit[6:8],'big'),credit_state_hex=credit.hex(),
                     visible_gems=sum(actors[i*48]==6 and bool(actors[i*48+3]&1) for i in range(9)))
        assert state['health']>0 and state['hurt']<=128
        assert word('sound_unhandled_command')==0
        if frame==start:assert state['game']==14 and data('game_save_state',592)[0x28]==1
        request=word('sound_request')&255
        if request and (not music or music[-1]['command']!=request):music.append(dict(frame=frame,command=request))
        if held is None and state['descriptor']==0x8495 and state['visible_gems']==9:
            held=frame;captures.add(frame+1)
        if credits_started is None and state['descriptor']==0x84e1 and 0x7800<=state['credit_row']<0x7f00 and state['credit_text']:
            credits_started=frame;captures.add(frame+1)
        if credits_started is not None and completed is None:
            if (frame-credits_started)%1000==0:captures.add(frame+1)
            if state['credits_done']:completed=frame;captures.add(frame+1)
        if completed is not None and state['game']==0 and state['descriptor']==0 and returned is None:
            assert ack is not None
            returned=frame;captures.add(frame+100)
        key=(state['game'],state['descriptor'],state['credits_done'],state['visible_gems'])
        if key!=last_key:events.append(dict(state));last_key=key

    def controller(frame):
        nonlocal ack
        if frame<=start:return timeline[frame]
        # The final credits tick still waits once before the source records
        # previous=input for its acknowledgement loop. Supply a fresh edge
        # after that loop is waiting, rather than holding C across entry.
        if completed is not None and frame>=completed+30 and ack is None:ack=frame
        value=[8] if ack is not None and ack<=frame<ack+3 else []
        if not controls or controls[-1]['buttons']!=value:controls.append(dict(frame=frame,buttons=value))
        return value

    with contextlib.redirect_stdout(io.StringIO()):
        run(rom,end,folder,captures,cap['presses'],
            ram_writes=FrameWrites(writes),ram_observer=observe,input_provider=controller,
            core_options=cap['core_options'],sram_in=initial,
            stop_when=lambda:returned is not None and observed>=returned+100)
    passed=all(v is not None for v in [held,credits_started,completed,returned])
    report=dict(passed=passed,failure=None if passed else 'ending_frame_limit',
                rom_sha256=cap['rom_sha256'],last_state=dict(state),
                ending_complete=passed,nine_gems_visible_frame=held,credits_started_frame=credits_started,
                credits_finished_frame=completed,acknowledgement_frame=ack,title_flow_return_frame=returned,
                music_requests=music,recorded_victory_prefix=a.trace,unassisted_extension=True,
                new_assistance_writes=0,primary_state_imports=int(bool(initial)),
                natural_campaign_proof=False,rom_modifications=False,
                driver_sha256=sha((ROOT/'tools/continue_recorded_ending.py').read_bytes()),
                scope='Actual final-boss handoff prefix; ordinary C acknowledges completed credits. No further RAM/state writes. Return to title flow includes its subsequent intro, not a claim of every final-title framebuffer matching SMS.')
    if initial:report.update(controlled_sram_fixture=True,game_written_save=False,sram_checkpoint_injection=True,sram_sha256=sha(initial.read_bytes()))
    for name,value in [('report',report),('controls',controls),('events',events),('assistance',assist)]:
        (folder/(name+'.json')).write_bytes((json.dumps(value,indent=2)+'\n').encode('utf-8'))
    recording(folder,json.loads((folder/'capture.json').read_bytes()))
    print('Real victory ending and title flow:',passed,held,credits_started,completed,returned)
    assert passed


if __name__=='__main__':
    main()
