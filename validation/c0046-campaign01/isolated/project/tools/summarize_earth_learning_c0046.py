"""Audit genuine gold gift and Earth purchase on the current cold v317 chain."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from assisted_prefix import recording,prefix_writes
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated

def main():
    refs={};stages=[];writes=[];sy=symbols(ROOT/'megadrive/out/release/symbol.txt');digest=sha((ROOT/'gaw-megadrive.bin').read_bytes())
    def read(p):
        raw=p.read_bytes();refs[p.relative_to(ROOT).as_posix()]=sha(raw);return raw
    prior=json.loads(read(ROOT/'analysis/c0046_d3_report.json'));assert prior['passed'] and prior['rom_sha256']==digest and prior['actual_third_crystal_and_exterior']
    assert digest=='9e747d38e0c6fb2d69b7c1aa8c2b296a61e8b6af41171d14e543ed9a6cb49cf5'
    cases=[('natural-dungeon-route','md-c0046-gold-entry01','route'),('natural-service-route','md-c0046-gold50-01','gold'),('natural-dungeon-route','md-c0046-earth-entry01','route'),('natural-service-route','md-c0046-earth-learn01','teacher')]
    for family,name,kind in cases:
        folder=ROOT/'validation'/family/name;c=json.loads(read(folder/'capture.json'));r=json.loads(read(folder/('route_report.json'if kind=='route'else'report.json')));a,w=recording(folder,c);read(folder/'assistance.json');end=c['frames'];cold=folder.with_name(folder.name+'-assisted-fixed-replay-'+str(end));p=json.loads(read(cold/'replay_report.json'))
        assert c['rom_sha256']==digest and c['sram_input']is None and r['failure']is None and p['passed']and p['whole_ram_bytes']==65536 and p['final_png_exact']and not p['feedback_reads']
        assert prefix_writes(folder,c,True)==w and all(addr==sy['hero_hurt']for _,addr,_ in w)and len(a['episodes'])==4 and a['boss_room']==0x180 and a['first_boss_entry']is None and not a['health_refills']and not a['primary_state_imports']
        for n,h in p['evidence'].items():assert sha(read(folder/n))==h
        for stem,ext in [('ram','bin'),('frame','png')]:assert read(folder/f'{stem}_{end:05d}.{ext}')==read(cold/f'{stem}_{end:05d}.{ext}')
        raw=read(folder/f'ram_{end:05d}.bin');data=lambda n,k:bytes(raw[(sy[n]+i)^1]for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
        assert data('game_save_state',592)[0x1f:0x28]==bytes([128]*3+[0]*6)and data('hero_items',17)[8]==data('hero_items',17)[13]==1 and word('hero_health')>0 and word('hero_max_health')==56 and not word('sound_unhandled_command')
        if kind=='route':assert r['reached_entrance']and r['directional_probe_succeeded']
        else:
            assert r['passed']and r['new_assistance_writes']==0
            sms=data('sms_vram',16384);v=read(folder/f'vram_{end:05d}.bin');regs=read(folder/f'vdp_regs_{end:05d}.bin');base=(regs[2]&56)<<10;width=[32,64,32,128][regs[16]&3]
            for n in range(128):
                off=base+((n//32+22)*width+n%32)*2;assert int.from_bytes(v[off:off+2],'little')==translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2],'little'))
        if kind=='gold':assert r['last_state']['gold']-r['first_state']['gold']==50
        if kind=='teacher':assert r['first_state']['gold']-r['last_state']['gold']==50 and r['first_state']['level']==0 and r['last_state']['level']==1 and word('hero_magic')==word('hero_max_magic')==48 and data('hero_items',17)[5]==1
        writes.append(w);stages.append(dict(trace=folder.relative_to(ROOT).as_posix(),kind=kind,frames=end,health=word('hero_health'),gold=word('hero_gold'),magic=word('hero_magic'),max_magic=word('hero_max_magic'),earth_level=data('hero_items',17)[5],whole_ram_png_exact=True))
    assert writes[0]==writes[1]and writes[2]==writes[3]
    result=dict(passed=True,md_sha256=digest,stages=stages,real_gold_gift=50,real_earth_price=50,earth_level=1,magic_capacity=48,resource_writes=0,primary_state_imports=0,new_service_assistance_writes=0,physical_hud_words_each_service=128,driver_sha256=sha(read(ROOT/'tools/summarize_earth_learning_c0046.py')),full_game_validated=False,evidence=refs,limits=['Same cold New Game three-crystal chain;approaches retain authorized hurt-counter writes. No resource/progression/SRAM imports.','Four checkpoints and actual teacher transaction;D4 combat/later progression,global R/IRQ and broader fidelity remain open.'])
    prefix=ROOT.relative_to(ROOT.parents[3]).as_posix()+'/'
    for stage in result['stages']:stage['trace']=prefix+stage['trace']
    result['evidence']={(k if k.startswith('analysis/') else prefix+k):v for k,v in refs.items()}
    (ROOT/'analysis/earth_learning_c0046_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print('Real gold gift and Earth purchase:four exact cold checkpoints')

if __name__=='__main__':main()
