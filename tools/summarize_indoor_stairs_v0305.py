"""Version305: source-confirmed interior stairs, natural oil route and stack."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from validate_playable_sprite_limit import symbols


def main():
    refs={}
    def read(n):
        raw=evidence(ROOT/n);refs[n]=sha(raw);return raw
    def load(n):return json.loads(read(n))
    rom=read('versions/v0305-83dfaf69/gaw-megadrive-v0305.bin');digest=sha(rom)
    assert digest=='83dfaf697521ce97597af259835eccae70bde055e70f321176caad34f93a23c7' and len(rom)==2097152
    checksum=sum(int.from_bytes(rom[i:i+2],'big') for i in range(512,len(rom),2))&65535
    assert checksum==int.from_bytes(rom[0x18e:0x190],'big')==0xc3b8
    assert read('gaw-megadrive.bin')==read('gaw-title-megadrive.bin')==rom
    original=read('input/original.sms')
    assert sha(original)=='852e068e331dbfb01b9c38a62eecf81ce5b9f0f1bd10fff497117bd885c716c9'
    before=load('validation/v0304-before-indoor-fix/before.json')
    after=load('validation/v0305-indoor-sources/after.json')
    assert before['production_sources'].keys()==after['production_sources'].keys()
    changed=[n for n,h in before['production_sources'].items() if after['production_sources'][n]!=h]
    assert changed==['megadrive/src/main.c']
    old=read('validation/v0304-before-indoor-fix/main.c');new=read('validation/v0305-indoor-sources/main.c')
    old_line=b'    if(world_graphics_class==1) return;\r\n    number=neighboring_room(direction);'
    new_line=b'    /* 2051..21C5 also scrolls connected interior rooms, e.g.1F <->0F. */\r\n    number=neighboring_room(direction);'
    assert old.count(old_line)==1 and old.replace(old_line,new_line)==new
    assert sha(old)==before['production_sources']['megadrive/src/main.c'] and sha(new)==after['production_sources']['megadrive/src/main.c']
    for n,h in before['protected'].items():assert sha(evidence(ROOT/n))==h
    assert len(before['protected'])==305
    symbols_name='validation/v0305-indoor-sources/symbol.txt';read(symbols_name);sy=symbols(ROOT/symbols_name)
    baseline=load('validation/indoor-stairs-v0304-baseline02/report.json')
    assert baseline['passed'] and baseline['baseline_block_reproduced']
    assert baseline['results']['sms']['final']['oil']==1 and baseline['results']['md']['final']['oil']==0
    assert baseline['results']['md']['visited']==[0x1f]
    rows=[]
    for suffix in ['', '-pal']:
        root='validation/indoor-stairs-v0305-fix01'+suffix
        r=load(root+'/report.json');assert r['passed'] and not r['baseline_block_reproduced']
        assert r['actual_c7_door_used'] and not r['post_door_outside_context_mutation'] and not r['inventory_or_actor_fixtures']
        values={}
        for tag in ['sms','md']:
            capture=load(root+'/'+tag+'/capture.json');f=capture['frames'];raw=read(root+'/'+tag+f'/ram_{f:05d}.bin')
            assert capture['sram_input'] is None and max(w['frame'] for w in capture['test_ram_writes'])==3400
            assert capture['rom_sha256']==(sha(original) if tag=='sms' else digest)
            seq=[]
            for event in r['results'][tag]['events']:
                if not seq or seq[-1]!=event['room']:seq.append(event['room'])
            assert seq==[0x1f,0xf,0x1f,0xc7]
            if tag=='sms':items=raw[0xe0:0xf1];cells=raw[0x1c00:0x1ca0]
            else:
                data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k))
                word=lambda n:int.from_bytes(data(n,2),'big')
                items=bytes([word('hero_basic_level'),word('hero_weapon_level')])+data('hero_items',17)[2:]
                cells=data('scratch',4096)[0x800:0x8a0]
            values[tag]=(items,cells)
        assert values['sms']==values['md']
        rows.append(dict(region=r['region'],room_sequence=[31,15,31,199],semantic_inventory_bytes_exact=17,
                         final_cells_exact=160,oil_owned=1,outside_flag=r['results']['md']['final']['flags']))
    stages=[]
    for root,report_name in [('validation/natural-dungeon-route/md-v0305-oil-route01','route_report.json'),
                             ('validation/natural-service-route/md-v0305-oil-stairs02','report.json')]:
        c=load(root+'/capture.json');r=load(root+'/'+report_name);f=c['frames']
        proof=root+'-fixed-replay';p=load(proof+'/replay_report.json')
        assert p['passed'] and p['whole_ram_bytes']==65536 and p['final_png_exact'] and not p['feedback_reads']
        assert c['rom_sha256']==p['rom_sha256']==digest and not c['test_ram_writes'] and c['sram_input'] is None
        assert r['failure'] is None and not r['ram_injections'] and not r['sram_checkpoint_injection']
        for n,h in p['evidence'].items():assert sha(read(root+'/'+n))==h
        for stem,ext in [('ram','bin'),('frame','png')]:
            n=f'/{stem}_{f:05d}.{ext}';assert read(root+n)==read(proof+n)
        if report_name=='route_report.json':
            assert r['reached_entrance'] and not r['normal_continues']
            assert r['route_driver_sha256']==sha(read('validation/v0305-indoor-sources/natural_dungeon_route.py'))
        else:
            assert r['passed'] and not r['primary_state_imports']
            assert r['first_state']['oil']==0 and r['last_state']['oil']==1 and r['last_state']['flags']&2
            assert r['last_state']['room']==r['last_state']['outside']==0xc7 and r['last_state']['health']==8
            assert sha(read(root+'/oil_stairs_driver.py'))==r['driver_sha256']
            seq=[]
            for event in load(root+'/events.json'):
                if not seq or seq[-1]!=event['room']:seq.append(event['room'])
            assert seq==[0x1f,0xf,0x1f,0xc7]
        stages.append(dict(trace=root,frames=f,whole_ram_png_exact=True))
    stack_root='validation/stack-v0305-oil-all';s=load(stack_root+'/stack_report.json')
    assert s['md_sha256']==digest and s['frames']==stages[-1]['frames'] and s['all_instructions'] and s['read_only']
    assert not s['ram_injections'] and not s['invalid_heap_examples']
    assert s['minimum_instruction_sp']==min(r['sp'] for r in s['instruction_minima'])
    assert s['minimum_sp']==min(s['minimum_instruction_sp'],s['minimum_sampled_sp'])
    boundary=max(r['end']+2 for r in s['heap_changes']);margin=s['minimum_sp']-boundary;assert margin>0
    for stem,ext in [('ram','bin'),('frame','png')]:
        n=f'/{stem}_{s["frames"]:05d}.{ext}';assert read(stack_root+n)==read(stages[-1]['trace']+n)
    historical=load('validation/natural-dungeon-combat/md-auto-v0305-d8-rebase-dynamic01/report.json')
    assert not historical['passed'] and historical['rom_sha256']==digest and historical['failure']=='hero_died'
    assert historical['last_state']['room']==0x163 and historical['last_state']['crystals']==[128]*4+[0]*5
    for n in ['tools/validate_indoor_stairs.py','tools/natural_oil_stairs.py','tools/summarize_indoor_stairs_v0305.py']:
        read(n)
    result=dict(passed=True,version=305,md_sha256=digest,source_sha256=sha(original),bytes=len(rom),checksum='C3B8',
                changed_production_sources=changed,old_numbered_roms_preserved=304,baseline_block_reproduced=True,
                controlled_source_comparisons=rows,natural_stages=stages,natural_oil_and_exterior_return=True,
                natural_health=8,natural_ram_injections=False,natural_sram_checkpoint_injection=False,
                instruction_stack_margin_bytes=margin,stack_frames=s['frames'],
                historical_full_campaign_promoted=False,full_game_validated=False,evidence=refs,limits=[
                    'Original2051..21C5 permits interior borders. The v304 graphics_class1 early return blocked1F->0F. The sole production edit removes it;normal exterior/dungeon gates remain.',
                    'Controlled actual C7 door plus one interior pose fixture compare both regions,Oil ownership,seventeen semantic inventory values and160 final cells. Dedicated native primary/axe level fields normalize the source inventory entries0/1.',
                    'Natural new-game route and Oil/stairs/return replay with all65536RAM and finalPNG exact,without any RAM/SRAM fixtures. The read-only instruction-stack profile covers4677 frames of this path,not the entire campaign.',
                    'Historical v304 commands are not promoted:the v305 adaptive-guard replay reaches four crystals then dies inD5. This is retained as a failed fixed-input regression;the full v305 campaign requires further work.',
                    'The v304 seventh crystal/thief-key evidence remains version-specific. Later bosses,ending,saves,source RNG/global phase and complete SMS video/audio/hardware fidelity remain unproved.'])
    (ROOT/'analysis/indoor_stairs_v0305_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
    print(f'v305:interior stairs/source Oil route exact;natural cold RAM/PNG replays passed;observed instruction-stack margin{margin} bytes')


if __name__=='__main__':main()
