"""Bind source78/79 dispatch omission, narrow fix and independent Z80 checks."""
import json
import subprocess
from run_core import ROOT
from archive_lossless_evidence import sha


def main():
    refs={}
    def read(name):
        raw=(ROOT/name).read_bytes();refs[name]=sha(raw);return raw
    def load(name):return json.loads(read(name))
    rom=read('gaw-megadrive.bin');digest=sha(rom)
    assert rom==read('gaw-title-megadrive.bin')==read('versions/v0294-508642dc/gaw-megadrive-v0294.bin')
    assert len(rom)==2097152 and digest=='508642dc6a7f27883746b1bbb5b208045205644205be325a3d3a317ecca87098'
    checksum=sum(int.from_bytes(rom[n:n+2],'big') for n in range(512,len(rom),2))&65535
    assert checksum==int.from_bytes(rom[0x18e:0x190],'big')==0x7f10
    original=read('input/original.sms')
    assert all(int.from_bytes(original[0x2b63+kind*2:0x2b65+kind*2],'little')==0x506b for kind in [0x63,0x64,0x78,0x79])
    assert original[0x506b:0x5071]==bytes.fromhex('2154a7c3604c')
    locations=[dict(room=room,types=[kind for kind in original[0x3234e+room*8:0x32356+room*8] if kind in [0x78,0x79]]) for room in range(512)]
    locations=[r for r in locations if r['types']]
    assert locations==[dict(room=0x1b8,types=[0x78]),dict(room=0x1be,types=[0x79])]
    baseline=subprocess.check_output(['git','show','50a3271:megadrive/src/actors.c'],cwd=ROOT)
    current=read('megadrive/src/actors.c')
    expected=baseline.replace(b'else if(entity[0]==0x63 || entity[0]==0x64)',b'/* Source2B63 also maps the ordinary variants78/79 to506B. */\r\n            else if(entity[0]==0x63 || entity[0]==0x64 || entity[0]==0x78 || entity[0]==0x79)')
    expected=expected.replace(b'(entity[0]>=0x72 && entity[0]<=0x76) || entity[0]==0x7a',b'(entity[0]>=0x72 && entity[0]<=0x76) || entity[0]==0x78 || entity[0]==0x79 || entity[0]==0x7a')
    assert current==expected
    production_changed=subprocess.check_output(['git','diff','50a3271','--name-only','--','megadrive/src'],cwd=ROOT,text=True).splitlines()
    assert production_changed==['megadrive/src/actors.c']
    unit=load('analysis/first_boss_alias_v0294_report.json');game=load('analysis/first_boss_alias_game_v0294_report.json')
    assert unit['md_sha256']==game['md_sha256']==digest and unit['source_sha256']==sha(original)
    assert unit['cases']==unit['boss_cases']==1824 and unit['all_768_actor_bytes_exact']
    assert unit['alias_types']==[0x63,0x64,0x78,0x79]
    assert len(game['cases'])==24 and all(r['all_768_actor_bytes_exact'] for r in game['cases'])
    assert {r['type'] for r in game['cases']}=={0x63,0x64,0x78,0x79}
    frames=sum(r['frames'] for r in game['cases']);assert frames==1232
    blocked=load('validation/natural-dungeon-combat/md-auto-v0293-d7-key05/report.json')
    assert blocked['failure']=='controller_stalled' and blocked['last_state']['room']==0x1b8
    actor=blocked['last_actors'][0];assert actor['type']==0x78 and actor['state']==0 and actor['flags']==0x20 and actor['hp']==30 and not actor['hit_box']
    retry=load('validation/natural-dungeon-combat/md-auto-v0294-d7-rebase01/report.json')
    assert not retry['passed'] and retry['failure']=='hero_died' and retry['frames']==13489
    for name in ['validate_first_boss.py','validate_first_boss_gameplay.py','first_boss_harness.c','first_boss_cases.inc','summarize_first_boss_variants_v0294.py','natural_dungeon_combat.py','natural_earth_passage.py','rebase_assisted_campaign.py']:
        read('tools/'+name)
    report=dict(passed=True,version=294,md_sha256=digest,bytes=len(rom),checksum='7F10',
                source_dispatch=0x506b,variant_locations=locations,production_scope='78/79 behavior dispatch and collision publication in actors.c only',
                isolated_original_native_cases=1824,production_loop_cases=24,production_actor_frames=frames,
                full_768_actor_bytes_exact=True,regions=['auto','pal'],natural_d7_correction_validated=False,
                historical_cold_replay_completed=False,historical_replay_failure=retry['failure'],historical_replay_stop_frame=13489,
                full_game_validated=False,source_campaign_compared=False,evidence=refs,
                limits=['Original dispatch aliases and narrow source diff establish the missing78/79 behavior. Unit fixtures execute original instructions with two explicit refresh bytes; full original RNG stream is not reproduced.',
                        'PAL/NTSC production segments inject an actor record and hero position in an exterior room. All768 actor bytes match,including collision boxes; actual D7 room graphics,all framebuffer/audio and a natural victory are not proven.',
                        'The historical v293 fixed controls die in D1 on the new build. This does not validate the current full campaign or identify the cause of trajectory divergence. Earlier D6/D7 campaign proofs remain scoped to v293.',
                        'A new adaptive current-ROM campaign,remaining dungeons,ending and global fidelity remain required.'])
    (ROOT/'analysis/first_boss_variants_v0294_report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('v294:78/79 source aliases restored;1824 unit cases and1232 PAL/NTSC actor frames exact;current campaign pending')


if __name__=='__main__':main()
