"""Verify the current PAL second guardian, Balloon, ninth crystal and exterior return."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0,'tools')
from archive_lossless_evidence import freeze, sha
from assisted_prefix import recording
from run_core import ROOT as PUBLIC_ROOT
ROOT=PUBLIC_ROOT/'validation/c0046-campaign01/isolated/project'
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated

work=ROOT/'validation/palc0046-d9-funded-finish-sources'
specs=[
    ('auto','approach-resume01',0x1be),('pal','switch1ad-01',0x1ad),
    ('pal','portal19e-ready01',0x19e),('pal','giant-ready02',0x19d),
    ('auto','giant-release01',0x19d),('pal','giant01',0x19c),
    ('auto','post-giant-resume01',0x19c),('pal','balloon01',0x19b),
    ('pal','main-approach01',0x1bc),('auto','main-release01',0x1bc),
    ('pal','boss01',0x1ac),('pal','exit01',0xeb),
]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--through',choices=['giant','balloon','boss','exit'],default='exit')
    through=parser.parse_args().through
    count={'giant':6,'balloon':8,'boss':11,'exit':12}[through]
    digest=sha((ROOT/'gaw-megadrive.bin').read_bytes())
    sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
    sms=(ROOT/'input/original.sms').read_bytes()
    for room,kind,hp in ((0x19c,0x7b,60),(0x1ac,0x6c,90)):
        assert sms[0x3234e+room*8]==kind and sms[0x320ea+(kind-32)*4]==hp
    paths={Path(__file__).resolve(),ROOT/'tools/continue_d9_funded_finish_palc0046.py'}
    def read(path):
        paths.add(path)
        return path.read_bytes()
    def load(path):
        return json.loads(read(path))
    prior=load(PUBLIC_ROOT/'analysis/palc0046_d9_midboss_report.json')
    assert prior['passed'] and prior['first_intermediate_defeated'] and prior['rom_sha256']==digest
    previous=PUBLIC_ROOT/prior['stages'][-1]['trace']
    previous_capture=load(previous/'capture.json')
    _,previous_writes=recording(previous,previous_capture)
    checkpoints=load(ROOT/'validation/palc0046-d9-funded-finish-cold-stream01/checkpoints.json')
    assert checkpoints['cold_boot_count']==1 and checkpoints['rom_sha256']==digest
    assert len(checkpoints['checkpoints'])>=count
    index=load(work/'finish-tools/source_index.json')
    for name,expected in index.items():
        assert sha(read(work/'finish-tools'/Path(name).name))==expected
    stages=[]
    giant=None
    main_boss=None
    guard_release={}
    for (region,trial,room),checkpoint in zip(specs[:count],checkpoints['checkpoints']):
        name='md-'+region+'-palc0046-d9-'+trial
        folder=ROOT/'validation/natural-dungeon-combat'/name
        cap=load(folder/'capture.json')
        report=load(folder/'report.json')
        aid,writes=recording(folder,cap)
        frame=cap['frames']
        assert checkpoint==dict(trace='natural-dungeon-combat/'+name,frames=frame,whole_ram_png_exact=True)
        assert cap['sram_input'] is None and cap['rom_sha256']==report['rom_sha256']==digest
        assert cap['core_options']['genesis_plus_gx_region_detect']=='pal'
        assert report['failure'] is None and not report['deaths']
        assert report['recorded_new_game_prefix']==previous.name
        assert report['prefix_end']==previous_capture['frames']<frame
        assert not aid['primary_state_imports'] and not aid['boss_assistance'] and not aid['health_refills']
        assert writes[:len(previous_writes)]==previous_writes
        assert all(a==sy['hero_hurt'] and v in (b'\0\0',b'\0\x81') for _,a,v in writes)
        proof=folder.with_name(name+f'-assisted-fixed-replay-{frame}')
        result=load(proof/'replay_report.json')
        assert result['passed'] and result['whole_ram_bytes']==65536 and result['final_png_exact']
        assert not result['feedback_reads'] and result['rom_sha256']==digest
        for leaf,digest_check in result['evidence'].items():
            assert sha(read(folder/leaf))==digest_check
        raw=read(folder/f'ram_{frame:05d}.bin')
        assert raw==read(proof/f'ram_{frame:05d}.bin')
        assert read(folder/f'frame_{frame:05d}.png')==read(proof/f'frame_{frame:05d}.png')
        def data(field,n):
            return bytes(raw[(sy[field]+i)^1] for i in range(n))
        def word(field):
            return int.from_bytes(data(field,2),'big')
        assert word('room_id')==room and word('hero_health')>0 and not word('sound_unhandled_command')
        items=data('hero_items',17)
        crystals=data('game_save_state',592)[0x1f:0x28]
        nine=trial in ('boss01','exit01')
        assert crystals==(bytes([128]*9) if nine else bytes([128]*8+[0]))
        assert bool(items[11])==(len(stages)>=7)
        if trial.endswith('resume01'):
            assert report['resumed_after_verified_intermediate']
            assert writes==previous_writes+[(frame,sy['hero_hurt'],b'\x00\x81')]
        if trial in ('giant-release01','main-release01'):
            assert writes==previous_writes+[(frame,sy['hero_hurt'],b'\0\0')]
            assert word('hero_hurt')==0
            guard_release[trial.split('-')[0]]=frame
        if trial in ('giant01','boss01','exit01'):
            assert writes==previous_writes and not report['new_assistance_writes']
            assert report['verified_persistent_prediction_windows']==report['full_ram_prediction_matches']
        if trial=='giant01':
            assert report['room_cleared'] and report['full_ram_prediction_matches']>0
            giant=report['first_intermediate_combat']
            assert giant['frame']>guard_release['giant'] and giant['hurt']==0
            assert giant['actors']==[dict(slot=0,kind=0x7b,hp=60)]
        if trial=='balloon01':
            assert report['item_acquisition_passed'] and report['collect_item_requested']==11
            assert not report['item_acquisition_state_writes']
            assert not report['item_acquisition_first']['owned'] and report['item_acquisition_last']['owned']==1
        if trial=='boss01':
            assert report['room_cleared'] and report['full_ram_prediction_matches']>0
            main_boss=report['first_intermediate_combat']
            assert main_boss['frame']>guard_release['main'] and main_boss['hurt']==0
            assert main_boss['actors']==[dict(slot=0,kind=0x6c,hp=90)]
            assert aid['first_boss_combat']['frame']==main_boss['frame']
            assert aid['first_boss_combat']['hurt']==0
            assert word('hero_health')==104 and word('hero_max_health')==104
        if trial=='exit01':
            assert report['full_dungeon_cleared'] and report['dungeon_exit_verified']
            assert not word('world_dungeon_number')
        if nine:
            mirror=data('sms_vram',16384)
            vram=read(folder/f'vram_{frame:05d}.bin')
            regs=read(folder/f'vdp_regs_{frame:05d}.bin')
            base=(regs[2]&56)<<10
            width=[32,64,32,128][regs[16]&3]
            for n in range(128):
                at=base+((n//32+22)*width+n%32)*2
                assert int.from_bytes(vram[at:at+2],'little')==translated(
                    int.from_bytes(mirror[0x3d00+n*2:0x3d02+n*2],'little'))
            for n in range(9):
                tile,offset=sms[0x1edc+n*2:0x1ede+n*2]
                assert mirror[0x3d00+offset:0x3d02+offset]==bytes([tile,0x59])
        stages.append(dict(trace=folder.relative_to(PUBLIC_ROOT).as_posix(),frames=frame,room=room,
            health=word('hero_health'),magic=word('hero_magic'),gold=word('hero_gold'),
            keys=word('hero_keys'),balloon=bool(items[11]),whole_ram_png_exact=True,
            prediction_windows=report.get('full_ram_prediction_matches')))
        previous,previous_capture,previous_writes=folder,cap,writes

    archive=PUBLIC_ROOT/f'analysis/palc0046-d9-{through}'
    result=dict(passed=True,candidate='c0046',region='pal',rom_sha256=digest,stages=stages,
        giant_defeated=True,first_giant_combat=giant,balloon_acquired=count>=8,
        ninth_crystal_obtained=count>=11,ninth_crystal_and_exterior_return=count==12,actual_ninth_crystal_and_exterior=count==12,
        first_main_combat=main_boss,
        guard_release_frames=guard_release,current_campaign_trace=stages[-1]['trace'],
        campaign_frames=stages[-1]['frames'],archive_manifest=(archive/'manifest.json').relative_to(ROOT).as_posix())
    freeze(PUBLIC_ROOT,archive,paths,result,[ROOT/'validation'])
    output=PUBLIC_ROOT/('analysis/palc0046_d9_report.json' if through=='exit' else f'analysis/palc0046_d9_{through}_report.json')
    assert not output.exists(),output
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    main()
