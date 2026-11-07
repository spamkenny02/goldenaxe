"""Audit the real PAL oil-to-Fire exchange, Long Sword gift and D5 entry."""
import json,sys
from pathlib import Path
sys.path.insert(0,'tools')
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated
work=Path(__file__).resolve().parent;project=work/'isolated/project';paths={Path(__file__).resolve(),work/'prepare_pal_fire_sword.py'}
def read(p):paths.add(p);return p.read_bytes()
def load(p):return json.loads(read(p))
digest=sha((project/'gaw-megadrive.bin').read_bytes());assert digest=='9e747d38e0c6fb2d69b7c1aa8c2b296a61e8b6af41171d14e543ed9a6cb49cf5'
prior=load(ROOT/'analysis/palc0046_d4_report.json');assert prior['passed'] and prior['region']=='pal' and prior['rom_sha256']==digest and prior['actual_fourth_crystal_and_exterior']
snapshot=project/'validation/palc0046-fire-sword-sources'
for n,h in load(snapshot/'source_index.json').items():assert sha(read(snapshot/Path(n).name))==h and sha(read(project/n))==h
sy=symbols(project/'megadrive/out/release/symbol.txt');previous=ROOT/prior['current_campaign_trace'];pc=load(previous/'capture.json');pa,pw=recording(previous,pc)
specs=[('natural-dungeon-route','md-pal-palc0046-fire-entry01','intro-route'),('natural-service-route','md-palc0046-fire-intro01','intro'),('natural-dungeon-route','md-pal-palc0046-fire-entry02','fire-route'),('natural-service-route','md-palc0046-fire-learn01','fire'),('natural-dungeon-route','md-pal-palc0046-sword2-entry01','sword-route'),('natural-service-route','md-palc0046-sword2-gift01','sword'),('natural-dungeon-route','md-pal-palc0046-d5-entry01','entry')]
stages=[];transactions={}
for family,name,kind in specs:
    folder=project/'validation'/family/name;c=load(folder/'capture.json');r=load(folder/('route_report.json' if family=='natural-dungeon-route' else 'report.json'));a,w=recording(folder,c);f=c['frames']
    assert c['rom_sha256']==r['rom_sha256']==digest and c['sram_input'] is None and c['core_options']['genesis_plus_gx_region_detect']=='pal' and f>pc['frames'] and r['failure'] is None and not r.get('deaths',0)
    assert not a['primary_state_imports'] and not a['health_refills'] and not a['boss_assistance'] and a['first_boss_entry'] is None and a['boss_room']==0x163
    assert all(addr==sy['hero_hurt'] and value in (b'\0\0',b'\0\x81') for _,addr,value in w) and w[:len(pw)]==pw
    if family=='natural-service-route':
        assert r['source_prefix']==previous.name and r['passed'] and not r['new_assistance_writes'] and w==pw
        before,after=r['first_state'],r['last_state'];transactions[kind]=dict(before=before,after=after)
        if kind=='intro':assert r['kind']=='teacher' and r['teacher']==0 and before['level']==after['level']==0 and before['intro']==0 and after['intro']==1
        elif kind=='fire':assert r['kind']=='teacher' and r['teacher']==0 and before['level']==0 and after['level']==1 and before['gold']==after['gold'] and before['max_magic']==48 and after['max_magic']==after['magic']==72
        else:assert before['basic']==1 and after['basic']==2
    else:
        assert r['prefix_end']==pc['frames'] and previous.name in (r.get('recorded_combat_prefix'),r.get('recorded_service_prefix')) and r['reached_entrance'] and r['directional_probe_succeeded']
    proof=folder.with_name(name+f'-assisted-fixed-replay-{f}');pr=load(proof/'replay_report.json')
    assert pr['passed'] and pr['rom_sha256']==digest and pr['whole_ram_bytes']==65536 and pr['final_png_exact'] and not pr['feedback_reads']
    for n,h in pr['evidence'].items():assert sha(read(folder/n))==h
    for stem,ext in [('ram','bin'),('frame','png')]:assert read(folder/f'{stem}_{f:05d}.{ext}')==read(proof/f'{stem}_{f:05d}.{ext}')
    raw=read(folder/f'ram_{f:05d}.bin');data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
    assert word('game_state')==12 and word('hero_health')>0 and word('hero_max_health')==64 and not word('sound_unhandled_command')
    assert data('game_save_state',592)[0x1f:0x28]==bytes([128]*4+[0]*5) and data('hero_items',17)[13]==1
    if kind in ('fire','sword-route','sword','entry'):assert data('hero_items',17)[4]==1 and data('hero_items',17)[8]==0 and word('hero_max_magic')==72
    if kind in ('intro-route','intro','fire-route'):assert data('hero_items',17)[8]==1 and data('hero_items',17)[4]==0
    if kind in ('sword','entry'):assert data('hero_items',17)[0]==2
    if kind=='entry':assert word('room_id')==0x186 and word('world_dungeon_number')==5
    stages.append(dict(trace=folder.relative_to(ROOT).as_posix(),frame=f,kind=kind,room=word('room_id'),health=word('hero_health'),gold=word('hero_gold'),magic=word('hero_magic'),whole_ram_png_exact=True))
    read(folder/'assistance.json');read(folder/'controls.json');previous,pc,pa,pw=folder,c,a,w
sms=data('sms_vram',16384);vram=read(previous/f'vram_{f:05d}.bin');regs=read(previous/f'vdp_regs_{f:05d}.bin');base=(regs[2]&56)<<10;width=[32,64,32,128][regs[16]&3]
for n in range(128):
    at=base+((n//32+22)*width+n%32)*2;assert int.from_bytes(vram[at:at+2],'little')==translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2],'little'))
stream=load(project/'validation/palc0046-fire-sword-cold-stream01/completed.json');assert stream['passed'] and stream['cold_boot_count']==1 and stream['rom_sha256']==digest and len(stream['checkpoints'])==7 and all(c['whole_ram_png_exact'] for c in stream['checkpoints'])
assert [c['frames'] for c in stream['checkpoints']]==[c['frame'] for c in stages]
out=ROOT/'analysis/palc0046-fire-sword'
r=dict(passed=True,candidate='c0046',region='pal',rom_sha256=digest,stages=stages,current_campaign_trace=stages[-1]['trace'],campaign_frames=stages[-1]['frame'],real_oil_trade_and_long_sword=True,fifth_dungeon_entered=True,transactions=transactions,physical_hud_words_exact=128,full_candidate_campaign_verified=False,archive_manifest=(out/'manifest.json').relative_to(ROOT).as_posix(),scope='Actual PAL continuation after four crystals; actual oil consumed for Fire, Long Sword gift, seven cold RAM/PNG proofs and physical HUD publication. No resource, actor, progression or SRAM import; fifth crystal and global SMS fidelity remain open.')
freeze(ROOT,out,paths,r,[work]);(ROOT/'analysis/palc0046_fire_sword_report.json').write_text(json.dumps(r,indent=2)+'\n')
print('PAL Fire, Long Sword and D5 entry audited and archived',flush=True)
