"""Audit the full PAL D6 route, real Ice Bell, unassisted boss and exterior return."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,'tools')
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated

work=Path(__file__).resolve().parent;project=work/'isolated/project'
parser=argparse.ArgumentParser();parser.add_argument('--prefix-only',action='store_true');options=parser.parse_args()
paths={Path(__file__).resolve(),work/'prepare_pal_d6.py',work/'after_pal_d6.py'}
def read(p):paths.add(p);return p.read_bytes()
def load(p):return json.loads(read(p))

digest=sha((project/'gaw-megadrive.bin').read_bytes())
assert digest=='9e747d38e0c6fb2d69b7c1aa8c2b296a61e8b6af41171d14e543ed9a6cb49cf5'
prior=load(ROOT/'analysis/palc0046_d5_report.json')
assert prior['passed'] and prior['region']=='pal' and prior['rom_sha256']==digest and prior['actual_fifth_crystal_and_exterior']
snapshot=project/'validation/palc0046-d6-sources02'
for n,h in load(snapshot/'source_index.json').items():
    assert sha(read(snapshot/Path(n).relative_to('tools')))==h and sha(read(project/n))==h
for n,h in load(snapshot/'native_source_index.json').items():assert sha(read(project/'megadrive/src'/n))==h
read(snapshot/'commands.jsonl')
diagnostic=load(project/'validation/palc0046-d6-sources/before-emulation-guard.json')
assert not diagnostic['passed'] and not diagnostic['emulation_started']
recipes=load(snapshot/'historical_recipes.json');executed=load(snapshot/'executed_recipes.json')
assert len(recipes)==15 and 0<len(executed)<=15 and recipes==load(project/'tools/recipes/d6-route-v0312.json')
if not options.prefix_only:assert len(executed)==15
sy=symbols(project/'megadrive/out/release/symbol.txt');source=read(ROOT/'input/original.sms')
assert source[0x3234e+0x115*8]==0x64 and source[0x320ea+(0x64-0x20)*4]==60
specs=[('natural-service-route','md-palc0046-d6-axe-equip01','equip',None),('natural-dungeon-route','md-pal-palc0046-d6-entry01','entry',None)]
for recipe in recipes:
    args=recipe['arguments'];name=args[args.index('--trial')+1].replace('v0312','palc0046')
    specs.append(('natural-dungeon-combat','md-pal-'+name,recipe['kind'],recipe))
specs.extend([('natural-dungeon-combat','md-auto-palc0046-d6-release01','release',None),('natural-dungeon-combat','md-pal-palc0046-d6-boss01','boss',None),('natural-dungeon-combat','md-pal-palc0046-d6-exit01','exit',None)])
if options.prefix_only:
    checkpoint=load(project/'validation/palc0046-d6-cold-stream01/checkpoints.json')
    assert checkpoint['rom_sha256']==digest and checkpoint['cold_boot_count']==1 and 0<len(checkpoint['checkpoints'])<=20
    specs=specs[:len(checkpoint['checkpoints'])]
previous=ROOT/prior['current_campaign_trace'];pc=load(previous/'capture.json');pa,pw=recording(previous,pc)
stages=[];release=None;fixed=None;fight=None;recipe_number=0;bell=False
for family,name,kind,recipe in specs:
    folder=project/'validation'/family/name;c=load(folder/'capture.json');r=load(folder/('route_report.json' if family=='natural-dungeon-route' else 'report.json'));a,w=recording(folder,c);f=c['frames']
    assert c['rom_sha256']==r['rom_sha256']==digest and c['sram_input'] is None and c['core_options']['genesis_plus_gx_region_detect']=='pal'
    assert f>pc['frames'] and r['failure'] is None and not r.get('deaths',0)
    assert not a['primary_state_imports'] and not a['boss_assistance'] and not a['health_refills']
    assert w[:len(pw)]==pw and all(addr==sy['hero_hurt'] and value in (b'\0\0',b'\0\x81') for _,addr,value in w)
    if kind=='equip':
        assert r['source_trace']==previous.parent.name+'/'+previous.name and r['passed'] and r['selected_slot']==1 and r['seen_menu'] and not r['new_assistance_writes'] and w==pw
        assert all(r['first_state'][n]==r['last_state'][n] for n in ('room','max_health','basic','axe','gold','keys','magic','items','crystals'))
    else:
        assert a['boss_room']==0x115 and r['prefix_end']==pc['frames']
        if kind=='entry':
            assert r['recorded_service_prefix']==previous.name and r['reached_entrance'] and r['directional_probe_succeeded'] and r['door_index']==6
        else:
            assert r['recorded_new_game_prefix']==previous.name and not r['rom_modifications'] and not r['sram_checkpoint_injection']
    if recipe is not None:
        tool,*args=recipe['arguments'];assert tool=='tools/assisted_boss_route.py'
        args=[*args,'--pal','--wake-sentinels'];args[args.index('--trial')+1]=name.removeprefix('md-pal-')
        flag='--prefix' if previous.parent.name=='natural-dungeon-route' else '--continuation'
        args[args.index(flag)+1]=previous.name;args[args.index('--frames')+1]=str(pc['frames']+18000)
        assert executed[recipe_number]==dict(source_recipe=recipe['source_recipe'],kind=kind,arguments=[tool,*args]);recipe_number+=1
        required={'clear':'room_cleared','key':'new_key_verified','contact':'contact_route_passed','earth':'earth_route_passed','item':'room_cleared'}[kind];assert r[required]
        if kind=='earth':
            action_only='--earth-action-only' in args
            assert r['earth_action_only_requested']==action_only and r['earth_cell_cleared'] and not r['earth_state_writes'] and r['earth_passage_room']==int(args[args.index('--earth-room')+1],0) and r['earth_cell']==int(args[args.index('--earth-cell')+1],0)
            before,opened=r['earth_before'],r['earth_opened']
            assert before['cell']==0x0b and opened['cell']!=0x0b and opened['magic']<before['magic']
            if action_only:assert not r['earth_passage_opened'] and not r['earth_passage_traversed'] and int(args[args.index('--passage-destination')+1],0)==r['earth_passage_room']
            else:assert r['earth_passage_opened'] and r['earth_passage_traversed'] and opened['flags']&4
        if kind=='contact':assert not r['contact_state_writes'] and r['contact_room']==int(args[args.index('--contact-room')+1],0) and r['contact_destination']==int(args[args.index('--contact-destination')+1],0)
        if kind=='item':
            # This recipe collects the reward with the ordinary combat driver.
            # Its schema differs from the dedicated item-acquisition wrapper.
            assert r['room_cleared'] and r['collect_item_requested']==10 and r['collect_item_target_value']==1 and r['last_state']['item_value']==1
            assert r['driver_sha256']==sha(read(project/'tools/natural_dungeon_combat.py'))
            prior_raw=read(previous/f'ram_{pc["frames"]:05d}.bin');assert prior_raw[(sy['hero_items']+10)^1]==0
            bell=True
    proof=folder.with_name(name+f'-assisted-fixed-replay-{f}');pr=load(proof/'replay_report.json')
    assert pr['passed'] and pr['rom_sha256']==digest and pr['whole_ram_bytes']==65536 and pr['final_png_exact'] and not pr['feedback_reads'] and pr['shared_cold_stream']=='validation/palc0046-d6-cold-stream01'
    for n,h in pr['evidence'].items():assert sha(read(folder/n))==h
    for stem,ext in [('ram','bin'),('frame','png')]:assert read(folder/f'{stem}_{f:05d}.{ext}')==read(proof/f'{stem}_{f:05d}.{ext}')
    raw=read(folder/f'ram_{f:05d}.bin');data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
    items=data('hero_items',17);save=data('game_save_state',592)
    assert word('game_state')==12 and word('hero_health')>0 and not word('sound_unhandled_command') and word('hero_selected_item')==1
    assert items[0]==2 and items[1]==items[4]==items[5]==items[12]==items[13]==items[14]==1 and not items[8]
    if bell:assert items[10]==1
    if kind=='release':
        release=f;fixed=w;assert word('hero_hurt')==0 and word('room_id')==0x125 and a['closed_before_room']==0x115 and w==pw+[(f,sy['hero_hurt'],b'\0\0')]
    if kind in ('boss','exit'):
        assert w==fixed and not r['new_assistance_writes'] and r['unassisted_extension'] and r['guard_release_frame']==release and r['extension_guard_checks_through_frame']==f and pr['live_boss_guard_check']
        assert r['unassisted_controller_sha256']==sha(read(project/'tools/unassisted_dungeon_continuation.py'))
        assert save[0x1f:0x28]==bytes([128]*6+[0]*3) and word('hero_max_health')==80
        assert r.get('full_ram_prediction_matches',0)==r.get('verified_persistent_prediction_windows',0) and not r.get('stack_only_difference_windows',0)
    else:assert save[0x1f:0x28]==bytes([128]*5+[0]*4) and word('hero_max_health')==72
    if kind=='boss':
        first=r['first_intermediate_combat'];assert first['room']==0x115 and first['frame']>release and first['health']>0 and first['hurt']==0 and any(e['kind']==0x64 and e['hp']==60 for e in first['actors'])
        assert r['room_cleared'] and r['collect_gem_requested'] and not word('item_reward_active') and r['full_ram_prediction_matches']>0 and r['short_stance_candidates'] and r['arrival_checked_on_every_entry']
        assert r['stance_controller_sha256']==sha(read(project/'tools/unassisted_stance_prediction.py')) and r['arrival_controller_sha256']==sha(read(project/'tools/unassisted_arrival_prediction.py'))
        fight=dict(first=first,release_frame=release,prediction_windows=r['full_ram_prediction_matches'],first_damage=r['first_extension_damage'])
    if kind=='exit':assert r['full_dungeon_cleared'] and r['dungeon_exit_verified'] and word('room_id')==0x8b and not word('world_dungeon_number') and 0x187 in r['deferred_puzzles']
    stages.append(dict(trace=folder.relative_to(ROOT).as_posix(),frame=f,kind=kind,room=word('room_id'),health=word('hero_health'),max_health=word('hero_max_health'),magic=word('hero_magic'),keys=word('hero_keys'),gold=word('hero_gold'),whole_ram_png_exact=True))
    read(folder/'controls.json');read(folder/'assistance.json');previous,pc,pa,pw=folder,c,a,w
if options.prefix_only:
    assert [(c['trace'],c['frames']) for c in checkpoint['checkpoints']]==[(Path(c['trace']).relative_to(project.relative_to(ROOT)/'validation').as_posix(),c['frame']) for c in stages]
    print('Read-only PAL D6 prefix audit passed:',len(stages),'stages; last',stages[-1],flush=True)
    raise SystemExit(0)
sms=data('sms_vram',16384);vram=read(previous/f'vram_{f:05d}.bin');regs=read(previous/f'vdp_regs_{f:05d}.bin');base=(regs[2]&56)<<10;width=[32,64,32,128][regs[16]&3]
for n in range(128):
    at=base+((n//32+22)*width+n%32)*2;assert int.from_bytes(vram[at:at+2],'little')==translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2],'little'))
s=load(project/'validation/palc0046-d6-cold-stream01/completed.json')
assert s['passed'] and s['rom_sha256']==digest and s['cold_boot_count']==1 and len(s['checkpoints'])==len(specs)==20 and all(c['whole_ram_png_exact'] for c in s['checkpoints'])
assert [(c['trace'],c['frames']) for c in s['checkpoints']]==[(Path(c['trace']).relative_to(project.relative_to(ROOT)/'validation').as_posix(),c['frame']) for c in stages]
out=ROOT/'analysis/palc0046-d6'
r=dict(passed=True,candidate='c0046',region='pal',rom_sha256=digest,stages=stages,current_campaign_trace=stages[-1]['trace'],campaign_frames=f,final_ram_sha256=sha(read(previous/f'ram_{f:05d}.bin')),actual_sixth_crystal_and_exterior=True,ice_bell_owned=True,fight=fight,physical_hud_words_exact=128,full_candidate_campaign_verified=False,pre_emulation_reader_guard_corrected=True,archive_manifest=(out/'manifest.json').relative_to(ROOT).as_posix(),scope='Actual PAL D6 continuation, normal weapon selection,15 source-derived recipes with real keys, Earth/contact mechanisms and Ice Bell, source-strength boss and exterior8B return. Twenty independent cold RAM/PNG checkpoints. Approach protection removed before boss; no later aid, no resource, actor, progression or initial SRAM import. Global SMS fidelity remains open.')
freeze(ROOT,out,paths,r,[work]);(ROOT/'analysis/palc0046_d6_report.json').write_text(json.dumps(r,indent=2)+'\n')
print('PAL sixth crystal, Ice Bell and exterior return audited and archived',flush=True)
