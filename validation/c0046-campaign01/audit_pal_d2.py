"""Verify actual PAL D2 keys, unassisted source-strength boss, crystal and return."""
import json,sys
from pathlib import Path
sys.path.insert(0,'tools')
from run_core import ROOT
from assisted_prefix import recording
from archive_lossless_evidence import freeze,sha
from validate_playable_sprite_limit import symbols
work=Path(__file__).resolve().parent;project=work/'isolated/project';paths={Path(__file__).resolve(),work/'prepare_pal_d2.py'}
def read(p):paths.add(p);return p.read_bytes()
def load(p):return json.loads(read(p))
digest=sha((project/'gaw-megadrive.bin').read_bytes());assert digest=='9e747d38e0c6fb2d69b7c1aa8c2b296a61e8b6af41171d14e543ed9a6cb49cf5'
prior=load(ROOT/'analysis/palc0046_after_d1_report.json');assert prior['passed'] and prior['region']=='pal' and prior['second_dungeon_entered'] and prior['rom_sha256']==digest
sy=symbols(project/'megadrive/out/release/symbol.txt');source=read(ROOT/'input/original.sms')
assert source[0x3234e+0x144*8]==0x63 and source[0x320ea+(0x63-0x20)*4]==30
snapshot=project/'validation/palc0046-d2-sources';index=load(snapshot/'source_index.json')
for name,h in index.items():
    assert sha(read(snapshot/Path(name).name))==h and sha(read(project/name))==h
previous=ROOT/prior['stages'][-1]['trace'];pc=load(previous/'capture.json');pa,pw=recording(previous,pc)
stages=[];release=None;fixed=None;fight=None
for suffix in ('key101','key201','key301','pre-boss01','release01','boss01','exit01'):
    name=('md-auto-' if suffix=='release01' else 'md-pal-')+'palc0046-d2-'+suffix
    folder=project/'validation/natural-dungeon-combat'/name;cap=load(folder/'capture.json');r=load(folder/'report.json');a,w=recording(folder,cap);f=cap['frames']
    assert cap['rom_sha256']==r['rom_sha256']==digest and cap['sram_input'] is None and cap['core_options']['genesis_plus_gx_region_detect']=='pal'
    assert r['failure'] is None and not r.get('deaths',0) and not a['primary_state_imports'] and not a['health_refills'] and not a['boss_assistance']
    assert r['prefix_end']==pc['frames'] and r['recorded_new_game_prefix']==previous.name and f>pc['frames']
    assert all(address==sy['hero_hurt'] and value in (b'\0\0',b'\0\x81') for _,address,value in w) and w[:len(pw)]==pw
    proofdir=folder.with_name(name+f'-assisted-fixed-replay-{f}');pr=load(proofdir/'replay_report.json')
    assert pr['passed'] and pr['whole_ram_bytes']==65536 and pr['final_png_exact'] and not pr['feedback_reads'] and pr['rom_sha256']==digest
    for n,h in pr['evidence'].items():assert sha(read(folder/n))==h
    for stem,ext in [('ram','bin'),('frame','png')]:assert read(folder/f'{stem}_{f:05d}.{ext}')==read(proofdir/f'{stem}_{f:05d}.{ext}')
    raw=read(folder/f'ram_{f:05d}.bin');data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
    assert word('game_state')==12 and word('hero_health')>0 and not word('sound_unhandled_command') and data('hero_items',17)[1]==1
    save=data('game_save_state',592)
    if suffix.startswith('key'):assert r['new_key_verified']
    if suffix=='pre-boss01':assert r['room_cleared'] and word('room_id')==0x143
    if suffix=='release01':
        release=f;fixed=w;assert word('hero_hurt')==0 and a['closed_before_room']==0x144 and w==pw+[(f,sy['hero_hurt'],b'\0\0')]
    if suffix in ('boss01','exit01'):
        assert w==fixed and not r['new_assistance_writes'] and r['unassisted_extension'] and r['guard_release_frame']==release and r['extension_guard_checks_through_frame']==f and word('hero_hurt')<=128
        assert save[0x1f:0x28]==bytes([128,128]+[0]*7) and word('hero_max_health')==48
    if suffix=='boss01':
        first=r['first_intermediate_combat'];assert first['room']==0x144 and first['frame']>release and first['health']>0 and first['hurt']<=128 and first['actors']==[dict(slot=0,kind=0x63,hp=30)]
        assert r['room_cleared'] and r['collect_gem_requested'] and word('hero_health')==48 and not word('item_reward_active')
        assert r['full_ram_prediction_matches']==r['verified_persistent_prediction_windows']>0 and not r['stack_only_difference_windows']
        fight=dict(first=first,release_frame=release,prediction_windows=r['full_ram_prediction_matches'],first_damage=r['first_extension_damage'])
    if suffix=='exit01':assert r['full_dungeon_cleared'] and r['dungeon_exit_verified'] and word('room_id')==0xd6 and not word('world_dungeon_number')
    stages.append(dict(trace=folder.relative_to(ROOT).as_posix(),frame=f,room=word('room_id'),health=word('hero_health'),max_health=word('hero_max_health'),keys=word('hero_keys'),whole_ram_png_exact=True))
    read(folder/'controls.json');read(folder/'assistance.json');previous,pc,pa,pw=folder,cap,a,w
stream=load(project/'validation/palc0046-d2-cold-stream/completed.json')
assert stream['passed'] and stream['rom_sha256']==digest and stream['cold_boot_count']==1 and len(stream['checkpoints'])==7 and all(c['whole_ram_png_exact'] for c in stream['checkpoints'])
assert [c['frames'] for c in stream['checkpoints']]==[c['frame'] for c in stages]
out=ROOT/'analysis/palc0046-d2'
r=dict(passed=True,candidate='c0046',region='pal',rom_sha256=digest,stages=stages,actual_second_crystal_and_exterior=True,
       current_campaign_trace=stages[-1]['trace'],campaign_frames=stages[-1]['frame'],fight=fight,full_candidate_campaign_verified=False,
       archive_manifest=(out/'manifest.json').relative_to(ROOT).as_posix(),scope='Cold PAL candidate continuation; actual keys/crystal and source-strength boss, approach-only hurt writes removed before combat. No resource, actor, progression or SRAM import; no global SMS fidelity claim.')
freeze(ROOT,out,paths,r,[work])
(ROOT/'analysis/palc0046_d2_report.json').write_text(json.dumps(r,indent=2)+'\n')
print('PAL candidate D2 audited and archived',flush=True)
