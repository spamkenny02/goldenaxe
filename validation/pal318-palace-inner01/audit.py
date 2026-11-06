"""Verify the V318 PAL palace from the first giant through the ending."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0,'tools')
from archive_lossless_evidence import freeze,sha
from assisted_prefix import recording
from run_core import ROOT
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated

work=Path(__file__).resolve().parent
family='natural-dungeon-combat'
steps=[
    ('auto','resume-giant01',0x15e),('pal','portal14e01',0x14e),
    ('pal','earth14e01',0x119),('pal','earth11a01',0x12a),
    ('pal','switch12901',0x12a),('pal','switch12c01',0x12c),
    ('pal','pre-guardian01',0x12e),('auto','guardian-release01',0x12e),
    ('pal','guardian01',0x11e),('auto','resume-final01',0x11e),
    ('pal','goldenaxe01',0x11d),('pal','earth13e01',0x16a),
    ('pal','switch17c01',0x17c),('pal','portal13c01',0x13c),
    ('pal','switch14b01',0x14b),('pal','portal15a01',0x15a),
    ('pal','earth15b01',0x16b),('pal','switch16c01',0x16c),
    ('pal','pre-final01',0x15c),('auto','release-final01',0x15c),
    ('pal','final01',0x14c),('auto','ending01',0x14c),
]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--through',choices=['portal','earth','inner','pre-guardian','guardian','golden-axe','pre-final','ending'],default='ending')
    mode=parser.parse_args().through
    count={'portal':2,'earth':3,'inner':5,'pre-guardian':7,'guardian':9,'golden-axe':11,'pre-final':19,'ending':22}[mode]
    paths={work/'run.py',work/'audit.py'}
    def read(path):
        paths.add(path)
        return path.read_bytes()
    def load(path):
        return json.loads(read(path))

    rom=ROOT/'gaw-megadrive.bin'
    digest=sha(rom.read_bytes())
    assert digest=='b9e1f0a0543f191e24ffd6d2740a0d717501e0fcd986f8b8953a37a1b3c416a4'
    sy=symbols(ROOT/'versions/v0318-b9e1f0a0/symbol.txt')
    source=(ROOT/'input/original.sms').read_bytes()
    rooms=((0x11e,0x7c),(0x14c,0x6d))
    hp={kind:source[0x320ea+(kind-32)*4] for _,kind in rooms}
    assert all(source[0x3234e+room*8]==kind for room,kind in rooms)
    assert hp[0x6d]==90

    stages=[]
    checkpoints=load(work/'cold-stream/checkpoints.json')
    assert checkpoints['cold_boot_count']==1 and checkpoints['rom_sha256']==digest
    assert len(checkpoints['checkpoints'])>=count
    index=load(work/'sources/source_index.json')
    for name,expected in index.items():
        assert sha(read(work/'sources'/Path(name).name))==expected
    prior=load(ROOT/'analysis/pal_palace_giant_v0318_report.json')
    assert prior['passed'] and prior['giant_defeated'] and prior['md_sha256']==digest
    previous=ROOT/prior['current_campaign_trace']
    old_cap=load(previous/'capture.json')
    _,old_writes=recording(previous,old_cap)
    releases={}
    fights={}
    ending=None

    def reader(raw):
        def data(field,n):
            return bytes(raw[(sy[field]+i)^1] for i in range(n))
        return data,lambda field:int.from_bytes(data(field,2),'big')

    for (tag,trial,room),checkpoint in zip(steps[:count],checkpoints['checkpoints']):
        name='md-'+tag+'-pal318-palace-'+trial
        folder=ROOT/'validation'/family/name
        cap=load(folder/'capture.json')
        r=load(folder/'report.json')
        aid,writes=recording(folder,cap)
        frame=cap['frames']
        assert checkpoint==dict(trace=family+'/'+name,frames=frame,whole_ram_png_exact=True)
        assert cap['rom_sha256']==r['rom_sha256']==digest and not cap['sram_input']
        assert cap['core_options']['genesis_plus_gx_region_detect']=='pal'
        assert r['failure'] is None and not r.get('deaths',0)
        if trial=='ending01':
            assert r['recorded_victory_prefix']==family+'/'+previous.name
        else:
            assert r['recorded_new_game_prefix']==previous.name and r['prefix_end']==old_cap['frames']
        assert frame>old_cap['frames']
        assert not aid['boss_assistance'] and not aid['health_refills'] and not aid['primary_state_imports']
        assert writes[:len(old_writes)]==old_writes
        assert all(a==sy['hero_hurt'] and v in (b'\0\0',b'\0\x81') for _,a,v in writes)
        proof=folder.with_name(name+f'-assisted-fixed-replay-{frame}')
        verified=load(proof/'replay_report.json')
        assert verified['passed'] and verified['rom_sha256']==digest and verified['whole_ram_bytes']==65536
        assert verified['final_png_exact'] and not verified['feedback_reads']
        for leaf,expected in verified['evidence'].items():
            assert sha(read(folder/leaf))==expected
        raw=read(folder/f'ram_{frame:05d}.bin')
        assert raw==read(proof/f'ram_{frame:05d}.bin')
        assert read(folder/f'frame_{frame:05d}.png')==read(proof/f'frame_{frame:05d}.png')
        data,word=reader(raw)
        game=word('game_state')
        save=data('game_save_state',592)
        assert word('room_id')==room and word('hero_health')>0 and not word('sound_unhandled_command')
        assert save[0x1f:0x28]==bytes([128]*9)
        assert word('world_dungeon_number')==10 and word('hero_max_health')==104
        assert data('hero_items',17)[1]==(1 if len(stages)<10 else 2)
        assert game==(0 if trial=='ending01' else 14 if trial=='final01' else 12)
        if trial.startswith('earth'):
            assert r['earth_route_passed'] and not r['earth_state_writes']
        if trial.startswith('switch'):
            assert r['contact_route_passed'] and not r['contact_state_writes']
        if trial.startswith('resume'):
            assert r['resumed_after_verified_intermediate']
            assert writes==old_writes+[(frame,sy['hero_hurt'],b'\0\x81')]
        if 'release' in trial:
            which='guardian' if trial.startswith('guardian') else 'final'
            releases[which]=frame
            assert word('hero_hurt')==0 and writes==old_writes+[(frame,sy['hero_hurt'],b'\0\0')]
        if trial in ('guardian01','final01'):
            which=trial.removesuffix('01')
            kind=0x7c if which=='guardian' else 0x6d
            first=r['first_intermediate_combat']
            assert first['frame']>releases[which] and first['room']==room and first['hurt']<=128
            assert any(a['kind']==kind and a['hp']==hp[kind] for a in first['actors'])
            assert writes==old_writes and not r['new_assistance_writes'] and r['unassisted_extension']
            assert r['full_ram_prediction_matches']==r['verified_persistent_prediction_windows']>0
            fights[which]=dict(first=first,prediction_windows=r['full_ram_prediction_matches'])
            read(folder/'events.json')
            if which=='final':
                assert r['ending_handoff_passed'] and r['ending_handoff']['final_dungeon_defeated']
                assert save[0x28]==1
        if trial=='goldenaxe01':
            assert r['item_acquisition_passed'] and not r['item_acquisition_state_writes']
            assert r['collect_item_requested']==1 and r['collect_item_target_value']==2
            assert r['item_acquisition_last']['owned']==2
        if trial=='pre-final01':
            mirror=data('sms_vram',16384)
            vram=read(folder/f'vram_{frame:05d}.bin')
            regs=read(folder/f'vdp_regs_{frame:05d}.bin')
            base=(regs[2]&56)<<10
            width=[32,64,32,128][regs[16]&3]
            for n in range(128):
                address=base+((n//32+22)*width+n%32)*2
                assert int.from_bytes(vram[address:address+2],'little')==translated(
                    int.from_bytes(mirror[0x3d00+n*2:0x3d02+n*2],'little'))
        if trial=='ending01':
            assert r['ending_complete'] and r['last_state']['credits_done']
            assert not r['new_assistance_writes'] and writes==old_writes
            assert r['nine_gems_visible_frame']<r['credits_started_frame']<r['credits_finished_frame']
            assert r['credits_finished_frame']<r['acknowledgement_frame']<=r['title_flow_return_frame']
            gem_frame=r['nine_gems_visible_frame']+1
            gem_data,gem_word=reader(read(folder/f'ram_{gem_frame:05d}.bin'))
            actors=gem_data('world_actor_state',768)
            assert gem_word('ending_hero_descriptor')==0x8495
            assert all(actors[i*48]==6 and actors[i*48+3]&1 for i in range(9))
            read(folder/f'frame_{gem_frame:05d}.png')
            ending={key:r[key] for key in ('nine_gems_visible_frame','credits_started_frame',
                'credits_finished_frame','title_flow_return_frame','music_requests')}
        stages.append(dict(trace=folder.relative_to(ROOT).as_posix(),frames=frame,room=room,
            game=game,health=word('hero_health'),magic=word('hero_magic'),whole_ram_png_exact=True))
        previous,old_cap,old_writes=folder,cap,writes

    archive=ROOT/f'analysis/pal-palace-{mode}-v0318'
    result=dict(passed=True,version=318,region='pal',md_sha256=digest,stages=stages,
        fights=fights,guard_release_frames=releases,actual_golden_axe_acquired=count>=11,
        ending_complete=ending is not None,ending=ending,campaign_frames=stages[-1]['frames'],
        current_campaign_trace=stages[-1]['trace'],archive_manifest=(archive/'manifest.json').relative_to(ROOT).as_posix())
    reused={}
    earlier={'portal':[], 'earth':['portal'], 'inner':['portal','earth'],
        'pre-guardian':['portal','earth','inner'],
        'guardian':['portal','earth','inner','pre-guardian'], 'golden-axe':['portal','earth','inner','pre-guardian','guardian'],
        'pre-final':['portal','earth','inner','pre-guardian','guardian','golden-axe'],
        'ending':['portal','earth','inner','pre-guardian','guardian','golden-axe','pre-final']}[mode]
    for previous_mode in earlier:
        manifest_path=ROOT/f'analysis/pal-palace-{previous_mode}-v0318/manifest.json'
        if not manifest_path.is_file():
            continue
        manifest=json.loads(manifest_path.read_bytes())
        assert manifest['passed'] and manifest['rom_sha256']==digest
        for path in tuple(paths):
            relative=path.relative_to(ROOT).as_posix()
            item=manifest['compressed'].get(relative)
            if item and sha(path.read_bytes())==item['raw_sha256']:
                assert sha((manifest_path.parent/item['stored']).read_bytes())==item['stored_sha256']
                paths.remove(path)
                reused[relative]=dict(raw_sha256=item['raw_sha256'],
                    manifest=manifest_path.relative_to(ROOT).as_posix())
    freeze(ROOT,archive,paths,dict(passed=True,rom_sha256=digest,region='pal',
        reused_references=reused),[work])
    (ROOT/f'analysis/pal_palace_{mode.replace("-","_")}_v0318_report.json').write_text(
        json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    main()
