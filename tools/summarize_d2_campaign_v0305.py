"""Audit acquired axe, first fairy and second-dungeon campaign on v305."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols


STAGES=[
    ('natural-dungeon-route','md-v0305-d1-return-axe01','route'),
    ('natural-dungeon-combat','md-auto-v0305-d1-axe-key01','key'),
    ('natural-dungeon-combat','md-auto-v0305-d1-axe01','axe'),
    ('natural-dungeon-combat','md-auto-v0305-d1-axe-exit01','exit1'),
    ('natural-dungeon-route','md-v0305-fairy-route01','route'),
    ('natural-service-route','md-v0305-fairy-service01','fairy'),
    ('natural-dungeon-route','md-v0305-d2-entry01','route'),
    ('natural-dungeon-combat','md-auto-v0305-d2-key01','key'),
    ('natural-dungeon-combat','md-auto-v0305-d2-key02e','reentry-key'),
    ('natural-dungeon-combat','md-auto-v0305-d2-key03','key'),
    ('natural-dungeon-combat','md-auto-v0305-d2-boss01','boss'),
    ('natural-dungeon-combat','md-auto-v0305-d2-exit01','exit2')]


def main():
    refs={}
    def read(name):
        raw=evidence(ROOT/name);refs[name]=sha(raw);return raw
    def load(name):return json.loads(read(name))
    digest=sha((ROOT/'gaw-megadrive.bin').read_bytes())
    prior=load('analysis/d1_oil_v0305_report.json')
    assert prior['passed'] and prior['md_sha256']==digest and prior['first_crystal_and_exterior_return']
    production=load('validation/v0305-indoor-sources/after.json')
    assert production['rom_sha256']==digest
    assert all(sha((ROOT/n).read_bytes())==h for n,h in production['production_sources'].items())
    for n in ['gaw-title-megadrive.bin','versions/v0305-83dfaf69/gaw-megadrive-v0305.bin']:
        assert sha((ROOT/n).read_bytes())==digest
    sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
    stages=[];latest=[];boss_assistance=None
    for index,(family,name,kind) in enumerate(STAGES):
        root=f'validation/{family}/{name}';c=load(root+'/capture.json')
        r=load(root+('/route_report.json' if kind=='route' else '/report.json'));f=c['frames']
        assert c['rom_sha256']==r['rom_sha256']==digest and c['sram_input'] is None
        assert r['failure'] is None and not r['sram_checkpoint_injection']
        if 'driver_sha256' in r:
            expected=read('validation/v0305-d2-door-probe-sources/natural_dungeon_combat_before.py') if index<8 else read('tools/natural_dungeon_combat.py')
            assert r['driver_sha256']==sha(expected)
        if kind=='route':assert r['reached_entrance'] and r['directional_probe_succeeded'] and not r['normal_continues']
        elif kind=='fairy':assert r['passed'] and not r['new_assistance_writes']
        else:assert r['room_cleared'] and not r['deaths']
        a,writes=recording(ROOT/root,c);read(root+'/assistance.json')
        assert a['boss_room']==0x144 and len(a['episodes'])==2
        assert a['episodes'][0]['release_write_frame']==14835
        assert a['episodes'][0]['first_boss_combat']==dict(frame=14907,health=24,hurt=0)
        assert a['activation_after_frame']==17482
        assert not a['health_refills'] and not a['primary_state_imports'] and not a['boss_assistance']
        assert all(addr==sy['hero_hurt'] for _,addr,_ in writes)
        assert writes[:len(latest)]==latest
        if kind=='exit2':
            assert writes==latest and a['unassisted_extension'] and not a['new_assistance_writes']
        latest=writes
        if kind in ('boss','exit2'):
            first=a['first_boss_combat'];assert first['health']==40 and first['hurt']==0
            assert writes[-1][0]==a['release_write_frame']<first['frame'] and writes[-1][2]==b'\0\0'
            boss_assistance=dict(release=a['release_write_frame'],first_combat=first,first_damage=a['first_boss_damage'])
        else:assert a['first_boss_entry'] is None and a['first_boss_combat'] is None
        proof=root+f'-assisted-fixed-replay-{f}';p=load(proof+'/replay_report.json')
        assert p['passed'] and p['rom_sha256']==digest and p['whole_ram_bytes']==65536
        assert p['final_png_exact'] and not p['feedback_reads']
        for n,h in p['evidence'].items():assert sha(read(root+'/'+n))==h
        raw=read(root+f'/ram_{f:05d}.bin')
        for stem,ext in [('ram','bin'),('frame','png')]:
            n=f'/{stem}_{f:05d}.{ext}';assert read(root+n)==read(proof+n)
        data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k))
        word=lambda n:int.from_bytes(data(n,2),'big')
        save=data('game_save_state',592);items=data('hero_items',17)
        assert items[8]==1 and save[0x117]&2 and save[0x1f]==128
        assert not word('sound_unhandled_command')
        if index>=2:assert word('hero_weapon_level')==1
        if index>=3:assert word('hero_selected_item')==1
        if index>=5:assert save[0x119]&2 and word('hero_max_health')>=40
        if kind in ('key','reentry-key'):assert r['new_key_verified']
        if kind=='reentry-key':
            assert r['retry_isolated_foes_requested'] and r['isolated_foe_retries']==2 and not r['rush_rooms']
            decisions=load(root+'/pilot_decisions.json')
            assert sum(x['reason']=='isolated_foe_reentry_complete' for x in decisions)==2
            assert r['driver_sha256']==sha(read('tools/natural_dungeon_combat.py'))
        if kind=='fairy':
            assert r['initial_state']['max_health']==32 and r['last_state']['max_health']==40
            assert word('hero_health')==40 and word('room_id')==0xc9
        if kind in ('exit1','exit2'):assert r['full_dungeon_cleared'] and not word('world_dungeon_number')
        if kind in ('boss','exit2'):
            assert save[0x20]==128 and word('hero_max_health')==48
            plan=load(root+'/planning_partial.json')
            assert plan['verified_windows']==plan['full_ram_matches'] and not plan['stack_only_difference_windows']
            assert not plan['primary_state_imports']
        stages.append(dict(trace=root,kind=kind,frames=f,room=word('room_id'),health=word('hero_health'),
                           max_health=word('hero_max_health'),keys=word('hero_keys'),oil_owned=True,
                           axe_owned=bool(word('hero_weapon_level')),crystals=sum(x==128 for x in save[0x1f:0x28]),whole_ram_png_exact=True))
    assert stages[-1]['room']==0xd6 and stages[-1]['crystals']==2
    stack='validation/stack-v0305-d2-all';s=load(stack+'/stack_report.json')
    assert s['md_sha256']==digest and s['frames']==stages[-1]['frames'] and s['read_only'] and s['all_instructions']
    assert s['logged_assistance_replayed'] and not s['invalid_heap_examples']
    assert s['minimum_instruction_sp']==min(x['sp'] for x in s['instruction_minima'])
    assert s['minimum_sp']==min(s['minimum_instruction_sp'],s['minimum_sampled_sp'])
    margin=s['minimum_sp']-max(x['end']+2 for x in s['heap_changes']);assert margin>0
    for stem,ext in [('ram','bin'),('frame','png')]:
        n=f'/{stem}_{s["frames"]:05d}.{ext}';assert read(stack+n)==read(stages[-1]['trace']+n)
    for name in ['key02','key02b','key02c','key02d']:
        root=f'validation/natural-dungeon-combat/md-auto-v0305-d2-{name}'
        r=load(root+'/report.json');assert r['failure']=='frame_limit' and not r['room_cleared']
        assert r['driver_sha256']==sha(read(root+'/combat_driver.py'))
    read('tools/summarize_d2_campaign_v0305.py')
    result=dict(passed=True,version=305,md_sha256=digest,production_rom_unchanged=True,
                second_crystal_and_exterior_return=True,stages=stages,boss_assistance=boss_assistance,
                instruction_stack_margin_bytes=margin,stack_frames=s['frames'],full_game_validated=False,evidence=refs,
                limits=['Twelve current-ROM stages cold-replayed with whole65536RAM and finalPNG exact. Approach protection writes only hero_hurt;no HP,actor,ownership,progression or SRAM fixtures.',
                        'D2 guard ends before the main boss and never resumes on the return. D1 assistance remains inherited and declared. This is not an entirely unassisted campaign.',
                        'Four failed controller attempts remain excluded. A side-door probe experiment was rejected. Optional bounded room reentry waits for actual attack boxes and uses ordinary movement;no native game rule changes.',
                        'Only the first two crystals and returns on v305. Later bosses,ending,saves,source RNG/global phase and complete source audio/video/hardware fidelity remain unproved.'])
    (ROOT/'analysis/d2_campaign_v0305_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
    print(f'v305:axe,fairy,second crystal and exterior return verified;12 cold replays;stack margin{margin} bytes')


if __name__=='__main__':main()
