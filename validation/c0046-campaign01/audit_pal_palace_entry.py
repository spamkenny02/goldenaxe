"""Audit current PAL owned Balloon, nine-crystal gate and first palace giant."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0,'tools')
from archive_lossless_evidence import freeze,sha
from assisted_prefix import recording,EPISODE_KEYS
from run_core import ROOT as PUBLIC_ROOT
ROOT=PUBLIC_ROOT/'validation/c0046-campaign01/isolated/project'
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated

work=ROOT/'validation/palc0046-pal-palace-entry-sources'
combat='natural-dungeon-combat'
route='natural-dungeon-route'
specs=[(combat,'md-auto-palc0046-owned-overview01',0xeb),
       (route,'md-pal-palc0046-cold-palace-entry01',0x18d),
       (combat,'md-pal-palc0046-palace-switch16d01',0x16d),
       (combat,'md-pal-palc0046-palace-pre-giant01',0x16e),
       (combat,'md-auto-palc0046-palace-giant-release01',0x16e),
       (combat,'md-pal-palc0046-palace-giant01',0x15e)]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--through',choices=['entry','mechanisms','giant'],default='giant')
    mode=parser.parse_args().through
    count={'entry':2,'mechanisms':4,'giant':len(specs)}[mode]
    paths={Path(__file__).resolve(),PUBLIC_ROOT/'validation/c0046-campaign01/prepare_pal_palace_entry.py',ROOT/'tools/continue_pal_palace_entry_c0046.py'}
    def read(path):
        paths.add(path)
        return path.read_bytes()
    def load(path):
        return json.loads(read(path))

    digest=sha((ROOT/'gaw-megadrive.bin').read_bytes())
    prior=load(PUBLIC_ROOT/'analysis/palc0046_d9_report.json')
    assert prior['passed'] and prior['ninth_crystal_and_exterior_return'] and prior['rom_sha256']==digest
    checkpoints=load(work/'cold-stream/checkpoints.json')
    assert checkpoints['cold_boot_count']==1 and checkpoints['rom_sha256']==digest
    assert len(checkpoints['checkpoints'])>=count
    index=load(work/'sources/source_index.json')
    for name,expected in index.items():
        assert sha(read(work/'sources'/name))==expected
    sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
    sms_rom=(ROOT/'input/original.sms').read_bytes()
    assert sms_rom[0x3234e+0x15e*8]==0x7b and sms_rom[0x320ea+(0x7b-32)*4]==60
    previous=PUBLIC_ROOT/prior['current_campaign_trace']
    old_cap=load(previous/'capture.json')
    old_aid,old_writes=recording(previous,old_cap)
    stage_rows=[]
    gate=None
    giant=None
    release=None

    for (family,name,room),checkpoint in zip(specs[:count],checkpoints['checkpoints']):
        folder=ROOT/'validation'/family/name
        cap=load(folder/'capture.json')
        report=load(folder/('route_report.json' if family==route else 'report.json'))
        aid,writes=recording(folder,cap)
        frame=cap['frames']
        assert checkpoint==dict(trace=family+'/'+name,frames=frame,whole_ram_png_exact=True)
        assert cap['rom_sha256']==report['rom_sha256']==digest and cap['sram_input'] is None
        assert cap['core_options']['genesis_plus_gx_region_detect']=='pal'
        assert report['failure'] is None and not report.get('deaths',0)
        assert report['prefix_end']==old_cap['frames']<frame
        assert report.get('recorded_new_game_prefix',report.get('recorded_combat_prefix'))==previous.name
        assert writes[:len(old_writes)]==old_writes
        assert not aid['primary_state_imports'] and not aid['health_refills'] and not aid['boss_assistance']
        assert all(a==sy['hero_hurt'] and v in (b'\0\0',b'\0\x81') for _,a,v in writes)
        proof=folder.with_name(name+f'-assisted-fixed-replay-{frame}')
        replay=load(proof/'replay_report.json')
        assert replay['passed'] and replay['rom_sha256']==digest and replay['whole_ram_bytes']==65536
        assert replay['final_png_exact'] and not replay['feedback_reads']
        for leaf,expected in replay['evidence'].items():
            assert sha(read(folder/leaf))==expected
        raw=read(folder/f'ram_{frame:05d}.bin')
        assert raw==read(proof/f'ram_{frame:05d}.bin')
        assert read(folder/f'frame_{frame:05d}.png')==read(proof/f'frame_{frame:05d}.png')

        def data(field,size):
            return bytes(raw[(sy[field]+i)^1] for i in range(size))
        def word(field):
            return int.from_bytes(data(field,2),'big')
        save=data('game_save_state',592)
        assert save[0x1f:0x28]==bytes([128]*9)
        assert data('hero_items',17)[11]==1
        assert word('game_state')==12 and word('room_id')==room
        assert 0<word('hero_health')<=104 and word('hero_max_health')==104
        assert not word('sound_unhandled_command')
        assert word('world_dungeon_number')==(0 if not stage_rows else 10)

        if not stage_rows:
            assert report['actual_owned_balloon'] and report['modal_resources_unchanged']
            assert report['background_5120_map_1280_cells_160_metadata_restored']
            assert not report['new_assistance_writes'] and writes==old_writes
        if family==route:
            assert report['reached_entrance'] and report['directional_probe_succeeded']
            assert report['door_index']==10 and report['palace_gate_verified']
            assert not report['palace_new_map_or_resource_writes']
            gate=report['palace_gate_opened']
            assert gate['cells']==[0x30,0x31,0x1f] and save[0x48]
            assert aid['boss_room']==0x14c and aid['activation_after_frame']==old_cap['frames']
            assert len(aid['episodes'])==len(old_aid['episodes'])+1
            for older,newer in zip(old_aid['episodes'],aid['episodes'][:-1]):
                assert all(older[k]==newer[k] for k in EPISODE_KEYS)
            read(folder/'palace_gate_events.json')
            assert sha(read(folder/'palace_world_driver.py'))==index['natural_palace_world_route.py']
        if name.endswith(('switch16d01','pre-giant01')):
            assert report['contact_route_passed'] and not report['contact_state_writes']
            assert report['contact_room']==report['contact_destination']==room
            assert save[0x50+(room&255)]&4
        if name.endswith('giant-release01'):
            release=frame
            assert word('hero_hurt')==0 and aid['closed_before_room']==0x15e
            assert writes==old_writes+[(frame,sy['hero_hurt'],b'\0\0')]
        if name.endswith('palace-giant01'):
            giant=report['first_intermediate_combat']
            assert giant['frame']>release and giant['hurt']<=128
            assert giant['actors']==[dict(slot=0,kind=0x7b,hp=60)]
            assert report['room_cleared'] and report['guard_release_frame']==release
            assert not report['new_assistance_writes'] and writes==old_writes
            assert report['full_ram_prediction_matches']==report['verified_persistent_prediction_windows']>0
            read(folder/'events.json')

        if family==route or name.endswith('palace-giant01'):
            mirror=data('sms_vram',16384)
            vram=read(folder/f'vram_{frame:05d}.bin')
            regs=read(folder/f'vdp_regs_{frame:05d}.bin')
            base=(regs[2]&56)<<10
            width=[32,64,32,128][regs[16]&3]
            for n in range(128):
                address=base+((n//32+22)*width+n%32)*2
                assert int.from_bytes(vram[address:address+2],'little')==translated(
                    int.from_bytes(mirror[0x3d00+n*2:0x3d02+n*2],'little'))
            for n in range(9):
                tile,offset=sms_rom[0x1edc+n*2:0x1ede+n*2]
                assert mirror[0x3d00+offset:0x3d02+offset]==bytes([tile,0x59])
        stage_rows.append(dict(trace=folder.relative_to(PUBLIC_ROOT).as_posix(),frames=frame,room=room,
            health=word('hero_health'),magic=word('hero_magic'),gold=word('hero_gold'),
            keys=word('hero_keys'),whole_ram_png_exact=True,
            prediction_windows=report.get('full_ram_prediction_matches')))
        previous,old_cap,old_aid,old_writes=folder,cap,aid,writes

    archive=PUBLIC_ROOT/f'analysis/palc0046-pal-palace-{mode}'
    result=dict(passed=True,candidate='c0046',region='pal',rom_sha256=digest,stages=stage_rows,
        palace_entered=True,nine_crystal_gate=gate,balloon_verified=True,
        giant_defeated=giant is not None,first_giant_combat=giant,guard_release_frame=release,
        campaign_frames=stage_rows[-1]['frames'],current_campaign_trace=stage_rows[-1]['trace'],
        physical_hud_words_exact=128,source_crystal_markers_exact=9,
        archive_manifest=(archive/'manifest.json').relative_to(PUBLIC_ROOT).as_posix())
    freeze(PUBLIC_ROOT,archive,paths,result,[ROOT/'validation'])
    (PUBLIC_ROOT/f'analysis/palc0046_palace_{mode}_report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    main()
