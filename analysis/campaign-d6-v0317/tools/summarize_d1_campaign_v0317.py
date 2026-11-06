"""Audit the newly played v317 first dungeon, not a historical replay claim."""
import json
from pathlib import Path
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols


def main():
    refs={}
    def read(p):
        raw=evidence(p);refs[p.relative_to(ROOT).as_posix()]=sha(raw);return raw
    def load(p):return json.loads(read(p))
    target=ROOT/'analysis/d1_campaign_v0317_report.json';assert not target.exists()
    digest=sha(read(ROOT/'gaw-megadrive.bin'))
    assert digest=='7694654ec85dd6626c0e17ff1834e5893d4eb35481400a4725eac6b6f3503294'
    symbol_file=ROOT/'megadrive/out/release/symbol.txt';read(symbol_file);sy=symbols(symbol_file)
    source=read(ROOT/'input/original.sms')
    stages=[];prior_end=0;prior_writes=[];final_raw=None
    release=None;first=None;boss_report=None
    for suffix,room in [('entry01',0x1e4),('key01',0x1e5),('ready01',0x185),
                        ('second-key01',0x193),('ready02',0x185),('release01',0x185),
                        ('boss01',0x175),('exit01',0xb9)]:
        entry=suffix=='entry01'
        name=('md-' if entry else 'md-auto-')+'v0317-d1-'+suffix
        folder=ROOT/'validation'/('natural-dungeon-route' if entry else 'natural-dungeon-combat')/name
        c=load(folder/'capture.json');r=load(folder/('route_report.json' if entry else 'report.json'))
        end=c['frames'];assert end>prior_end and c['rom_sha256']==digest and c['sram_input'] is None
        assert r['failure'] is None and not r.get('deaths',r.get('normal_continues',0))
        proof=folder.with_name(name+('-fixed-replay' if entry else f'-assisted-fixed-replay-{end}'))
        q=load(proof/'replay_report.json')
        assert q['passed'] and q['rom_sha256']==digest and q['whole_ram_bytes']==65536
        assert q['final_png_exact'] and not q['feedback_reads']
        for n,h in q['evidence'].items():assert sha(read(folder/n))==h
        for stem,ext in [('ram','bin'),('frame','png')]:
            filename=f'{stem}_{end:05d}.{ext}'
            assert read(folder/filename)==read(proof/filename)
        raw=read(folder/f'ram_{end:05d}.bin');final_raw=raw
        data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k))
        word=lambda n:int.from_bytes(data(n,2),'big')
        assert word('room_id')==room and word('game_state')==12 and word('hero_health')>0
        assert not word('sound_unhandled_command') and data('hero_items',17)==bytes(17)
        if entry:
            assert not c['test_ram_writes'] and r['reached_entrance'] and r['directional_probe_succeeded']
            writes=[]
        else:
            assist,writes=recording(folder,c);read(folder/'assistance.json')
            assert not assist['boss_assistance'] and not assist['primary_state_imports'] and not assist['health_refills']
            assert len(assist['episodes'])==1 and assist['boss_room']==0x175
            assert writes[:len(prior_writes)]==prior_writes
            assert all(addr==sy['hero_hurt'] for _,addr,_ in writes)
            if suffix in ('key01','second-key01'):assert r['new_key_verified'] and word('hero_keys')==1
            if suffix=='release01':
                release=end;assert word('hero_hurt')==0 and assist['closed_before_room']==0x175
                assert writes[-1]==(release,sy['hero_hurt'],b'\0\0')
            if suffix in ('boss01','exit01'):
                assert writes==prior_writes and writes[-1][0]==release
                assert r['unassisted_extension'] and not r['new_assistance_writes'] and not r['primary_state_imports']
                assert data('game_save_state',592)[0x1f:0x28]==bytes([128]+[0]*8)
                assert r['extension_guard_checks_through_frame']==end
            if suffix=='boss01':
                boss_report=r;first=r['first_intermediate_combat']
                assert r['room_cleared'] and first['hurt']==0 and release<first['frame']
                kind=source[0x3234e+0x175*8]
                assert kind==0x68 and first['actors']==[dict(slot=0,kind=kind,hp=source[0x320ea+(kind-0x20)*4])]
                assert r['full_ram_prediction_matches']==r['verified_persistent_prediction_windows']==33
                assert not r['stack_only_difference_windows']
            if suffix=='exit01':
                assert r['full_dungeon_cleared'] and r['dungeon_exit_verified']
                assert word('world_dungeon_number')==0 and word('hero_max_health')==32
                assert not word('item_reward_active') and word('hero_health')==28
        stages.append(dict(trace=folder.relative_to(ROOT).as_posix(),frames=end,room=room,
                           health=word('hero_health'),whole_ram_and_final_png_replayed_exactly=True))
        prior_end=end;prior_writes=writes
    result=dict(passed=True,version=317,md_sha256=digest,fresh_new_game_first_crystal_and_exit=True,
        campaign_frames=prior_end,stages=stages,guard_release_frame=release,first_boss_combat=first,
        boss_prediction_windows=boss_report['full_ram_prediction_matches'],deaths=0,
        initial_sram=False,primary_state_imports=0,resource_writes=0,boss_assistance=False,
        approach_only_hurt_writes=len(prior_writes),full_game_validated=False,
        current_campaign_trace=stages[-1]['trace'],evidence=refs,
        driver_sha256=sha(Path(__file__).read_bytes()),
        limits=['New controller recording on this receiving binary. Logged approach-only hurt guards end before the boss; no resource or state imports.',
                'Eight cold full-RAM/final-PNG reproductions and source boss birth data verify this checkpoint. They do not prove whole-source visual/audio fidelity, PAL campaign, optional content or later dungeons.'])
    target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('V317 fresh first crystal and exterior exit verified:',prior_end,'frames; boss unassisted')


if __name__=='__main__':main()
