"""Audit actual D8 payment, entrance and unassisted intermediate on the PAL campaign."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,'tools')
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols

parser=argparse.ArgumentParser();parser.add_argument('--prefix-only',action='store_true');options=parser.parse_args()
work=Path(__file__).resolve().parent;project=work/'isolated/project';paths={Path(__file__).resolve(),work/'prepare_pal_d8_entry.py'}
def read(p):paths.add(p);return p.read_bytes()
def load(p):return json.loads(read(p))
digest=sha((project/'gaw-megadrive.bin').read_bytes());assert digest=='9e747d38e0c6fb2d69b7c1aa8c2b296a61e8b6af41171d14e543ed9a6cb49cf5'
prior=load(ROOT/'analysis/palc0046_d7_report.json');assert prior['passed'] and prior['actual_seventh_crystal_and_exterior'] and prior['region']=='pal' and prior['rom_sha256']==digest
source=read(ROOT/'input/original.sms');assert sha(source)=='852e068e331dbfb01b9c38a62eecf81ce5b9f0f1bd10fff497117bd885c716c9'
assert source[0x3234e+0x1c9*8]==0x7a and source[0x320ea+(0x7a-0x20)*4]==50
snapshot=project/'validation/palc0046-d8-entry-sources/d8-entry-and-intermediate'
for n,h in load(snapshot/'source_index.json').items():assert sha(read(snapshot/n))==h and sha(read(project/'tools'/n))==h
read(snapshot.parent/'commands.jsonl')
previous=ROOT/prior['current_campaign_trace'];pc=load(previous/'capture.json');pa,pw=recording(previous,pc)
assert sha(read(previous/f'ram_{pc["frames"]:05d}.bin'))==prior['final_ram_sha256']
sy=symbols(project/'megadrive/out/release/symbol.txt')
specs=[('natural-dungeon-route','md-pal-palc0046-d8-paid3c-route01','route'),('natural-service-route','md-palc0046-d8-paid3c-service01','payment'),('natural-dungeon-route','md-pal-palc0046-d8-entry01','entry'),('natural-dungeon-combat','md-pal-palc0046-d8-mini-ready01','ready'),('natural-dungeon-combat','md-auto-palc0046-d8-guard-release01','release'),('natural-dungeon-combat','md-pal-palc0046-d8-midboss01','boss')]
if prior['stages'][-1]['health']<prior['stages'][-1]['max_health']:specs[:0]=[('natural-dungeon-route','md-pal-palc0046-d8-healer-route01','route'),('natural-service-route','md-palc0046-d8-heal01','healing')]
stream=load(project/'validation/palc0046-d8-entry-cold-stream01'/('checkpoints.json' if options.prefix_only else 'completed.json'))
assert stream['rom_sha256']==digest and stream['cold_boot_count']==1 and all(c['whole_ram_png_exact'] for c in stream['checkpoints'])
if options.prefix_only:
    assert 0<len(stream['checkpoints'])<=len(specs);specs=specs[:len(stream['checkpoints'])]
else:assert stream['passed'] and len(stream['checkpoints'])==len(specs)
stages=[];transactions=[];release=None;first=None;fight=None
for family,name,kind in specs:
    folder=project/'validation'/family/name;c=load(folder/'capture.json');r=load(folder/('route_report.json' if family=='natural-dungeon-route' else 'report.json'));a,w=recording(folder,c);f=c['frames']
    assert c['rom_sha256']==r['rom_sha256']==digest and c['sram_input'] is None and c['core_options']['genesis_plus_gx_region_detect']=='pal' and f>pc['frames']
    assert r['failure'] is None and not r.get('deaths',0) and not a['boss_assistance'] and not a['primary_state_imports'] and not a['health_refills']
    assert w[:len(pw)]==pw and all(addr==sy['hero_hurt'] and value in (b'\0\0',b'\0\x81') for _,addr,value in w)
    if family=='natural-dungeon-route':
        assert r['prefix_end']==pc['frames'] and previous.name in (r['recorded_combat_prefix'],r['recorded_service_prefix']) and r['reached_entrance'] and r['directional_probe_succeeded'] and not r['normal_continues'] and not r['retry_deaths']
        if kind=='entry':assert r['door_index']==8
    elif family=='natural-service-route':
        assert r['passed'] and r['source_prefix']==previous.name and not r['new_assistance_writes'] and w==pw and not r['currency_or_inventory_fixtures']
        before,after=r['first_state'],r['last_state'];transactions.append(dict(kind=kind,before=before,after=after))
        if kind=='payment':
            assert r['price']==10 and before['gold']-after['gold']==10 and after['room']==0x1a
            assert all(before[n]==after[n] for n in ('health','magic','keys','inventory_hex','crystals_hex'))
        else:
            assert r['normal_health_refill'] and before['health']<after['health']==after['max_health']==88 and after['room']==0x94 and {1,2,3}.issubset(r['observed_healer_phases'])
            assert all(before[n]==after[n] for n in ('gold','magic','keys','items','crystals'))
    else:assert r['prefix_end']==pc['frames'] and r['recorded_new_game_prefix']==previous.name and not r['rom_modifications'] and not r['sram_checkpoint_injection']
    proof=folder.with_name(name+f'-assisted-fixed-replay-{f}');pr=load(proof/'replay_report.json')
    assert pr['passed'] and pr['rom_sha256']==digest and pr['whole_ram_bytes']==65536 and pr['final_png_exact'] and not pr['feedback_reads'] and pr['shared_cold_stream']=='validation/palc0046-d8-entry-cold-stream01'
    for n,h in pr['evidence'].items():assert sha(read(folder/n))==h
    for stem,ext in [('ram','bin'),('frame','png')]:assert read(folder/f'{stem}_{f:05d}.{ext}')==read(proof/f'{stem}_{f:05d}.{ext}')
    raw=read(folder/f'ram_{f:05d}.bin');data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
    assert data('game_save_state',592)[0x1f:0x28]==bytes([128]*7+[0]*2) and data('hero_items',17)[16]==1
    assert word('game_state')==12 and word('hero_health')>0 and word('hero_max_health')==88 and not word('sound_unhandled_command')
    if kind=='ready':assert r['room_cleared'] and word('room_id')==0x1ca
    if kind=='release':
        assert word('room_id')==0x1ca and word('hero_hurt')==0 and r['closed_before_room']==0x1c9 and w==pw+[(f,sy['hero_hurt'],b'\0\0')];release=f
    if kind=='boss':
        first=r['first_intermediate_combat'];assert first['room']==0x1c9 and first['hurt']==0 and first['health']>0 and first['actors']==[dict(slot=0,kind=0x7a,hp=50)] and first['frame']>release
        assert r['room_cleared'] and not r['last_actors'] and w==pw and not r['new_assistance_writes'] and r['guard_release_frame']==release and r['extension_guard_checks_through_frame']==f and pr['live_boss_guard_check']
        assert r['full_ram_prediction_matches']==r['verified_persistent_prediction_windows']>0 and not r['stack_only_difference_windows'] and r['secondary_video_suppressed'] and not r['primary_video_suppressed'];fight=r
    stages.append(dict(trace=folder.relative_to(ROOT).as_posix(),frame=f,kind=kind,room=word('room_id'),health=word('hero_health'),max_health=word('hero_max_health'),magic=word('hero_magic'),gold=word('hero_gold'),keys=word('hero_keys'),whole_ram_png_exact=True))
    read(folder/'controls.json');read(folder/'assistance.json');previous,pc,pa,pw=folder,c,a,w
assert [(c['trace'],c['frames']) for c in stream['checkpoints']]==[(Path(c['trace']).relative_to(project.relative_to(ROOT)/'validation').as_posix(),c['frame']) for c in stages]
if options.prefix_only:
    print('Read-only D8 entry prefix audit passed:',len(stages),'stages; last',stages[-1],flush=True);raise SystemExit(0)
out=ROOT/'analysis/palc0046-d8-midboss'
r=dict(passed=True,candidate='c0046',region='pal',rom_sha256=digest,stages=stages,current_campaign_trace=stages[-1]['trace'],campaign_frames=stages[-1]['frame'],final_ram_sha256=sha(read(previous/f'ram_{stages[-1]["frame"]:05d}.bin')),paid_horns=10,transactions=transactions,intermediate_defeated=True,intermediate_assistance=False,guard_release_frame=release,first_combat=first,first_damage=fight['first_extension_damage'],prediction_windows=fight['full_ram_prediction_matches'],full_candidate_campaign_verified=False,eighth_crystal_validated=False,archive_manifest=(out/'manifest.json').relative_to(ROOT).as_posix(),scope='Actual PAL continuation after seven crystals, optional real healer, ten-piece payment, D8 entry and source-strength intermediate. Independent cold whole-RAM/PNG endpoints, no resource/actor/progression/SRAM imports, no boss assistance. Eighth crystal, main boss and global SMS fidelity remain open.')
freeze(ROOT,out,paths,r,[work]);(ROOT/'analysis/palc0046_d8_midboss_report.json').write_text(json.dumps(r,indent=2)+'\n')
print('PAL D8 payment, entrance and unassisted intermediate audited',flush=True)
