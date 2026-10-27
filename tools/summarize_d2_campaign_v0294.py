"""Version-bound D2 keys, cold combat prefix, second crystal and exterior exit."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols


def main():
    refs={}
    def read(name):
        raw=evidence(ROOT/name);refs[name]=sha(raw);return raw
    def load(name):return json.loads(read(name))
    digest=sha(read('versions/v0294-508642dc/gaw-megadrive-v0294.bin'))
    prior=load('analysis/d2_approach_v0294_report.json');assert prior['passed'] and prior['md_sha256']==digest
    index=load('analysis/d2_campaign_v0294_source_index.json');assert index['md_sha256']==digest
    source_hashes={}
    for name,item in index['sources'].items():assert sha(read(item['path']))==item['sha256'];source_hashes[name]=item['sha256']
    sy=symbols(ROOT/'validation/stack-v0294-d2-all/symbol.txt');read('validation/stack-v0294-d2-all/symbol.txt')
    stages=[];roots={}
    for suffix in ['key01','key02','key03','prefix02','boss04','exit01']:
        root='validation/natural-dungeon-combat/md-auto-v0294-d2-'+suffix;roots[suffix]=root
        c=load(root+'/capture.json');r=load(root+'/report.json');p=load(root+f'-assisted-fixed-replay-{c["frames"]}/replay_report.json')
        a,w=recording(ROOT/root,c);read(root+'/assistance.json')
        assert c['rom_sha256']==p['rom_sha256']==digest and c['sram_input'] is None
        assert p['passed'] and p['whole_ram_bytes']==65536 and p['final_png_exact'] and not p['feedback_reads']
        for name,h in p['evidence'].items():assert sha(read(root+'/'+name))==h
        assert len(a['episodes'])==2 and a['boss_room']==0x144 and not a['boss_assistance']
        assert not a['primary_state_imports'] and not a['health_refills'] and all(address==sy['hero_hurt'] for _,address,_ in w)
        assert r['failure'] is None and not r['deaths']
        raw=read(root+f'/ram_{c["frames"]:05d}.bin');read(root+f'/frame_{c["frames"]:05d}.png')
        data=lambda n,k:bytes(raw[(sy[n]+j)^1] for j in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
        assert data('hero_items',17)[1]==1 and word('hero_selected_item')==1
        save=data('game_save_state',592);assert save[0x1f]==128 and save[0x21:0x28]==bytes(7)
        if suffix.startswith('key'):
            assert r['new_key_verified'] and r['room_cleared'] and word('hero_health')==word('hero_max_health')==40
            assert a['first_boss_entry'] is None and save[0x20]==0
            assert r['driver_sha256']==source_hashes['validation/natural-dungeon-combat/md-auto-v0294-d2-boss01/combat_driver_before.py']
        else:
            assert a['release_write_frame']==33281 and a['first_boss_combat']==dict(frame=33338,health=40,hurt=0)
            assert a['first_boss_damage']==dict(frame=33548,before=40,after=32,hurt=47)
            assert all(f<=33281 for f,_,_ in w)
            if suffix=='prefix02':
                assert r['passed'] and r['combat_prefix_only'] and not r['room_cleared']
                assert c['frames']==33847 and word('hero_health')==16 and word('hero_hurt')==46 and data('world_actor_state',768)[24]==8
                original='validation/natural-dungeon-combat/md-auto-v0294-d2-boss01'
                for stem,ext in [('ram','bin'),('frame','png')]:assert read(root+f'/{stem}_33847.{ext}')==read(original+f'/{stem}_33847.{ext}')
                assert r['driver_sha256']==source_hashes['tools/clip_assisted_combat_prefix.py']
            else:
                assert r['room_cleared'] and save[0x20]==128 and word('hero_max_health')==48
                assert a['unassisted_extension'] and a['new_assistance_writes']==0
                assert r['primary_state_imports']==0 and r['planning_decisions']==r['verified_persistent_prediction_windows']==r['full_ram_prediction_matches']
                assert not r['stack_only_difference_windows']
                if suffix=='boss04':assert word('hero_health')==48 and not r['last_actors'] and not r['last_state']['reward_active']
                else:assert r['full_dungeon_cleared'] and r['dungeon_exit_verified'] and word('room_id')==0xd6 and word('world_dungeon_number')==0 and word('hero_health')==31
        stages.append(dict(trace=root,frames=c['frames'],last_state=r['last_state'],whole_ram_bytes=65536,final_png_exact=True))
    sroot='validation/stack-v0294-d2-all';s=load(sroot+'/stack_report.json')
    assert s['md_sha256']==digest and s['all_instructions'] and s['frames']==37128 and not s['invalid_heap_examples']
    low=min(x['sp'] for x in s['instruction_minima']);boundary=max(x['end']+2 for x in s['heap_changes']);assert low>=boundary
    for stem,ext in [('ram','bin'),('frame','png')]:assert read(sroot+f'/{stem}_37128.{ext}')==read(roots['exit01']+f'/{stem}_37128.{ext}')
    pending=load('analysis/actor_7c_v0294_pending.json');assert pending['status']=='pending_native_fix' and pending['type']==0x7c
    read('tools/summarize_d2_campaign_v0294.py')
    out=dict(passed=True,version=294,md_sha256=digest,production_rom_unchanged=True,stages=stages,
             native_two_crystals=True,dungeon2_completed=True,exit_health=31,max_health=48,keys_remaining=1,
             boss_assistance=False,health_refills=0,primary_state_imports=0,guard_release_lead_frames=57,
             cold_combat_prefix_primary_imports=0,stack=dict(frames=37128,all_instructions=True,minimum_sp=low,heap_boundary=boundary,observed_margin_bytes=low-boundary,heap_valid=True,whole_ram_png_exact=True),
             pending_native_7c_fix=True,full_game_validated=False,source_campaign_compared=False,evidence=refs,
             limits=['Approaches retain explicitly logged hurt protection. D1 and D2 bosses and their exits add no boss assistance. No health,keys,equipment or primary snapshot fixture is used.',
                     'The successful D2 branch replays the first diagnostic only through33847,at16HP and8 bossHP,then chooses new ordinary controls. Expected captured RAM/PNG are compared,never imported; the shorter prefix has its own independent cold replay.',
                     'The second diagnostic and the later part of the first diagnostic die and are not promoted. A frozen source index preserves the controller variants used by the retained records.',
                     'Stack scope ends at37128. Actor7C in11E remains an identified native omission; later dungeons,ending,original SMS full campaign and global fidelity remain unfinished.'])
    (ROOT/'analysis/d2_campaign_v0294_report.json').write_text(json.dumps(out,indent=2)+'\n')
    print('v294 two crystals and D2 exteriorD6:31/48HP,cold RAM/PNG exact,stack margin',low-boundary,';7C fix pending')


if __name__=='__main__':main()
