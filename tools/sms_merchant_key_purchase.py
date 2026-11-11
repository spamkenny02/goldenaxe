"""Buy the first-listed key, magic refill or Knight Shield with real SMS funds."""
import argparse
import contextlib
import io
import json
from run_core import ROOT,run,FrameWrites,compile_fixed_inputs
from natural_dungeon_combat import walk
from assisted_prefix import prefix_writes,recording
from archive_lossless_evidence import sha


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--sms',action='store_true',required=True)
    p.add_argument('--prefix',required=True)
    p.add_argument('--outside',type=lambda x:int(x,0),required=True)
    p.add_argument('--trial',required=True)
    p.add_argument('--assisted-prefix',action='store_true')
    p.add_argument('--kind',choices=['key','magic','shield'],default='key')
    a=p.parse_args()
    source=ROOT/'validation/natural-dungeon-route'/a.prefix
    cap=json.loads((source/'capture.json').read_bytes())
    prior=json.loads((source/'route_report.json').read_bytes())
    assert prior['reached_entrance'] and prior['failure'] is None and prior['house_outside']==a.outside
    assert cap['sram_input'] is None and cap['rom_sha256']==sha((ROOT/'input/original.sms').read_bytes())
    assets=json.loads((ROOT/'analysis/merchant_assets.json').read_bytes())
    town=next(row for row in assets['towns'] if row[0]==a.outside)
    if a.kind in ('key','shield'):
        assert town[1]==0 and assets['goods'][town[2]][0][0]==(30 if a.kind=='key' else 25)
        price=assets['goods'][town[2]][0][1];magic_gain=0
    else:
        assert town[1]==2
        rom=(ROOT/'input/original.sms').read_bytes();price=rom[0x75af];magic_gain=rom[0x75ac]*8
    house=prior['house_target'];_,nx,ny=next(row for row in assets['nodes'] if row[0]==house)
    start=cap['frames'];presses=list(map(tuple,cap['presses']))
    prior_controls=json.loads((source/'controls.json').read_bytes())
    for i,row in enumerate(prior_controls):
        end=prior_controls[i+1]['frame']-1 if i+1<len(prior_controls) else start
        presses.extend((row['frame'],end,b) for b in row['buttons'])
    masks=compile_fixed_inputs(presses,start)
    writes=prefix_writes(source,cap,a.assisted_prefix)
    folder=ROOT/'validation/natural-service-route'/('sms-'+a.trial);assert not folder.exists()
    state={};first=None;done=None;failure=None;observed=0;direction=0
    controls=list(prior_controls);events=[];captures={start}
    def purchased():
        if first is None:return False
        reward=(state['keys']==first['keys']+1 if a.kind=='key' else
                state['shield']==2 and state['keys']==first['keys'] and state['magic']==first['magic'] if a.kind=='shield' else
                state['magic']==min(first['max_magic'],first['magic']+magic_gain) and state['keys']==first['keys'])
        return reward and state['gold']==first['gold']-price
    def observe(frame,raw):
        nonlocal first,done,failure,observed
        observed=frame
        if frame<start:return
        state.update(room=int.from_bytes(raw[0xb9:0xbb],'little'),game=raw[0x1d],hero=raw[0x301],
                     counter=raw[0x304],x=raw[0x313],y=raw[0x311],health=raw[0x318],
                     gold=raw[0xdd],keys=raw[0xde],magic=raw[0xdb],max_magic=raw[0xdc],shield=raw[0xf2],tilemap=bytes(raw[0x1600:0x1c00]))
        if first is None:
            first={k:v for k,v in state.items() if k!='tilemap'}
            assert state['room']==house and first['gold']>=price
            assert first['keys']<99 if a.kind=='key' else first['shield']<2 if a.kind=='shield' else first['magic']<first['max_magic']
        if not state['health']:failure='hero_died'
        if not events or any(state[k]!=events[-1][k] for k in ('room','game','gold','keys')):
            events.append(dict(frame=frame,**{k:v for k,v in state.items() if k!='tilemap'}));captures.add(frame+1)
        if purchased() and state['room']==a.outside and state['game']==12 and state['hero']==1 and done is None:
            done=frame;captures.add(frame+150)
    def choose(frame):
        nonlocal direction
        if frame<=start:return [b for b in range(16) if masks[frame]&(1<<b)]
        if failure:return []
        if done is not None:return [5] if frame-done<=32 and state['room']==a.outside and state['game']==12 else []
        if state['game']==22:return ([0] if purchased() else [8]) if frame%40==0 else []
        if state['game']!=12 or state['hero']!=1 or state['room']!=house:return []
        if state['counter']:return [4+direction]
        point=state['x'],state['y'];goal=(136,160) if purchased() else (nx,ny)
        if point==goal:direction=1 if purchased() else 0;return [4+direction]
        path=walk(state['tilemap'],point,lambda q:q==goal)
        if path:direction=path[0];return [4+direction]
        return []
    def controller(frame):
        buttons=choose(frame)
        if frame>start and (not controls or controls[-1]['buttons']!=buttons):
            controls.append(dict(frame=frame,buttons=buttons))
        return buttons
    with contextlib.redirect_stdout(io.StringIO()):
        run(ROOT/'input/original.sms',start+6000,folder,captures,cap['presses'],skip_intro=False,
            input_provider=controller,ram_observer=observe,ram_writes=FrameWrites(writes),
            core_options=cap['core_options'],stop_when=lambda:bool(failure) or done is not None and observed>=done+150)
    result=dict(passed=done is not None and failure is None,failure=failure or (None if done is not None else 'frame_limit'),
                rom_sha256=cap['rom_sha256'],source_prefix=a.prefix,outside=a.outside,unit_price=price,
                service_kind=a.kind,keys_bought=1 if a.kind=='key' else 0,magic_points_offered=magic_gain,shields_bought=1 if a.kind=='shield' else 0,
                first_state=first,last_state={k:v for k,v in state.items() if k!='tilemap'},
                complete_frame=done,new_assistance_writes=0,primary_state_imports=0,
                ram_injections=bool(writes),sram_checkpoint_injection=False,
                scope='First-listed merchant option bought with existing gold: key, magic refill or Knight Shield. Other choices, refusals, pages, audio and timing remain open.')
    for name,value in [('report',result),('controls',controls),('events',events)]:
        (folder/(name+'.json')).write_text(json.dumps(value,indent=2)+'\n')
    if writes:
        (folder/'assistance.json').write_bytes((source/'assistance.json').read_bytes())
        recording(folder,json.loads((folder/'capture.json').read_bytes()))
    print(result)


if __name__=='__main__':main()
