"""Audit the real PAL50-piece gift,50-piece Earth purchase and D4 entry."""
import json,sys
from pathlib import Path
sys.path.insert(0,'tools')
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated
work=Path(__file__).resolve().parent;project=work/'isolated/project';paths={Path(__file__).resolve(),work/'prepare_pal_earth.py'}
def read(p):paths.add(p);return p.read_bytes()
def load(p):return json.loads(read(p))
digest=sha((project/'gaw-megadrive.bin').read_bytes());assert digest=='9e747d38e0c6fb2d69b7c1aa8c2b296a61e8b6af41171d14e543ed9a6cb49cf5'
prior=load(ROOT/'analysis/palc0046_d3_report.json');assert prior['passed'] and prior['region']=='pal' and prior['rom_sha256']==digest and prior['actual_third_crystal_and_exterior']
snapshot=project/'validation/palc0046-earth-sources'
for n,h in load(snapshot/'source_index.json').items():assert sha(read(snapshot/Path(n).name))==h and sha(read(project/n))==h
sy=symbols(project/'megadrive/out/release/symbol.txt');previous=ROOT/prior['current_campaign_trace'];pc=load(previous/'capture.json');pa,pw=recording(previous,pc)
specs=[('natural-dungeon-route','md-pal-palc0046-gold-entry01','gift-route'),('natural-service-route','md-palc0046-gold50-01','gift'),('natural-dungeon-route','md-pal-palc0046-earth-entry01','earth-route'),('natural-service-route','md-palc0046-earth-learn01','earth'),('natural-dungeon-route','md-pal-palc0046-d4-entry01','entry')]
stages=[];transactions={}
for family,name,kind in specs:
    folder=project/'validation'/family/name;c=load(folder/'capture.json');r=load(folder/('route_report.json' if family=='natural-dungeon-route' else 'report.json'));a,w=recording(folder,c);f=c['frames']
    assert c['rom_sha256']==r['rom_sha256']==digest and c['sram_input'] is None and c['core_options']['genesis_plus_gx_region_detect']=='pal' and f>pc['frames'] and r['failure'] is None and not r.get('deaths',0)
    assert not a['primary_state_imports'] and not a['health_refills'] and not a['boss_assistance'] and a['first_boss_entry'] is None and a['boss_room']==0x180
    assert all(addr==sy['hero_hurt'] and value in (b'\0\0',b'\0\x81') for _,addr,value in w) and w[:len(pw)]==pw
    if family=='natural-service-route':
        assert r['source_prefix']==previous.name and r['passed'] and not r['new_assistance_writes'] and w==pw
        before,after=r['first_state'],r['last_state'];transactions[kind]=dict(before=before,after=after)
        if kind=='gift':assert r['kind']=='gold' and after['gold']-before['gold']==50 and after['outside_flags']&2
        else:assert r['kind']=='teacher' and r['teacher']==1 and r['expected_level']==1 and before['level']==0 and after['level']==1 and before['gold']-after['gold']==50 and before['max_magic']==24 and after['max_magic']==after['magic']==48
    else:
        assert r['prefix_end']==pc['frames'] and previous.name in (r.get('recorded_combat_prefix'),r.get('recorded_service_prefix')) and r['reached_entrance'] and r['directional_probe_succeeded']
        if kind=='earth-route':assert r['required_chop_verified']
    proof=folder.with_name(name+f'-assisted-fixed-replay-{f}');pr=load(proof/'replay_report.json')
    assert pr['passed'] and pr['rom_sha256']==digest and pr['whole_ram_bytes']==65536 and pr['final_png_exact'] and not pr['feedback_reads']
    for n,h in pr['evidence'].items():assert sha(read(folder/n))==h
    for stem,ext in [('ram','bin'),('frame','png')]:assert read(folder/f'{stem}_{f:05d}.{ext}')==read(proof/f'{stem}_{f:05d}.{ext}')
    raw=read(folder/f'ram_{f:05d}.bin');data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
    assert word('game_state')==12 and word('hero_health')>0 and word('hero_max_health')==56 and not word('sound_unhandled_command')
    assert data('game_save_state',592)[0x1f:0x28]==bytes([128]*3+[0]*6) and data('hero_items',17)[13]==1
    if kind in ('earth','entry'):assert data('hero_items',17)[5]==1 and word('hero_max_magic')==48
    if kind=='entry':assert word('room_id')==0x1f0 and word('world_dungeon_number')==4
    stages.append(dict(trace=folder.relative_to(ROOT).as_posix(),frame=f,kind=kind,room=word('room_id'),health=word('hero_health'),gold=word('hero_gold'),magic=word('hero_magic'),whole_ram_png_exact=True))
    read(folder/'assistance.json');read(folder/'controls.json');previous,pc,pa,pw=folder,c,a,w
sms=data('sms_vram',16384);vram=read(previous/f'vram_{f:05d}.bin');regs=read(previous/f'vdp_regs_{f:05d}.bin');base=(regs[2]&56)<<10;width=[32,64,32,128][regs[16]&3]
for n in range(128):
    at=base+((n//32+22)*width+n%32)*2;assert int.from_bytes(vram[at:at+2],'little')==translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2],'little'))
stream=load(project/'validation/palc0046-earth-cold-stream01/completed.json');assert stream['passed'] and stream['cold_boot_count']==1 and stream['rom_sha256']==digest and len(stream['checkpoints'])==5 and all(c['whole_ram_png_exact'] for c in stream['checkpoints'])
assert [c['frames'] for c in stream['checkpoints']]==[c['frame'] for c in stages]
out=ROOT/'analysis/palc0046-earth'
r=dict(passed=True,candidate='c0046',region='pal',rom_sha256=digest,stages=stages,current_campaign_trace=stages[-1]['trace'],campaign_frames=stages[-1]['frame'],real_gold_gift_and_earth_purchase=True,fourth_dungeon_entered=True,transactions=transactions,physical_hud_words_exact=128,full_candidate_campaign_verified=False,archive_manifest=(out/'manifest.json').relative_to(ROOT).as_posix(),scope='Actual PAL continuation after three crystals; real50-piece gift and Earth price, required axe chop, five cold RAM/PNG proofs and physical HUD publication. No resource, actor, progression or SRAM import; fourth crystal and global SMS timing remain open.')
freeze(ROOT,out,paths,r,[work]);(ROOT/'analysis/palc0046_earth_report.json').write_text(json.dumps(r,indent=2)+'\n')
print('PAL real gold gift, Earth purchase and D4 entry audited and archived',flush=True)
