"""Version-bound single-pass masking,controlled burst cadence and fresh D1 proof."""
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
    digest=sha(read('versions/v0304-b7b4e150/gaw-megadrive-v0304.bin'))
    host=load('analysis/sprite_mask_cache_host_v0304_report.json')
    pixels=load('analysis/sprite_mask_cache_gameplay_v0304_report.json')
    native=load('analysis/sprite_rows_native_v0304_report.json')
    burst=load('analysis/burst_variant_7c_v0304_gameplay_report.json')
    cost=load('analysis/burst_render_cost_cost-v0304_report.json')
    coherent=load('analysis/world_frame_coherence_v0304_report.json')
    for report in [host,pixels,native,burst,cost,coherent]:assert report['md_sha256']==digest
    assert host['passed'] and host['compiled_c_cases']==133120
    assert pixels['passed'] and len(pixels['cases'])==12 and all(c['all_pixels_exact'] and c['physical_sprite_frames']==9 for c in pixels['cases'])
    assert native['passed'] and all(r['done'] and not r['failed'] and r['cases']==8192 for r in native['results'])
    assert len(burst['cases'])==6 and burst['all_cases_exact'] and not burst['diagnostic']
    assert {(c['region'],c['type']) for c in burst['cases']}=={(r,t) for r in ['auto','pal'] for t in [0x6a,0x6b,0x7c]}
    assert all(c['frames']==252 and c['all_768_actor_bytes_exact'] for c in burst['cases'])
    assert all(not r['gaps'] for r in cost['results']) and len(cost['results'])==2
    baseline=load('analysis/burst_render_cost_cost-v0296_report.json')
    assert all(len(r['gaps'])==36 for r in baseline['results'])
    assert coherent['passed'] and len(coherent['cases'])==12 and all(c['differing_pixels']==0 for c in coherent['cases'])
    candidates=load('analysis/burst_cadence_v0304_candidates.json')
    assert candidates['selected_version']==304 and len(candidates['candidates'])==8
    for stage in candidates['candidates']:
        observed=load(stage['report']);assert observed['md_sha256']==stage['md_sha256']
        assert {r['region']:len(r['gaps']) for r in observed['results']}==stage['gaps']
    source_index=load('analysis/burst_cadence_v0304_source_index.json')
    for item in source_index['sources'].values():assert sha(read(item['path']))==item['sha256']
    assert host['production_source_sha256']==native['production_source_sha256']==source_index['sources']['megadrive/src/main.c']['sha256']
    assert native['helper_sha256']==source_index['sources']['row_helper.inc']['sha256']
    assert sha(read('validation/v0304-sources/row_harness_rom.bin'))==native['harness_sha256']
    sy=symbols(ROOT/'validation/stack-v0304-d1-all/symbol.txt');read('validation/stack-v0304-d1-all/symbol.txt')
    stages=[]
    for suffix,frame,hp,room in [('boss01',12867,32,0x175),('exit01',14583,28,0xb9)]:
        root='validation/natural-dungeon-combat/md-auto-v0304-d1-'+suffix
        capture=load(root+'/capture.json');report=load(root+'/report.json')
        proof=load(root+f'-assisted-fixed-replay-{frame}/replay_report.json')
        assist,writes=recording(ROOT/root,capture);read(root+'/assistance.json')
        assert capture['rom_sha256']==proof['rom_sha256']==digest and capture['frames']==frame and capture['sram_input'] is None
        assert proof['passed'] and proof['whole_ram_bytes']==65536 and proof['final_png_exact'] and not proof['feedback_reads']
        for n,h in proof['evidence'].items():assert sha(read(root+'/'+n))==h
        assert report['failure'] is None and not report['deaths'] and report['room_cleared']
        assert report['assisted_route'] and report['ram_injections'] and not report['boss_assistance']
        assert assist['release_write_frame']==11893 and assist['first_boss_combat']==dict(frame=11965,health=20,hurt=0)
        assert assist['first_boss_damage']==dict(frame=12049,before=20,after=16,hurt=47)
        assert max(f for f,_,_ in writes)==11893 and all(address==sy['hero_hurt'] for _,address,_ in writes)
        raw=read(root+f'/ram_{frame:05d}.bin');read(root+f'/frame_{frame:05d}.png')
        data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k))
        word=lambda n:int.from_bytes(data(n,2),'big')
        assert word('room_id')==room and word('hero_health')==hp and word('hero_max_health')==32
        assert data('game_save_state',592)[0x1f:0x28]==bytes([128]+[0]*8)
        assert data('hero_items',17)==bytes(17) and word('hero_selected_item')==0
        if suffix=='exit01':assert report['full_dungeon_cleared'] and report['dungeon_exit_verified']
        stages.append(dict(trace=root,frames=frame,room=room,health=hp,max_health=32,whole_ram_png_exact=True))
    old_route=load('validation/natural-dungeon-combat/md-auto-v0304-d3-rope-rebase01/report.json')
    assert not old_route['passed'] and old_route['failure']=='next_approach_prerequisite_mismatch' and not old_route['ram_injections']
    stack=load('validation/stack-v0304-d1-all/stack_report.json')
    assert stack['md_sha256']==digest and stack['all_instructions'] and stack['frames']==14583 and not stack['invalid_heap_examples']
    boundary=stack['heap_changes'][-1]['end']+2;assert stack['minimum_sp']-boundary==496
    assert read('validation/stack-v0304-d1-all/ram_14583.bin')==read('validation/natural-dungeon-combat/md-auto-v0304-d1-exit01/ram_14583.bin')
    assert read('validation/stack-v0304-d1-all/frame_14583.png')==read('validation/natural-dungeon-combat/md-auto-v0304-d1-exit01/frame_14583.png')
    read('tools/summarize_burst_cadence_v0304.py')
    result=dict(passed=True,version=304,md_sha256=digest,controlled_burst_cadence_fixed=True,
                controlled_actor_frames_exact=1512,actor_bytes_per_frame=768,
                physical_simulation_gaps=dict(baseline_ntsc=36,baseline_pal=36,current_ntsc=0,current_pal=0),
                host_mask_cases=133120,native_row_cases_per_region=8192,native_mask_sprite_frames=108,
                coherent_natural_framebuffers=12,fresh_first_crystal_and_exit=True,
                current_campaign_stages=stages,guard_release_lead_frames=72,boss_assistance=False,
                primary_state_imports=0,health_refills=0,observed_stack_margin_bytes=496,
                second_dungeon_revalidated=False,full_game_validated=False,evidence=refs,
                limits=['Controlled exterior boss/hero records and initial world-clock alignment. All six6A/6B/7C PAL/NTSC first-cycle traces match source actor RAM; this does not establish global boot-to-combat phase,RNG,all encounters or whole-game speed.',
                        'Host masking tests use a constant VRAM port and varied queued patterns. Exact inline assembly has its own native8192-case test; real sprite pixels have separate native old/new comparisons. Full game video/audio and physical hardware remain unproved.',
                        'Historical ordinary buttons diverge before D1. Fresh adaptive entry/key route,first crystal and exterior return are independently cold-replayed. Logged hurt protection covers only the approach; boss and return add no assistance. Later dungeon proofs remain historical versions.'])
    (ROOT/'analysis/burst_cadence_v0304_report.json').write_text(json.dumps(result,indent=2)+'\n')
    print('v304:controlled burst gaps36->0 in both regions;1512 actor frames exact;fresh D1 crystal/exit exact;496-byte observed stack margin')


if __name__=='__main__':main()
