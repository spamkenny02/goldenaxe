"""Audit real PAL D7 funding, key purchase, entrance and two Earth preparations."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,'tools')
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols

parser=argparse.ArgumentParser();parser.add_argument('--prefix-only',action='store_true');options=parser.parse_args()
work=Path(__file__).resolve().parent;project=work/'isolated/project'
paths={Path(__file__).resolve(),work/'prepare_pal_d7.py'}
def read(p):paths.add(p);return p.read_bytes()
def load(p):return json.loads(read(p))

digest=sha((project/'gaw-megadrive.bin').read_bytes())
assert digest=='9e747d38e0c6fb2d69b7c1aa8c2b296a61e8b6af41171d14e543ed9a6cb49cf5'
prior=load(ROOT/'analysis/palc0046_d6_report.json')
assert prior['passed'] and prior['actual_sixth_crystal_and_exterior'] and prior['region']=='pal' and prior['rom_sha256']==digest
snapshot=project/'validation/palc0046-d7-prep-sources'
for n,h in load(snapshot/'source_index.json').items():assert sha(read(snapshot/Path(n).name))==h and sha(read(project/n))==h
for row in read(snapshot/'commands.jsonl').splitlines():
    command=json.loads(row);assert command['sha256']==sha(read(project/'tools'/command['tool']))
previous=ROOT/prior['current_campaign_trace'];pc=load(previous/'capture.json');pa,pw=recording(previous,pc)
assert sha(read(previous/f'ram_{pc["frames"]:05d}.bin'))==prior['final_ram_sha256']
sy=symbols(project/'megadrive/out/release/symbol.txt')
kinds={'gold-route':('route',None),'gold10':('gold',10),'gold7d-route':('route',None),'gold30':('gold',30),'key-shop-route':('route',None),'buy-key':('purchase',None),'healer-route':('route',None),'heal':('heal',None),'entry':('entry',None),'key01':('key',0x1cb),'key03':('key',0x1b9),'earth01':('earth',0x36),'earth02':('earth',0x2b)}
order=list(kinds);points=load(snapshot/'verified_endpoints.json');stages=[];seen=[];transactions=[]
for point in points:
    local=Path(point['trace']);assert local.parts[0]=='validation';folder=project/local
    name=folder.name;assert name.startswith(('md-pal-palc0046-d7-01-','md-palc0046-d7-01-'))
    suffix=name.split('palc0046-d7-01-',1)[1];kind,target=kinds[suffix]
    assert suffix not in seen and (not seen or order.index(suffix)>order.index(seen[-1]));seen.append(suffix)
    r=load(folder/('route_report.json' if kind in ('route','entry') else 'report.json'));c=load(folder/'capture.json');a,w=recording(folder,c);f=c['frames']
    gate='reached_entrance' if kind in ('route','entry') else 'new_key_verified' if kind=='key' else 'earth_route_passed' if kind=='earth' else 'passed'
    assert point['gate']==gate and r[gate] and r['failure'] is None and not r.get('deaths',0)
    assert f==point['frames']>pc['frames'] and c['rom_sha256']==r['rom_sha256']==digest and c['sram_input'] is None and c['core_options']['genesis_plus_gx_region_detect']=='pal'
    assert a['boss_room']==0x1b8 and a['activation_after_frame']==prior['campaign_frames'] and a['first_boss_entry'] is None and len(a['episodes'])==7
    assert not a['primary_state_imports'] and not a['boss_assistance'] and not a['health_refills'] and w[:len(pw)]==pw
    assert all(addr==sy['hero_hurt'] and value in (b'\0\0',b'\0\x81') for _,addr,value in w)
    if kind in ('gold','purchase','heal'):
        assert r['source_prefix']==previous.name and not r['new_assistance_writes'] and w==pw
        before,after=r['first_state'],r['last_state'];transactions.append(dict(kind=kind,before=before,after=after))
        if kind=='gold':assert after['gold']-before['gold']==target and after['outside_flags']==before['outside_flags']|2 and after['room']==(0xb5 if target==10 else 0x7d)
        if kind=='purchase':assert r['outside']==0x94 and r['unit_price']==60 and r['keys_bought']==1 and before['gold']-after['gold']==60 and after['keys']==before['keys']+1 and not r['currency_or_inventory_fixtures'] and r['free_healing_completed'] and after['health']==after['max_health']==80
    else:
        assert r['prefix_end']==pc['frames']
        if kind in ('route','entry'):assert previous.name in (r.get('recorded_combat_prefix'),r.get('recorded_service_prefix')) and r['directional_probe_succeeded'] and not r['normal_continues']
        else:assert r['recorded_new_game_prefix']==previous.name and not r['rom_modifications'] and not r['sram_checkpoint_injection']
    if kind=='earth':
        assert r['earth_action_only_requested'] and r['earth_cell_cleared'] and not r['earth_passage_traversed'] and not r['earth_state_writes'] and r['earth_passage_room']==0x1b9 and r['earth_cell']==target
        assert r['earth_before']['cell']==11 and r['earth_opened']['cell']!=11 and r['earth_before']['magic']-r['earth_opened']['magic']==8
        read(folder/'earth_events.json')
    if kind=='key':assert r['new_key_verified'] and r['room_cleared'] and r['target_room']==target
    if kind=='entry':assert r['door_index']==7 and r['house_outside'] is None
    proof=folder.with_name(name+f'-assisted-fixed-replay-{f}');pr=load(proof/'replay_report.json')
    assert pr['passed'] and pr['rom_sha256']==digest and pr['whole_ram_bytes']==65536 and pr['final_png_exact'] and not pr['feedback_reads'] and pr['shared_cold_stream']=='validation/palc0046-d7-prep-cold-stream01'
    for n,h in pr['evidence'].items():assert sha(read(folder/n))==h
    for stem,ext in [('ram','bin'),('frame','png')]:assert read(folder/f'{stem}_{f:05d}.{ext}')==read(proof/f'{stem}_{f:05d}.{ext}')
    raw=read(folder/f'ram_{f:05d}.bin');data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
    items=data('hero_items',17)
    assert word('game_state')==12 and word('hero_health')>0 and word('hero_max_health')==80 and not word('sound_unhandled_command')
    assert data('game_save_state',592)[0x1f:0x28]==bytes([128]*6+[0]*3) and items[0]==2 and all(items[i]==1 for i in (1,4,5,10,12,13,14)) and not items[16]
    if kind=='entry':assert word('room_id')==0x1db and word('world_dungeon_number')==7
    if kind in ('key','earth'):assert word('room_id')==(target if kind=='key' else 0x1b9)
    stages.append(dict(trace=folder.relative_to(ROOT).as_posix(),frame=f,stage=suffix,kind=kind,room=word('room_id'),health=word('hero_health'),max_health=word('hero_max_health'),magic=word('hero_magic'),keys=word('hero_keys'),gold=word('hero_gold'),whole_ram_png_exact=True))
    read(folder/'controls.json');read(folder/'assistance.json');previous,pc,pa,pw=folder,c,a,w
stream=load(project/'validation/palc0046-d7-prep-cold-stream01'/('checkpoints.json' if options.prefix_only else 'completed.json'))
assert stream['rom_sha256']==digest and stream['cold_boot_count']==1 and all(c['whole_ram_png_exact'] for c in stream['checkpoints'])
assert [(c['trace'],c['frames']) for c in stream['checkpoints']]==[(Path(c['trace']).relative_to(project.relative_to(ROOT)/'validation').as_posix(),c['frame']) for c in stages]
if options.prefix_only:
    print('Read-only PAL D7 preparation prefix audit passed:',len(stages),'stages; last',stages[-1],flush=True);raise SystemExit(0)
assert stream['passed'] and seen[-5:]==['entry','key01','key03','earth01','earth02'] and 'buy-key' in seen
proposal=load(snapshot/'historical_proposal.json');assert sha(read(project/proposal['path']))==proposal['sha256']
out=ROOT/'analysis/palc0046-d7-preparation'
r=dict(passed=True,candidate='c0046',region='pal',rom_sha256=digest,stages=stages,current_campaign_trace=stages[-1]['trace'],campaign_frames=stages[-1]['frame'],final_ram_sha256=sha(read(previous/f'ram_{stages[-1]["frame"]:05d}.bin')),original_crystals_retained=6,transactions=transactions,key_price=60,earth_casts=2,earth_magic_spent=16,intermediate_boss_entered=False,seventh_crystal_validated=False,full_candidate_campaign_verified=False,archive_manifest=(out/'manifest.json').relative_to(ROOT).as_posix(),scope='Actual PAL D7 funding and60-piece key purchase, normal healing, entry, two keys and two preparatory Earth bricks. Each step matches independent cold whole-RAM/PNG replay. No resource, actor, progression or initial SRAM import. Approach guard remains active; intermediate/main bosses and seventh crystal are not validated here.')
freeze(ROOT,out,paths,r,[work]);(ROOT/'analysis/palc0046_d7_preparation_report.json').write_text(json.dumps(r,indent=2)+'\n')
print('PAL D7 real funding, key purchase and preparation audited and archived',flush=True)
