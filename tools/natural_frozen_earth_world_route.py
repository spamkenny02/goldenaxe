"""Ring the owned Ice Bell before an exterior Earth cast; freeze lava if present."""
import json,sys
from pathlib import Path
import natural_dungeon_route as game
import natural_earth_world_route as earth
from run_core import ROOT
from archive_lossless_evidence import sha


def main():
    sms='--sms' in sys.argv
    from md_readonly_view import md_to_sms_view
    from validate_playable_sprite_limit import symbols
    sy=None if sms else symbols(ROOT/'megadrive/out/release/symbol.txt')
    outside=int(sys.argv[sys.argv.index('--house-outside')+1],0);assert 0x10<=outside<0xff
    flag='--prefix-combat' if '--prefix-combat' in sys.argv else '--prefix-service'
    family='natural-dungeon-combat' if flag=='--prefix-combat' else 'natural-service-route'
    p=ROOT/'validation'/family/sys.argv[sys.argv.index(flag)+1]
    cap=json.loads((p/'capture.json').read_bytes());start=cap['frames']
    raw=(p/f'ram_{start:05d}.bin').read_bytes()
    if not sms:raw=md_to_sms_view(raw,sy)
    assert raw[0xea] and raw[0xe5]
    original_run,original_render=game.run,game.World.render_cells
    state={};events=[];controls=[];result={};finished=False
    def render(world,room,cells,meta=None):
        # A proposed path only. The actual primary machine must ring the Bell.
        if room==outside:cells=bytearray(0x3a if b==0x3f else b for b in cells)
        return original_render(world,room,cells,meta)
    def wrapped(*args,**kwargs):
        result['folder']=Path(args[2]);observe_base=kwargs['ram_observer'];control_base=kwargs['input_provider']
        def observe(f,r):
            observe_base(f,r)
            if f<start:return
            if not sms:r=md_to_sms_view(r,sy)
            state.update(room=int.from_bytes(r[0xb9:0xbb],'little'),game=r[0x1d],hero=r[0x301],counter=r[0x304],
                selected=r[0xdf],slot=r[0xa0],bell=r[0xac],lava=bytes(r[0x1c00:0x1ca0]).count(0x3f),terrain=r[0x41])
            if state['room']==outside and (not events or any(state[k]!=events[-1][k] for k in ['bell','lava','selected'])):
                events.append(dict(frame=f,**state));args[3].add(f+1)
        def control(f):
            nonlocal finished
            if f>start and state.get('room')==outside and state['bell'] and state['selected']==1 and state['game']==12 and state['hero']==1:finished=True
            if f<=start or state.get('room')!=outside or finished or state['terrain'] in (3,5):value=control_base(f)
            else:
                value=[];wanted=1 if state['bell'] else 10
                if f%20==0:
                    if state['game']==12 and state['hero']==1 and not state['counter']:
                        value=[8] if state['selected']==10 and not state['bell'] else [0]
                    elif state['game']==16:
                        if state['selected']==wanted:value=[0]
                        elif state['slot']//4!=wanted//4:value=[5 if state['slot']//4<wanted//4 else 4]
                        elif state['slot']%4!=wanted%4:value=[7 if state['slot']%4<wanted%4 else 6]
                        else:value=[8]
            if not controls or controls[-1]['buttons']!=list(value):controls.append(dict(frame=f,buttons=list(value)))
            return value
        kwargs.update(ram_observer=observe,input_provider=control);return original_run(*args,**kwargs)
    game.run=wrapped;game.World.render_cells=render
    try:earth.main()
    finally:game.run=original_run;game.World.render_cells=original_render
    folder=result['folder'];report=json.loads((folder/'route_report.json').read_bytes())
    frozen=next((e for e in events if e['bell'] and not e['lava']),None)
    assert not report['reached_entrance'] or frozen and finished
    report.update(lava_frozen_by_owned_bell=frozen,freeze_controller_sha256=sha(Path(__file__).read_bytes()),freeze_resource_or_terrain_writes=0)
    for name,value in [('controls',controls),('freeze_events',events),('route_report',report)]:
        (folder/(name+'.json')).write_text(json.dumps(value,indent=2)+'\n')


if __name__=='__main__':main()
