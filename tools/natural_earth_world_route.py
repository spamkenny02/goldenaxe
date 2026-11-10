"""Reveal an exterior entrance with the owned Earth spell and ordinary input."""
import argparse,json,sys
from pathlib import Path
import natural_dungeon_route as game
import natural_dungeon_combat as combat
import natural_bell_world_route as persistent
from run_core import ROOT
from archive_lossless_evidence import sha


def main():
    p=argparse.ArgumentParser(add_help=False);p.add_argument('--earth-world-cell',type=lambda v:int(v,0),required=True)
    a,remaining=p.parse_known_args();assert '--sms' in remaining
    outside=int(remaining[remaining.index('--house-outside')+1],0);index=a.earth_world_cell
    flag='--prefix-combat' if '--prefix-combat' in remaining else '--prefix-service'
    family='natural-dungeon-combat' if flag=='--prefix-combat' else 'natural-service-route'
    cap=json.loads((ROOT/'validation'/family/remaining[remaining.index(flag)+1]/'capture.json').read_bytes())
    start=cap['frames'];original=game.run;state={};actual=[];events=[];result={};opened=None;approached=False;direction=0;sequence=False
    cast=((index&15)*16+8,(index&240)+24);behind=(cast[0],cast[1]+8)
    assert 8<=cast[0]<=248 and 8<=cast[1]<=160
    def wrapped(*args,**kwargs):
        result['folder']=Path(args[2]);base_observe=kwargs['ram_observer'];base_control=kwargs['input_provider']
        def observe(f,r):
            nonlocal opened
            base_observe(f,r)
            if f<start:return
            state.update(room=int.from_bytes(r[0xb9:0xbb],'little'),game=r[0x1d],hero=r[0x301],counter=r[0x304],
                x=r[0x313],y=r[0x311],direction=r[0x30a],selected=r[0xdf],slot=r[0xa0],level=r[0xe5],magic=r[0xdb],
                flags=r[0x100+outside],cell=r[0x1c00+index],spell=r[0x330],tilemap=bytes(r[0x1600:0x1c00]))
            if state['room']==outside and state['game']==12:
                assert state['level'] and state['magic']>=0
                row={k:v for k,v in state.items() if k!='tilemap'}
                if not events or any(row[k]!=events[-1][k] for k in ['flags','cell','selected','magic']):events.append(dict(frame=f,**row));args[3].add(f+1)
                if state['flags']&1 and opened is None:opened=dict(frame=f,**row)
        def control(f):
            nonlocal approached,direction,sequence
            if f>start and state.get('room')==outside and not sequence and opened is None:
                if abs(state['x']-cast[0])+abs(state['y']-cast[1])<=24:
                    sequence=combat.walk(state['tilemap'],(state['x'],state['y']),lambda q:q==cast) is not None
            active=f>start and sequence and state.get('room')==outside
            if not active:value=base_control(f)
            elif state['selected']!=(1 if opened else 5) or state['game']==16:
                value=[];wanted=1 if opened else 5
                if f%20==0:
                    if state['game']==12 and state['hero']==1:value=[0]
                    elif state['game']==16:
                        if state['selected']==wanted:value=[0]
                        elif state['slot']//4!=wanted//4:value=[5 if state['slot']//4<wanted//4 else 4]
                        elif state['slot']%4!=wanted%4:value=[7 if state['slot']%4<wanted%4 else 6]
                        else:value=[8]
            elif state['game']!=12 or state['hero'] not in (0,1):value=[]
            elif state['spell']:value=[]
            elif opened:value=[4]
            elif (state['x'],state['y'])==cast and state['direction']==0:value=[] if state['counter'] or f%3==0 else [8]
            elif state['counter']:value=[4+direction]
            elif (state['x'],state['y'])==cast:value=[4]
            else:
                point=(state['x'],state['y'])
                if point==behind:approached=True
                path=combat.walk(state['tilemap'],point,lambda q:q==(cast if approached else behind));value=[]
                if path is None:path=combat.walk(state['tilemap'],point,lambda q:q==cast)
                if path is None:value=base_control(f)
                if path:direction=path[0];value=[4+direction]
            if not actual or actual[-1]['buttons']!=list(value):actual.append(dict(frame=f,buttons=list(value)))
            return value
        kwargs.update(ram_observer=observe,input_provider=control);return original(*args,**kwargs)
    game.run=wrapped;sys.argv=[sys.argv[0]]+remaining
    try:persistent.main()
    finally:game.run=original
    folder=result['folder'];report=json.loads((folder/'route_report.json').read_bytes())
    assert not report['reached_entrance'] or opened is not None
    report.update(earth_exterior_opened=opened,earth_exterior_cell=index,earth_exterior_new_resource_writes=0,
                  earth_exterior_driver_sha256=sha(Path(__file__).read_bytes()))
    for name,value in [('controls',actual),('earth_world_events',events),('route_report',report)]:
        (folder/(name+'.json')).write_bytes((json.dumps(value,indent=2)+'\n').encode())


if __name__=='__main__':main()
