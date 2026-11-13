"""Shared proposals for real MD house entry; proposals never count as visits."""
from continue_sms_plain_house_census import COMBAT_ENTRANCES
from extract_title import rle_planes
import json,subprocess,sys
from run_core import ROOT
from continue_sms_plain_house_census import census_world
def entry_options(raw,outside,house,direction,world):
    extra=['--house-outside',hex(outside),'--house-target',hex(house),'--persisted-only','--live-prefix-terrain','--door-entry-direction',str(direction)]
    if outside in COMBAT_ENTRANCES and not raw[0x100+outside]&1:extra+=['--fight-for-entrance']
    tool='natural_bell_world_route.py';meta=world.arrays['world_room_metadata'];node=next((meta[i:i+4] for i in range(0,len(meta)-3,4) if meta[i]==outside),None)
    reveal_matches_goal=(node is not None and node[3] in (0,2,3,4,5,7)
        and (world.goal['x'],world.goal['y'])==((node[2]&15)*16+8,(node[2]&240)+16))
    if reveal_matches_goal and not raw[0x100+outside]&1:
        cells=bytearray(160);ptr=int.from_bytes(world.arrays['world_room_index'][outside*2:outside*2+2],'little');rle_planes(world.arrays['world_room_streams'],ptr,cells,0,1)
        kind=cells[node[1]]
        if kind in (0x13,0x38,0x3d,0x85,0x86):
            if not raw[0xe5] or kind in (0x38,0x3d,0x85) and raw[0xe5]<2:return None
            tool='natural_frozen_earth_world_route.py' if kind==0x38 else 'natural_earth_world_route.py';extra+=['--earth-world-cell',hex(node[1])]
        elif 0x80<=kind<=0x84 and node[1]!=node[2]:extra+=['--required-chop',f'{hex(outside)}:{hex(node[1])}']
    return tool,extra

def enter(c,outside,house,tag,bell_room=None):
    """Try feasible approaches from the same verified prefix, retaining failures."""
    if c.sms_view()[0xe1] and c.sms_view()[0xdf]!=1:c.equip(1,tag+'-equip-axe')
    previous=c.family,c.current;raw=c.sms_view()
    start=(int.from_bytes(raw[0xb9:0xbb],'little'),raw[0x313],raw[0x311])
    for direction in range(4):
        c.family,c.current=previous
        world=census_world(raw,outside,house,direction)
        if outside==0x2c:
            render=world.render_cells
            world.render_cells=lambda room,cells,meta=None,render=render:render(room,bytearray(0x3a if b==0x3f else b for b in cells) if room==outside else cells,meta)
        options=entry_options(raw,outside,house,direction,world)
        if not options or world.route(start)[0] is None:continue
        tool,extra=options
        if '--earth-world-cell' in extra:assert raw[0xdb]>=8,('Actual magic refill required before Earth route',outside)
        if bell_room is not None and not raw[0x100+bell_room]&1:
            extra=[x for x in extra if x!='--persisted-only'];extra+=['--bell-room',hex(bell_room)]
        n=1
        while (ROOT/f'validation/natural-dungeon-route/md-{c.label}-{tag}-entry{n:02d}').exists():n+=1
        try:
            c.route(tag+f'-entry{n:02d}',extra,tool);return n
        except (AssertionError,subprocess.CalledProcessError):
            path=ROOT/f'validation/natural-dungeon-route/md-{c.label}-{tag}-entry{n:02d}/route_report.json'
            if not path.exists():raise
            failed=json.loads(path.read_bytes())
            if failed.get('failure') not in ('unexpected_position','no_waypoint_progress','frame_limit') or failed.get('normal_continues') or not failed['last_state']['health']:raise
            print('MD ENTRY PLANNER RETRY',tag,direction,failed['failure'],flush=True)
    c.family,c.current=previous
    raise AssertionError(('No actual entry verified from feasible approaches',outside,house))

def film(c,name,first):
    with (ROOT/'validation'/(name+'-video.log')).open('w') as log:
        subprocess.run([sys.executable,str(ROOT/'tools/record_md_annex.py'),'--trace',c.trace,'--rom',str(c.rom),'--from-frame',str(first),'--name',name],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)

def fund_wallet(c,minimum):
    """Receive unclaimed positive gifts; never write currency."""
    assert 0<minimum<=255
    while c.sms_view()[0xdd]<minimum:
        raw=c.sms_view();start=(int.from_bytes(raw[0xb9:0xbb],'little'),raw[0x313],raw[0x311]);options=[]
        for outside,gain in json.loads((ROOT/'analysis/house_gold_reference.json').read_bytes())['records']:
            if not 0<gain<128 or raw[0x100+outside]&2:continue
            world=census_world(raw,outside,0x3f,0);proposal=entry_options(raw,outside,0x3f,0,world)
            if not proposal or '--earth-world-cell' in proposal[1] and raw[0xdb]<8:continue
            path,_=world.route(start)
            if path is not None:options.append(((minimum-raw[0xdd]+gain-1)//gain,len(path),outside,gain))
        assert options,'No reachable unclaimed gold gift for actual refill'
        _,_,outside,gain=min(options);tag=f'fund-wallet-{outside:02x}'
        attempt=enter(c,outside,0x3f,tag);first=c.cap()['frames']+1
        c.service(tag+f'-gift{attempt:02d}','natural_house_service',['--outside',hex(outside),'--kind','gold','--gold-gain',str(gain)])
        film(c,f'md-{c.label}-{tag}-gift{attempt:02d}',first)

def refill_magic(c):
    """Buy a real refill with earned gold."""
    fund_wallet(c,20)
    raw=c.sms_view();assert raw[0xdb]<raw[0xdc] and raw[0xdd]>=20
    start=(int.from_bytes(raw[0xb9:0xbb],'little'),raw[0x313],raw[0x311]);options=[]
    for outside,mode,_ in json.loads((ROOT/'analysis/merchant_assets.json').read_bytes())['towns']:
        if mode!=2:continue
        for direction in range(4):
            world=census_world(raw,outside,0x2f,direction);proposal=entry_options(raw,outside,0x2f,direction,world)
            if not proposal or '--earth-world-cell' in proposal[1]:continue
            path,_=world.route(start)
            if path is not None:options.append((len(path),outside))
    assert options,'No reachable magic merchant without spending missing MP'
    _,outside=min(options);tag=f'magic-refill-{outside:02x}';attempt=enter(c,outside,0x2f,tag);first=c.cap()['frames']+1
    c.service(tag+f'-buy{attempt:02d}','natural_merchant_purchase',['--outside',hex(outside),'--kind','magic','--count','1'])
    film(c,f'md-{c.label}-{tag}-buy{attempt:02d}',first)
    assert c.sms_view()[0xdb]>=8
