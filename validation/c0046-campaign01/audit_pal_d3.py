"""Audit actual PAL oil, rope, third crystal and return across the verified controller recovery."""
import json,sys
from pathlib import Path
sys.path.insert(0,'tools')
from run_core import ROOT
from assisted_prefix import recording
from archive_lossless_evidence import freeze,sha
from validate_playable_sprite_limit import symbols
work=Path(__file__).resolve().parent;project=work/'isolated/project';paths={Path(__file__).resolve(),work/'prepare_pal_d3.py',work/'resume_pal_d3.py'}
def read(p):paths.add(p);return p.read_bytes()
def load(p):return json.loads(read(p))
digest=sha((project/'gaw-megadrive.bin').read_bytes());assert digest=='9e747d38e0c6fb2d69b7c1aa8c2b296a61e8b6af41171d14e543ed9a6cb49cf5'
prior=load(ROOT/'analysis/palc0046_d2_report.json');assert prior['passed'] and prior['region']=='pal' and prior['rom_sha256']==digest and prior['actual_second_crystal_and_exterior']
for name in ('palc0046-d3-sources','palc0046-d3-resumed-sources01'):
    folder=project/'validation'/name;index=load(folder/'source_index.json')
    for n,h in index.items():assert sha(read(folder/Path(n).name))==h and sha(read(project/n))==h
sy=symbols(project/'megadrive/out/release/symbol.txt');source=read(ROOT/'input/original.sms')
assert source[0x3234e+0x1c3*8]==0x69 and source[0x320ea+(0x69-0x20)*4]==32
previous=ROOT/prior['current_campaign_trace'];pc=load(previous/'capture.json');pa,pw=recording(previous,pc)
specs=[('natural-dungeon-route','md-pal-palc0046-oil-route01','oil-route'),('natural-service-route','md-palc0046-oil-service01','oil'),('natural-dungeon-route','md-pal-palc0046-d3-entry01','entry')]
specs += [('natural-dungeon-combat',('md-auto-' if suffix=='release01' else 'md-pal-')+'palc0046-d3-'+suffix,kind) for suffix,kind in [('rope01','rope'),('switch01','switch'),('key01','key'),('pre-boss01','ready'),('release01','release'),('boss01','boss'),('exit01','exit')]]
stages=[];release=None;fixed=None;fight=None
for family,name,kind in specs:
    folder=project/'validation'/family/name;c=load(folder/'capture.json');r=load(folder/('route_report.json' if family=='natural-dungeon-route' else 'report.json'));a,w=recording(folder,c);f=c['frames']
    assert c['rom_sha256']==r['rom_sha256']==digest and c['sram_input'] is None and c['core_options']['genesis_plus_gx_region_detect']=='pal' and f>pc['frames']
    assert r['failure'] is None and not r.get('deaths',0) and not a['primary_state_imports'] and not a['health_refills'] and not a['boss_assistance']
    assert all(addr==sy['hero_hurt'] and value in (b'\0\0',b'\0\x81') for _,addr,value in w) and w[:len(pw)]==pw
    if kind=='oil':assert r['source_prefix']==previous.name and w==pw and not r['new_assistance_writes'] and r['passed'] and r['first_state']['oil']==0 and r['last_state']['oil']==1 and r['visited']==[0x1f,0xf,0xc7]
    else:
        assert r['prefix_end']==pc['frames']
        assert previous.name in [r.get(k) for k in ('recorded_combat_prefix','recorded_service_prefix','recorded_replay_prefix','recorded_new_game_prefix')]
    proof=folder.with_name(name+f'-assisted-fixed-replay-{f}');pr=load(proof/'replay_report.json')
    assert pr['passed'] and pr['rom_sha256']==digest and pr['whole_ram_bytes']==65536 and pr['final_png_exact'] and not pr['feedback_reads']
    for n,h in pr['evidence'].items():assert sha(read(folder/n))==h
    for stem,ext in [('ram','bin'),('frame','png')]:assert read(folder/f'{stem}_{f:05d}.{ext}')==read(proof/f'{stem}_{f:05d}.{ext}')
    raw=read(folder/f'ram_{f:05d}.bin');data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
    items=data('hero_items',17);save=data('game_save_state',592)
    assert word('game_state')==12 and word('hero_health')>0 and not word('sound_unhandled_command') and items[1]==1
    assert items[8]==(0 if kind=='oil-route' else 1)
    if kind not in ('oil-route','oil','entry'):assert items[13]==1
    if kind=='rope':assert r['item_acquisition_passed'] and r['collect_item_requested']==13 and r['collect_item_target_value']==1 and not r['item_acquisition_state_writes']
    if kind=='switch':assert r['contact_route_passed'] and not r['contact_state_writes']
    if kind=='key':assert r['new_key_verified']
    if kind=='ready':assert r['room_cleared'] and word('room_id')==0x1d3
    if kind=='release':
        release=f;fixed=w;assert word('hero_hurt')==0 and a['closed_before_room']==0x1c3 and w==pw+[(f,sy['hero_hurt'],b'\0\0')]
    if kind in ('boss','exit'):
        assert w==fixed and not r['new_assistance_writes'] and r['unassisted_extension'] and r['guard_release_frame']==release and r['extension_guard_checks_through_frame']==f and word('hero_hurt')<=128
        assert save[0x1f:0x28]==bytes([128]*3+[0]*6) and word('hero_max_health')==56
    if kind=='boss':
        first=r['first_intermediate_combat'];assert first['room']==0x1c3 and first['frame']>release and first['health']>0 and first['hurt']<=128 and first['actors']==[dict(slot=0,kind=0x69,hp=32)]
        assert r['room_cleared'] and r['collect_gem_requested'] and not word('item_reward_active')
        assert r['full_ram_prediction_matches']==r['verified_persistent_prediction_windows']>0 and not r['stack_only_difference_windows']
        fight=dict(first=first,release_frame=release,prediction_windows=r['full_ram_prediction_matches'],first_damage=r['first_extension_damage'])
    if kind=='exit':assert r['full_dungeon_cleared'] and r['dungeon_exit_verified'] and word('room_id')==0x62 and not word('world_dungeon_number')
    stages.append(dict(trace=folder.relative_to(ROOT).as_posix(),frame=f,kind=kind,room=word('room_id'),health=word('hero_health'),max_health=word('hero_max_health'),magic=word('hero_magic'),whole_ram_png_exact=True))
    read(folder/'assistance.json');read(folder/'controls.json');previous,pc,pa,pw=folder,c,a,w
points=[]
for n,count in [('palc0046-d3-cold-stream',3),('palc0046-d3-cold-stream02',7)]:
    s=load(project/'validation'/n/'completed.json');assert s['passed'] and s['rom_sha256']==digest and s['cold_boot_count']==1 and len(s['checkpoints'])==count and all(c['whole_ram_png_exact'] for c in s['checkpoints']);points.extend(s['checkpoints'])
assert [c['frames'] for c in points]==[c['frame'] for c in stages]
out=ROOT/'analysis/palc0046-d3'
r=dict(passed=True,candidate='c0046',region='pal',rom_sha256=digest,stages=stages,current_campaign_trace=stages[-1]['trace'],campaign_frames=stages[-1]['frame'],actual_third_crystal_and_exterior=True,oil_and_rope_owned=True,fight=fight,cold_streams=2,controller_scope_error_recovered=True,full_candidate_campaign_verified=False,archive_manifest=(out/'manifest.json').relative_to(ROOT).as_posix(),scope='Actual PAL cold campaign after D2; oil/stairs and D3 entry verified before controller scope fix, remaining seven milestones independently replayed after recovery. No resource, actor, progression or SRAM import; no boss aid or global SMS fidelity claim.')
freeze(ROOT,out,paths,r,[work])
(ROOT/'analysis/palc0046_d3_report.json').write_text(json.dumps(r,indent=2)+'\n')
print('PAL D3, oil and rope audited and archived across the verified scope-error recovery',flush=True)
