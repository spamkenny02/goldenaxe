"""Bind native magic rope, controlled source oracle and natural v287 D1 evidence."""
import json
from run_core import ROOT
from rebase_natural_campaign import evidence
from archive_lossless_evidence import sha
from validate_playable_sprite_limit import symbols

def main():
    refs={}
    def read(name):
        b=evidence(ROOT/name);refs[name]=sha(b);return b
    def load(name):return json.loads(read(name))
    digest=sha((ROOT/'gaw-megadrive.bin').read_bytes());rules=load('analysis/magic_rope_rules_report.json');game=load('analysis/magic_rope_game_report.json')
    assert rules['passed'] and rules['module_sha256']==sha(read('megadrive/src/source_magic_rope.c'))
    assert game['passed'] and game['rom_sha256']==digest
    assert len(game['results'])==4 and all(r['next_vblank_rows_exact']==6 for r in game['results'])
    stages=[]
    for name in ['md-v0287-d1-entry01','md-auto-v0287-axe01','md-auto-v0287-d1-boss01','md-auto-v0287-d1-exit01']:
        family='natural-dungeon-route' if 'entry' in name else 'natural-dungeon-combat';base=f'validation/{family}/{name}'
        r=load(base+('/route_report.json' if family=='natural-dungeon-route' else '/report.json'));c=load(base+'/capture.json');proof=load(base+'-fixed-replay/replay_report.json')
        assert r['rom_sha256']==c['rom_sha256']==proof['rom_sha256']==digest
        assert not c['test_ram_writes'] and c['sram_input'] is None
        assert proof['passed'] and proof['whole_ram_bytes']==65536 and proof['final_png_exact']
        assert r['failure'] is None and not r.get('deaths',0)
        stages.append(dict(trace=base,frames=c['frames'],state=r['last_state'],full_ram_png_cold_replay=True))
    final=stages[-1]['state'];assert final['first_gem']==128 and final['completed_dungeon_progress']==128 and final['max_health']==32 and final['weapon']==final['selected']==1 and final['dungeon']==0 and final['room']==0xb9 and final['health']>0
    stack=load('validation/stack-v0287-d1-natural-all/stack_report.json');assert stack['all_instructions'] and not stack['invalid_heap_examples'] and not stack['ram_injections'] and stack['md_sha256']==digest
    minimum=min(v['sp'] for v in stack['instruction_minima']);heap=stack['heap_changes'][-1]['end']+2
    assert minimum>=heap
    old_d3=[]
    for tag,frame in [('md',41270),('sms',62281)]:
        base=f'validation/natural-dungeon-combat/{tag}-auto-v0286-d3-rope01';r=load(base+'/report.json');c=load(base+'/capture.json');proof=load(base+f'-assisted-fixed-replay-{frame}/replay_report.json');assist=load(base+'/assistance.json')
        assert r['room_cleared'] and r['failure'] is None and not r['deaths'] and r['last_state']['item_value']==1 and r['last_state']['room']==0x1f4
        assert proof['passed'] and proof['final_png_exact'] and proof['rom_sha256']==r['rom_sha256']==c['rom_sha256']
        assert len(assist['episodes'])==2 and assist['episodes'][0]['release_write_frame']<assist['episodes'][1]['activation_after_frame']
        read(base+'/controls.json');read(base+f'/ram_{frame:05}.bin')
        old_d3.append(dict(trace=base,rom_sha256=r['rom_sha256'],state=r['last_state'],approach_assisted=True,full_ram_png_cold_replay=True))
    oldsy=symbols(ROOT/'validation/v0286-d3-symbol.txt');raw=read('validation/natural-dungeon-combat/md-auto-v0286-d3-rope01/ram_41270.bin');sms=read('validation/natural-dungeon-combat/sms-auto-v0286-d3-rope01/ram_62281.bin')
    data=lambda n,k:bytes(raw[(oldsy[n]+i)^1] for i in range(k))
    assert data('game_save_state',592)[0x50:0x150]==sms[0x100:0x200]
    assert data('sms_vram',16384)[0x3800:0x3d00]==sms[0x1600:0x1b00]
    assert data('hero_items',17)==sms[0xe0:0xf1]
    source=load('validation/natural-dungeon-combat/sms-auto-v0286-d3-boss03/report.json');capture=load('validation/natural-dungeon-combat/sms-auto-v0286-d3-boss03/capture.json');proof=load(f"validation/natural-dungeon-combat/sms-auto-v0286-d3-boss03-assisted-fixed-replay-{capture['frames']}/replay_report.json")
    assert source['room_cleared'] and not source['deaths'] and proof['passed']
    failures=[]
    for n in ['boss03','boss04']:
        p=f'validation/natural-dungeon-combat/md-auto-v0286-d3-{n}';r=load(p+'/report.json');a=load(p+'/assistance.json')
        assert r['deaths']==1 and r['entered_room'] and not r['room_cleared'] and a['release_write_frame']<a['first_boss_combat']['frame'] and a['first_boss_combat']['hurt']==0
        assert max(w['frame'] for w in a['writes'])==a['release_write_frame']
        failures.append(dict(trace=p,failure=r['failure'],state=r['last_state'],release_frame=a['release_write_frame'],first_boss_combat=a['first_boss_combat'],cold_replay_verified=False))
    result=dict(passed=True,md_sha256=digest,version=287,source_rules=rules,production_rope=game['results'],natural_d1=stages,stack=dict(minimum_sp=minimum,heap_boundary=heap,observed_margin_bytes=minimum-heap,heap_valid=True,frames=stack['frames']),historical_v286_d3_rope=old_d3,historical_v286_d3_cross_system=dict(flags_exact_bytes=256,map_exact_bytes=1280,inventory_exact_bytes=17),historical_v286_d3_native_failed_boss_trials=failures,full_game_validated=False,evidence=refs,limits=['Controlled rope fixtures validate original terrain logic, byte state and next-VBlank tile publication in PAL/NTSC; natural rope deployment and hardware remain unvalidated.','D1 passed naturally on v287; D2 and D3 rope progression cited here belong to historical v286, not v287.','D3 source boss victory passed fixed replay; native v286 boss trials died. No D3 native boss victory is claimed and no source/port AI bug is inferred solely from different fights.','The obsolete v286 fixed D1 controls failed to reach the target on v287; new adaptive ordinary controls were recorded and independently replayed.','Full campaign, source RNG/R/IRQ integration, global timing, waveform and hardware parity remain incomplete.'])
    (ROOT/'analysis/magic_rope_v0287_report.json').write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items() if k in ['passed','md_sha256','stack']})
if __name__=='__main__':main()
