"""Audit all 18 PAL D5 stages, real purchases, satellites and unassisted return."""
import json,sys
from pathlib import Path
sys.path.insert(0,'tools')
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated

work=Path(__file__).resolve().parent
project=work/'isolated/project'
paths={Path(__file__).resolve(),work/'prepare_pal_d5.py'}
def read(p): paths.add(p); return p.read_bytes()
def load(p): return json.loads(read(p))

digest=sha((project/'gaw-megadrive.bin').read_bytes())
assert digest=='9e747d38e0c6fb2d69b7c1aa8c2b296a61e8b6af41171d14e543ed9a6cb49cf5'
prior=load(ROOT/'analysis/palc0046_fire_sword_report.json')
assert prior['passed'] and prior['fifth_dungeon_entered'] and prior['rom_sha256']==digest and prior['region']=='pal'
snapshot=project/'validation/palc0046-d5-sources'
for n,h in load(snapshot/'source_index.json').items():
    assert sha(read(snapshot/Path(n).name))==h and sha(read(project/n))==h
read(snapshot/'commands.jsonl')
sy=symbols(project/'megadrive/out/release/symbol.txt')
source=read(ROOT/'input/original.sms')
assert source[0x3234e+0x163*8]==0x65 and source[0x320ea+(0x65-0x20)*4]==72
stream=load(project/'validation/palc0046-d5-cold-stream01/completed.json')
assert stream['passed'] and stream['cold_boot_count']==1 and stream['rom_sha256']==digest
assert len(stream['checkpoints'])==18 and all(c['whole_ram_png_exact'] for c in stream['checkpoints'])
previous=ROOT/prior['current_campaign_trace'];pc=load(previous/'capture.json');pa,pw=recording(previous,pc)
stages=[];transactions={};release=None;fixed=None;boss_report=None;boss_assist=None;boss_folder=None
expected=['key01','earth01','boots01','supply-exit01','golda1-entry01','golda1-gift01','goldb4-entry01','goldb4-gift01','merchant94-entry01','key94-buy01','return-entry01','warp01','contact01','approach01','release01','boss01','return-contact01','exit01']
for suffix,checkpoint in zip(expected,stream['checkpoints']):
    folder=project/'validation'/checkpoint['trace'];family=folder.parent.name;f=checkpoint['frames']
    assert folder.name.endswith('palc0046-d5-'+suffix)
    c=load(folder/'capture.json');r=load(folder/('route_report.json' if family=='natural-dungeon-route' else 'report.json'));a,w=recording(folder,c)
    assert c['rom_sha256']==r['rom_sha256']==digest and c['sram_input'] is None and c['core_options']['genesis_plus_gx_region_detect']=='pal' and c['frames']==f>pc['frames']
    assert r['failure'] is None and not r.get('deaths',0) and not a['primary_state_imports'] and not a['health_refills'] and not a['boss_assistance'] and a['boss_room']==0x163
    assert w[:len(pw)]==pw and all(addr==sy['hero_hurt'] and value in (b'\0\0',b'\0\x81') for _,addr,value in w)
    if family=='natural-service-route':
        assert r['source_prefix']==previous.name and r['passed'] and not r['new_assistance_writes'] and w==pw
        before,after=r['first_state'],r['last_state'];transactions[suffix]=dict(before=before,after=after)
        if suffix.endswith('gift01'):
            assert r['kind']=='gold' and after['gold']-before['gold']==30 and after['outside_flags']&2
        else:
            assert suffix=='key94-buy01' and r['keys_bought']==1 and r['unit_price']==60 and before['gold']-after['gold']==60 and after['keys']==before['keys']+1
            assert r['free_healing_requested'] and r['free_healing_completed'] and after['health']==after['max_health']==64 and not r['currency_or_inventory_fixtures']
    else:
        assert r['prefix_end']==pc['frames']
        if family=='natural-dungeon-route':assert previous.name in (r.get('recorded_combat_prefix'),r.get('recorded_service_prefix')) and r['reached_entrance'] and r['directional_probe_succeeded']
        else:assert r['recorded_new_game_prefix']==previous.name and not r['rom_modifications'] and not r['sram_checkpoint_injection']
    proof=folder.with_name(folder.name+f'-assisted-fixed-replay-{f}');pr=load(proof/'replay_report.json')
    assert pr['passed'] and pr['rom_sha256']==digest and pr['whole_ram_bytes']==65536 and pr['final_png_exact'] and not pr['feedback_reads']
    for n,h in pr['evidence'].items():assert sha(read(folder/n))==h
    for stem,ext in [('ram','bin'),('frame','png')]:assert read(folder/f'{stem}_{f:05d}.{ext}')==read(proof/f'{stem}_{f:05d}.{ext}')
    raw=read(folder/f'ram_{f:05d}.bin');data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
    items=data('hero_items',17);save=data('game_save_state',592)
    assert word('game_state')==12 and word('hero_health')>0 and not word('sound_unhandled_command')
    assert items[0]==2 and items[1]==items[4]==items[5]==items[12]==items[13]==1 and not items[8]
    if suffix=='key01':assert r['new_key_verified']
    if suffix in ('earth01','warp01'):
        room,cell,dest=(0x176,0x4a,0x166) if suffix=='earth01' else (0x153,0x44,0x162)
        assert r['earth_route_passed'] and r['earth_passage_opened'] and r['earth_passage_traversed'] and not r['earth_state_writes'] and r['earth_passage_room']==room and r['earth_cell']==cell and word('room_id')==dest
    if suffix=='boots01':assert r['item_acquisition_passed'] and r['collect_item_requested']==14 and r['collect_item_target_value']==1 and not r['item_acquisition_state_writes']
    if expected.index(suffix)>=2:assert items[14]==1
    if suffix in ('contact01','return-contact01'):
        room,dest=(0x162,0x172) if suffix=='contact01' else (0x173,0x174)
        assert r['contact_route_passed'] and not r['contact_state_writes'] and r['contact_room']==room and r['contact_destination']==dest
    if suffix=='release01':
        release=f;fixed=w;assert word('hero_hurt')==0 and a['closed_before_room']==0x163 and w==pw+[(f,sy['hero_hurt'],b'\0\0')]
    if suffix in ('boss01','return-contact01','exit01'):
        assert w==fixed and not r['new_assistance_writes'] and r['unassisted_extension'] and r['guard_release_frame']==release and r['extension_guard_checks_through_frame']==f
        assert pr['live_boss_guard_check'] and r['unassisted_controller_sha256']==sha(read(project/'tools/unassisted_dungeon_continuation.py'))
        assert save[0x1f:0x28]==bytes([128]*5+[0]*4) and word('hero_max_health')==72
    else:assert save[0x1f:0x28]==bytes([128]*4+[0]*5) and word('hero_max_health')==64
    if suffix=='boss01':
        first=r['first_intermediate_combat'];assert first['room']==0x163 and first['frame']>release and first['health']>0 and first['hurt']==0 and any(e['kind']==0x65 and e['hp']==72 for e in first['actors'])
        assert r['room_cleared'] and r['collect_gem_requested'] and not word('item_reward_active') and r['satellites_in_input_search'] and r['arrival_checked_on_every_entry']
        assert r['arrival_controller_sha256']==sha(read(project/'tools/unassisted_satellite_arrival.py')) and r['satellite_controller_sha256']==sha(read(project/'tools/unassisted_satellite_boss.py'))
        assert r['full_ram_prediction_matches']==r['verified_persistent_prediction_windows']>0 and not r['stack_only_difference_windows']
        boss_report,boss_assist,boss_folder=r,a,folder
    if suffix=='exit01':
        assert r['full_dungeon_cleared'] and r['dungeon_exit_verified'] and word('room_id')==0x49 and not word('world_dungeon_number')
        assert r['full_ram_prediction_matches']==r['verified_persistent_prediction_windows']>0 and not r['stack_only_difference_windows']
    stages.append(dict(trace=folder.relative_to(ROOT).as_posix(),frame=f,stage=suffix,room=word('room_id'),health=word('hero_health'),max_health=word('hero_max_health'),magic=word('hero_magic'),whole_ram_png_exact=True))
    read(folder/'assistance.json');read(folder/'controls.json');previous,pc,pa,pw=folder,c,a,w
events=load(boss_folder/'events.json');combat=[row for row in events if row['room']==0x163 and row['game']==12]
assert max(sum(e['type']==0x66 and e['hp']>0 for e in row['actors']) for row in combat)==8
spawned=min(row['frame'] for row in combat if sum(e['type']==0x66 and e['hp']>0 for e in row['actors'])==8)
vulnerable=next(row['frame'] for row in combat if row['frame']>spawned and any(e['type']==0x65 and 0<e['hp']<72 for e in row['actors']) and not any(e['type']==0x66 and e['hp'] for e in row['actors']))
sms=data('sms_vram',16384);vram=read(previous/f'vram_{f:05d}.bin');regs=read(previous/f'vdp_regs_{f:05d}.bin');base=(regs[2]&56)<<10;width=[32,64,32,128][regs[16]&3]
for n in range(128):
    at=base+((n//32+22)*width+n%32)*2;assert int.from_bytes(vram[at:at+2],'little')==translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2],'little'))
out=ROOT/'analysis/palc0046-d5'
r=dict(passed=True,candidate='c0046',region='pal',rom_sha256=digest,stages=stages,current_campaign_trace=stages[-1]['trace'],campaign_frames=f,actual_fifth_crystal_and_exterior=True,transactions=transactions,boots_owned=True,satellites_observed=8,first_core_damage=vulnerable,guard_release_frame=release,first_boss_combat=boss_report['first_intermediate_combat'],boss_prediction_windows=boss_report['full_ram_prediction_matches'],physical_hud_words_exact=128,full_candidate_campaign_verified=False,archive_manifest=(out/'manifest.json').relative_to(ROOT).as_posix(),scope='Actual PAL D5 with boots, real gold gifts,60-piece key and ordinary healing, Earth/contact mechanisms, source-strength satellite boss and exterior return. Eighteen cold RAM/PNG checkpoints; approach protection removed before boss. No resource, actor, progression or initial SRAM import. Global SMS fidelity remains open.')
freeze(ROOT,out,paths,r,[work]);(ROOT/'analysis/palc0046_d5_report.json').write_text(json.dumps(r,indent=2)+'\n')
print('PAL D5 full route, real supplies, satellite boss and exterior return audited',flush=True)
