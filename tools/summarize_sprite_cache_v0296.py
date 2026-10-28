"""Version-bound pixel-equivalent tile reuse and current D3 rope milestone."""
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
    digest=sha(read('versions/v0296-3446f41f/gaw-megadrive-v0296.bin'))
    host=load('analysis/sprite_mask_cache_host_v0296_report.json')
    game=load('analysis/sprite_mask_cache_gameplay_v0296_report.json')
    assert host['passed'] and host['md_sha256']==digest and host['compiled_c_cases']==133120 and host['saved_uploads']>0
    assert game['passed'] and game['md_sha256']==digest and len(game['cases'])==12
    assert all(row['all_pixels_exact'] and row['physical_sprite_frames']==9 for row in game['cases'])
    before=load('analysis/burst_render_cost_cost-v0295_report.json')
    after=load('analysis/burst_render_cost_cost-v0296_report.json')
    assert after['md_sha256']==digest and after['read_only_timing']
    timing=[]
    for old,new in zip(before['results'],after['results']):
        assert old['region']==new['region'] and len(old['gaps'])==len(new['gaps'])==36
        assert new['gaps'][0]==dict(before=2908,after=2910,frames=2)
        old_span=next(s for s in old['mask_spans'] if s['begin']==2908)
        new_span=next(s for s in new['mask_spans'] if s['begin']==2908)
        old_jobs=next(s['jobs'] for s in old['samples'] if s['frame']==2909)
        new_jobs=next(s['jobs'] for s in new['samples'] if s['frame']==2909)
        assert new_jobs==old_jobs-2
        timing.append(dict(region=new['region'],before_first_burst_jobs=old_jobs,
                           after_first_burst_jobs=new_jobs,before_mask_master=old_span['master'],
                           after_mask_master=new_span['master'],simulation_gaps_still_present=36))
    sy=symbols(ROOT/'validation/stack-v0296-d2-all02/symbol.txt')
    read('validation/stack-v0296-d2-all02/symbol.txt')
    stages=[]
    for name,room,hp,rope in [('d2-rebase01',0xd6,31,False),('d3-entry01',0x1f8,31,False),('d3-rope01',0x1f4,48,True)]:
        root='validation/natural-dungeon-combat/md-auto-v0296-'+name
        capture=load(root+'/capture.json');report=load(root+'/report.json')
        proof=load(root+f'-assisted-fixed-replay-{capture["frames"]}/replay_report.json')
        assist,writes=recording(ROOT/root,capture);read(root+'/assistance.json')
        assert capture['rom_sha256']==proof['rom_sha256']==digest and capture['sram_input'] is None
        assert proof['passed'] and proof['whole_ram_bytes']==65536 and proof['final_png_exact'] and not proof['feedback_reads']
        for n,h in proof['evidence'].items():assert sha(read(root+'/'+n))==h
        assert report['failure'] is None and not report['deaths']
        assert all(address==sy['hero_hurt'] for _,address,_ in writes)
        raw=read(root+f'/ram_{capture["frames"]:05d}.bin');read(root+f'/frame_{capture["frames"]:05d}.png')
        data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k))
        word=lambda n:int.from_bytes(data(n,2),'big')
        assert word('room_id')==room and word('hero_health')==hp and word('hero_max_health')==48
        assert data('game_save_state',592)[0x1f:0x28]==bytes([128,128]+[0]*7)
        assert data('hero_items',17)[1]==word('hero_selected_item')==1
        assert bool(data('hero_items',17)[13])==rope
        if rope:assert report['room_cleared'] and report['collect_item_requested']==13 and report['last_state']['item_value']==1
        stages.append(dict(trace=root,frames=capture['frames'],room=room,health=hp,max_health=48,rope_owned=rope,whole_ram_png_exact=True))
    stack=load('validation/stack-v0296-d2-all02/stack_report.json')
    assert stack['md_sha256']==digest and stack['all_instructions'] and stack['frames']==37128 and not stack['invalid_heap_examples']
    boundary=stack['heap_changes'][-1]['end']+2;assert stack['minimum_sp']-boundary==356
    assert read('validation/stack-v0296-d2-all02/ram_37128.bin')==read('validation/natural-dungeon-combat/md-auto-v0296-d2-rebase01/ram_37128.bin')
    assert read('validation/stack-v0296-d2-all02/frame_37128.png')==read('validation/natural-dungeon-combat/md-auto-v0296-d2-rebase01/frame_37128.png')
    sources=load('analysis/sprite_cache_v0296_source_index.json')
    for item in sources['sources'].values():assert sha(read(item['path']))==item['sha256']
    read('tools/summarize_sprite_cache_v0296.py')
    result=dict(passed=True,version=296,md_sha256=digest,masked_tiles_reused_within_frame=True,
                host_cases=133120,native_physical_sprite_frames=108,all_controlled_sprite_pixels_exact=True,
                timing=timing,burst_slowdown_fixed=False,stages=stages,native_two_crystals=True,
                acquired_rope=True,third_crystal_validated=False,boss_assistance=False,
                health_refills=0,primary_state_imports=0,observed_stack_margin_bytes=356,
                full_game_validated=False,evidence=refs,
                limits=['Row-masked clone tiles are reused only for identical source tile and row mask within the same preparation pass. This changes clone tile identities and reduces transfers,not the expected pixels.',
                        'Selected native tests cover overlap,full actor pool,top/bottom clipping and list termination. Host port reads are stubbed; native pixel evidence is separate. Entire game video/audio and all pattern combinations remain unproved.',
                        'The first controlled burst saves two queued tile uploads,but36 two-frame simulation gaps remain in the profiled segment. This is a bounded transfer optimization,not a completed speed fix.',
                        'Logged test-only guards cover approaches. D1/D2 boss fights and returns have no assistance. The D3 rope milestone is independently replayed; no third crystal or complete campaign claim. Stack margin covers the route through D2 exit only.'])
    (ROOT/'analysis/sprite_cache_v0296_report.json').write_text(json.dumps(result,indent=2)+'\n')
    print('v296:133120 host cases,108 native sprite frames exact,D1/D2 and D3 rope replayed;burst slowdown open')


if __name__=='__main__':main()
