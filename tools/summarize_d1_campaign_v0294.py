"""Current v294 D1 crystal and exit, with approach-only assistance."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols


def main():
    refs={}
    def read(name):
        raw=(ROOT/name).read_bytes();refs[name]=sha(raw);return raw
    def load(name):return json.loads(read(name))
    digest=sha(read('gaw-megadrive.bin'));assert digest==sha(read('versions/v0294-508642dc/gaw-megadrive-v0294.bin'))
    sy=symbols(ROOT/'megadrive/out/release/symbol.txt');stages=[]
    for suffix in ['assisted03','exit01']:
        root='validation/natural-dungeon-combat/md-auto-v0294-d1-'+suffix
        c=load(root+'/capture.json');r=load(root+'/report.json');p=load(root+f'-assisted-fixed-replay-{c["frames"]}/replay_report.json')
        a,w=recording(ROOT/root,c);read(root+'/assistance.json')
        assert c['rom_sha256']==p['rom_sha256']==digest and c['sram_input'] is None
        assert p['passed'] and p['whole_ram_bytes']==65536 and p['final_png_exact'] and not p['feedback_reads']
        for n,h in p['evidence'].items():assert sha(read(root+'/'+n))==h
        assert a['activation_after_frame']==5045 and a['boss_room']==0x175
        assert a['release_write_frame']==12338 and a['first_boss_combat']==dict(frame=12409,health=20,hurt=0)
        assert a['first_boss_damage']==dict(frame=12493,before=20,after=16,hurt=47)
        assert not a['health_refills'] and not a['primary_state_imports'] and not a['boss_assistance']
        assert all(address==sy['hero_hurt'] and 5045<frame<=12338 for frame,address,_ in w)
        assert r['failure'] is None and not r['deaths'] and r['last_state']['max_health']==32
        raw=read(root+f'/ram_{c["frames"]:05d}.bin');read(root+f'/frame_{c["frames"]:05d}.png')
        data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k))
        assert data('game_save_state',592)[0x1f:0x28]==bytes([128]+[0]*8)
        assert data('hero_items',17)==bytes(17) and r['last_state']['weapon']==r['last_state']['selected']==0
        if suffix=='assisted03':
            assert r['room_cleared'] and r['last_state']['health']==32 and r['last_state']['room']==0x175
        else:
            assert r['full_dungeon_cleared'] and r['dungeon_exit_verified']
            assert r['last_state']['room']==0xb9 and r['last_state']['dungeon']==0 and r['last_state']['health']==28
            assert a['unassisted_extension'] and a['new_assistance_writes']==0
            assert r['planning_decisions']==r['verified_persistent_prediction_windows']==r['full_ram_prediction_matches']==23
        stages.append(dict(trace=root,frames=c['frames'],last_state=r['last_state'],whole_ram_bytes=65536,final_png_exact=True))
    stack_root='validation/stack-v0294-d1-all';s=load(stack_root+'/stack_report.json')
    assert s['md_sha256']==digest and s['all_instructions'] and s['frames']==15025 and not s['invalid_heap_examples']
    low=min(x['sp'] for x in s['instruction_minima']);boundary=max(x['end']+2 for x in s['heap_changes']);assert low>=boundary
    for stem,ext in [('ram','bin'),('frame','png')]:assert read(stack_root+f'/{stem}_15025.{ext}')==read(stages[-1]['trace']+f'/{stem}_15025.{ext}')
    for n in ['summarize_d1_campaign_v0294.py','assisted_boss_route.py','natural_dungeon_combat.py','natural_exit_planner.py','profile_playable_stack.py','replay_assisted_prefix.py']:read('tools/'+n)
    out=dict(passed=True,version=294,md_sha256=digest,production_rom_unchanged=True,native_d1_completed=True,
             stages=stages,approach_assistance=True,boss_assistance=False,health_refills=0,primary_state_imports=0,
             guard_release_lead_frames=71,ordinary_boss_damage_observed=True,exit_health=28,max_health=32,
             stack=dict(frames=15025,all_instructions=True,minimum_sp=low,heap_boundary=boundary,observed_margin_bytes=low-boundary,heap_valid=True,whole_ram_png_exact=True),
             historical_fixed_campaign_still_invalid=True,source_campaign_compared=False,full_game_validated=False,evidence=refs,
             limits=['Fresh adaptive v294 route. Only the approach after5045 uses logged hurt-counter protection. The boss and exit have ordinary damage and no new help; no health,keys,equipment or primary snapshots are injected.',
                     'The first crystal and outsideB9 are verified on this ROM,with the basic weapon. Axe acquisition and later dungeons are separate steps.',
                     'Final whole RAM and PNG match independent cold replays. Stack scope ends at15025; original SMS full campaign,all intermediate pixels,audio waves,hardware timing and ending remain unproven.'])
    (ROOT/'analysis/d1_campaign_v0294_report.json').write_text(json.dumps(out,indent=2)+'\n')
    print('v294 D1 crystal and outsideB9:28/32HP,ordinary boss damage,cold RAM/PNG exact,stack margin',low-boundary)


if __name__=='__main__':main()
