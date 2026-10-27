"""Verify second D7 key, two ordinary Earth casts and the1B9 mechanism."""
import gzip,json,re
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
    digest=sha(read('versions/v0293-878a7f44/gaw-megadrive-v0293.bin'));prior=load('analysis/d7_approach_v0293_report.json')
    assert prior['passed'] and prior['md_sha256']==digest and prior['first_d7_key_obtained']
    manifest=load('analysis/d6-campaign-v0293/manifest.json')
    symbol_name='megadrive/out/release/symbol.txt'
    if symbol_name in manifest['files']:
        frozen_symbols=read('analysis/d6-campaign-v0293/'+symbol_name);assert sha(frozen_symbols)==manifest['files'][symbol_name]
    else:
        item=manifest['compressed'][symbol_name]
        encoded=read('analysis/d6-campaign-v0293/'+item['stored']);assert sha(encoded)==item['stored_sha256']
        frozen_symbols=gzip.decompress(encoded);assert sha(frozen_symbols)==item['raw_sha256']
    sy={m[2].split('.lto_priv.')[0]:int(m[1],16)&65535 for line in frozen_symbols.decode().splitlines() if(m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))};stages=[]
    for suffix in ['key03','earth1b9-02','earth1b9-03','contact1b9-01']:
        root='validation/natural-dungeon-combat/md-auto-v0293-d7-'+suffix
        c=load(root+'/capture.json');r=load(root+'/report.json')
        p=load(root+f'-assisted-fixed-replay-{c["frames"]}/replay_report.json')
        a,w=recording(ROOT/root,c);read(root+'/assistance.json')
        assert c['rom_sha256']==p['rom_sha256']==digest and c['sram_input'] is None
        assert p['passed'] and p['whole_ram_bytes']==65536 and p['final_png_exact'] and not p['feedback_reads']
        for n,h in p['evidence'].items():assert sha(read(root+'/'+n))==h
        assert a['boss_room']==0x179 and a['first_boss_entry'] is None and a['preserve_floor_hurt_requested']
        assert not a['health_refills'] and not a['primary_state_imports'] and not a['boss_assistance']
        assert all(address==sy['hero_hurt'] for _,address,_ in w)
        assert not r['deaths'] and r['failure'] is None and r['last_state']['health']==74 and r['last_state']['keys']==2
        raw=read(root+f'/ram_{c["frames"]:05d}.bin');read(root+f'/frame_{c["frames"]:05d}.png')
        data=lambda name,n:bytes(raw[(sy[name]+i)^1] for i in range(n))
        save=data('game_save_state',592);cells=data('scratch',4096)[0x800:0x8a0]
        assert save[0x1f:0x25]==bytes([128]*6) and save[0x25]==0
        if suffix=='key03':
            assert r['room_cleared'] and r['new_key_verified'] and r['last_state']['magic']==48
            assert r['driver_sha256']==sha(read('validation/natural-dungeon-combat/md-auto-v0293-d7-earth1b9-01/combat_driver_before.py'))
            events=load(root+'/events.json');assert any(e['health']==58 for e in events) and any(e['health']==74 for e in events)
        elif suffix.startswith('earth'):
            assert r['passed'] and r['earth_route_passed'] and r['earth_cell_cleared']
            assert r['earth_action_only_requested'] and not r['earth_passage_traversed'] and not r['earth_state_writes']
            assert r['last_state']['game']==12 and r['last_state']['selected']==1 and not save[0x50+0xb9]&4
            assert r['earth_controller_sha256']==sha(read('tools/natural_earth_passage.py'))
            assert r['driver_sha256']==sha(read('tools/natural_dungeon_combat.py'))
            assert cells[0x36]==0
            if suffix.endswith('02'):
                assert r['earth_cell']==0x36 and r['earth_cast_position']==[104,80] and r['earth_cast_direction']==0
                assert r['last_state']['magic']==40 and cells[0x2b]==11
            else:
                assert r['earth_cell']==0x2b and r['earth_cast_position']==[168,48] and r['earth_cast_direction']==3
                assert r['last_state']['magic']==32 and cells[0x2b]==0
        else:
            assert r['passed'] and r['contact_route_passed'] and not r['contact_state_writes']
            assert r['contact_room']==0x1b9 and r['contact_destination']==0x1b8 and r['contact_opened']['flags']&4
            assert save[0x50+0xb9]&4 and r['last_state']['room']==0x1b8
        stages.append(dict(trace=root,frames=c['frames'],last_state=r['last_state'],whole_ram_bytes=65536,final_png_exact=True))
    diagnostic=load('validation/natural-dungeon-combat/md-auto-v0293-d7-earth1b9-01/report.json')
    assert diagnostic['earth_cell_cleared'] and not diagnostic['earth_route_passed'] and diagnostic['last_state']['game']==16
    for n in ['natural_contact_passage.py','assisted_boss_route.py','summarize_d7_passage_v0293.py']:read('tools/'+n)
    out=dict(passed=True,version=293,md_sha256=digest,production_rom_unchanged=True,stages=stages,
             d7_keys_obtained=2,keys_remaining=2,health=74,max_health=80,magic_spent=16,
             mechanism1b9_opened=True,room1b8_entered=True,boss_entered=False,dungeon7_completed=False,
             source_campaign_compared=False,full_game_validated=False,evidence=refs,
             limits=['Logged hurt-counter protection remains on the approach. No health,items,keys,magic or primary snapshots are injected. The boss has not been entered.',
                     'The first Earth attempt stopped in the menu after clearing36. The wrapper now continues after room-clear success until its action ends; ordinary failure and frame-budget stops remain active.',
                     'Earth casts clear36 then2B but do not by themselves claim passage completion. A separate real UP mechanism and traversal prove entry into1B8.',
                     'Ship,boss,seventh crystal,exit,later dungeons,ending and whole-game SMS/audio/visual/hardware fidelity remain unverified.'])
    (ROOT/'analysis/d7_passage_v0293_report.json').write_text(json.dumps(out,indent=2)+'\n')
    print('D7 two keys,Earth36/2B and mechanism1B9 to1B8: cold RAM/PNG exact,74/80HP')


if __name__=='__main__':main()
