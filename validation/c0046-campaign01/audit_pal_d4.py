"""Audit actual PAL D4 Earth passages, canoe, unassisted burst boss and fourth crystal."""
import json,sys
from pathlib import Path
sys.path.insert(0,'tools')
from run_core import ROOT
from assisted_prefix import recording
from archive_lossless_evidence import freeze,sha
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated
work=Path(__file__).resolve().parent;project=work/'isolated/project';paths={Path(__file__).resolve(),work/'prepare_pal_d4.py'}
def read(p):paths.add(p);return p.read_bytes()
def load(p):return json.loads(read(p))
digest=sha((project/'gaw-megadrive.bin').read_bytes());assert digest=='9e747d38e0c6fb2d69b7c1aa8c2b296a61e8b6af41171d14e543ed9a6cb49cf5'
prior=load(ROOT/'analysis/palc0046_earth_report.json');assert prior['passed'] and prior['region']=='pal' and prior['rom_sha256']==digest and prior['fourth_dungeon_entered']
snapshot=project/'validation/palc0046-d4-sources'
for n,h in load(snapshot/'source_index.json').items():assert sha(read(snapshot/Path(n).name))==h and sha(read(project/n))==h
sy=symbols(project/'megadrive/out/release/symbol.txt');source=read(ROOT/'input/original.sms')
assert source[0x3234e+0x180*8]==0x6a and source[0x320ea+(0x6a-0x20)*4]==30
previous=ROOT/prior['current_campaign_trace'];pc=load(previous/'capture.json');pa,pw=recording(previous,pc)
suffixes=('key01','earth01','a1-key01','canoe01','warp01','boss-key01','pre-boss01','release01','boss01','exit01')
stages=[];release=None;fixed=None;fight=None
for suffix in suffixes:
    name=('md-auto-' if suffix=='release01' else 'md-pal-')+'palc0046-d4-'+suffix;folder=project/'validation/natural-dungeon-combat'/name
    c=load(folder/'capture.json');r=load(folder/'report.json');a,w=recording(folder,c);f=c['frames']
    assert c['rom_sha256']==r['rom_sha256']==digest and c['sram_input'] is None and c['core_options']['genesis_plus_gx_region_detect']=='pal'
    assert r['failure'] is None and not r['deaths'] and f>pc['frames'] and r['prefix_end']==pc['frames'] and r['recorded_new_game_prefix']==previous.name
    assert not a['primary_state_imports'] and not a['health_refills'] and not a['boss_assistance'] and a['boss_room']==0x180
    assert all(addr==sy['hero_hurt'] and value in (b'\0\0',b'\0\x81') for _,addr,value in w) and w[:len(pw)]==pw
    proof=folder.with_name(name+f'-assisted-fixed-replay-{f}');pr=load(proof/'replay_report.json')
    assert pr['passed'] and pr['rom_sha256']==digest and pr['whole_ram_bytes']==65536 and pr['final_png_exact'] and not pr['feedback_reads']
    for n,h in pr['evidence'].items():assert sha(read(folder/n))==h
    for stem,ext in [('ram','bin'),('frame','png')]:assert read(folder/f'{stem}_{f:05d}.{ext}')==read(proof/f'{stem}_{f:05d}.{ext}')
    raw=read(folder/f'ram_{f:05d}.bin');data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
    items=data('hero_items',17);save=data('game_save_state',592)
    assert word('game_state')==12 and word('hero_health')>0 and not word('sound_unhandled_command') and items[1]==items[5]==items[8]==items[13]==1
    if suffix in ('key01','a1-key01','boss-key01'):assert r['new_key_verified']
    if suffix in ('earth01','warp01'):
        room,cell,dest=(0x1e1,0x58,0x1d1) if suffix=='earth01' else (0x1a3,0x5c,0x192)
        assert r['earth_route_passed'] and r['earth_passage_traversed'] and r['earth_passage_opened'] and not r['earth_state_writes'] and r['earth_passage_room']==room and r['earth_cell']==cell and word('room_id')==dest
    if suffix=='canoe01':assert r['item_acquisition_passed'] and r['collect_item_requested']==12 and r['collect_item_target_value']==1 and not r['item_acquisition_state_writes'] and items[12]==1
    if suffix in suffixes[3:]:assert items[12]==1
    if suffix=='pre-boss01':assert r['target_room_reached'] and word('room_id')==0x190
    if suffix=='release01':
        release=f;fixed=w;assert word('hero_hurt')==0 and a['closed_before_room']==0x180 and w==pw+[(f,sy['hero_hurt'],b'\0\0')]
    if suffix in ('boss01','exit01'):
        assert w==fixed and not r['new_assistance_writes'] and r['unassisted_extension'] and r['guard_release_frame']==release and r['extension_guard_checks_through_frame']==f and word('hero_hurt')<=128
        assert save[0x1f:0x28]==bytes([128]*4+[0]*5) and word('hero_max_health')==64
    if suffix=='boss01':
        first=r['first_intermediate_combat'];assert first['room']==0x180 and first['frame']>release and first['health']>0 and first['hurt']<=128 and any(e['kind']==0x6a and e['hp']==30 for e in first['actors'])
        assert r['room_cleared'] and r['collect_gem_requested'] and not word('item_reward_active')
        assert r['full_ram_prediction_matches']==r['verified_persistent_prediction_windows']>0 and not r['stack_only_difference_windows']
        fight=dict(first=first,release_frame=release,prediction_windows=r['full_ram_prediction_matches'],first_damage=r['first_extension_damage'])
    if suffix=='exit01':assert r['full_dungeon_cleared'] and r['dungeon_exit_verified'] and word('room_id')==0x10 and not word('world_dungeon_number') and 0x1b0 in r['deferred_puzzles']
    stages.append(dict(trace=folder.relative_to(ROOT).as_posix(),frame=f,stage=suffix,room=word('room_id'),health=word('hero_health'),max_health=word('hero_max_health'),magic=word('hero_magic'),whole_ram_png_exact=True))
    read(folder/'assistance.json');read(folder/'controls.json');previous,pc,pa,pw=folder,c,a,w
sms=data('sms_vram',16384);vram=read(previous/f'vram_{f:05d}.bin');regs=read(previous/f'vdp_regs_{f:05d}.bin');base=(regs[2]&56)<<10;width=[32,64,32,128][regs[16]&3]
for n in range(128):
    at=base+((n//32+22)*width+n%32)*2;assert int.from_bytes(vram[at:at+2],'little')==translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2],'little'))
s=load(project/'validation/palc0046-d4-cold-stream01/completed.json');assert s['passed'] and s['rom_sha256']==digest and s['cold_boot_count']==1 and len(s['checkpoints'])==10 and all(c['whole_ram_png_exact'] for c in s['checkpoints'])
assert [c['frames'] for c in s['checkpoints']]==[c['frame'] for c in stages]
out=ROOT/'analysis/palc0046-d4'
r=dict(passed=True,candidate='c0046',region='pal',rom_sha256=digest,stages=stages,current_campaign_trace=stages[-1]['trace'],campaign_frames=stages[-1]['frame'],actual_fourth_crystal_and_exterior=True,canoe_owned=True,fight=fight,physical_hud_words_exact=128,full_candidate_campaign_verified=False,archive_manifest=(out/'manifest.json').relative_to(ROOT).as_posix(),scope='Actual PAL D4 keys, two Earth passages, canoe, source-strength burst boss and return with1B0 optional puzzle deferred. Ten independent cold RAM/PNG checkpoints; no resource, actor, progression or SRAM import, no boss/return aid; global SMS timing remains unproved.')
freeze(ROOT,out,paths,r,[work]);(ROOT/'analysis/palc0046_d4_report.json').write_text(json.dumps(r,indent=2)+'\n')
print('PAL fourth crystal, canoe and return audited and archived',flush=True)
