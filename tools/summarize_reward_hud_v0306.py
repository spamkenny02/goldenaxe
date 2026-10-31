"""Audit native HUD fix against SMS VRAM and current-ROM campaign replays."""
import json,re
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols
from audit_item_reward_visuals import sms_pixels,md_pixels
from validate_reward_hud_restore import translated


def main():
    refs={}
    def read(name):
        raw=evidence(ROOT/name);refs[name]=sha(raw);return raw
    def load(name):return json.loads(read(name))
    rom=(ROOT/'gaw-megadrive.bin').read_bytes();digest=sha(rom)
    assert len(rom)==2097152 and int.from_bytes(rom[0x18e:0x190],'big')==0x343b
    assert sum(int.from_bytes(rom[n:n+2],'big') for n in range(0x200,len(rom),2))&65535==0x343b
    assert rom==(ROOT/'gaw-title-megadrive.bin').read_bytes()==(ROOT/'versions/v0306-3a12380b/gaw-megadrive-v0306.bin').read_bytes()
    before=load('validation/v0305-before-reward-hud-fix/before.json')
    assert before['rom_sha256']==load('analysis/d4_campaign_v0305_report.json')['md_sha256']
    assert len(before['protected_sha256'])==306
    for n,h in before['protected_sha256'].items():assert sha((ROOT/n).read_bytes())==h
    changed=[n for n,h in before['production_sources'].items() if sha((ROOT/n).read_bytes())!=h]
    assert changed==['megadrive/src/main.c']
    source=read('input/original.sms');old=read('validation/v0305-before-reward-hud-fix/main.c');new=read('megadrive/src/main.c')
    marks=re.search(rb'marks\[18\]=\{([^}]+)\}',new);assert marks
    assert bytes(int(x,0) for x in marks[1].decode().split(','))==source[0x1edc:0x1eee]
    start=new.index(b'/* 1EB5..1EDB:');stop=new.index(b'/* 5C40/5C18/5BF0:',start)
    restored=new[:start]+new[stop:]
    assert restored.count(b'    prepare_hero_crystal_hud();\r\n')==2
    restored=restored.replace(b'    prepare_hero_crystal_hud();\r\n',b'')
    restored=restored.replace(b'    source_class0_video_map(sms_vram+0x3d00,md_map+20*32,32*4);\r\n',b'')
    restored=restored.replace(b'    /* 1DE2 also restores all four HUD rows after the acquisition window. */\r\n    VDP_setTileMapDataRect(BG_A,md_map,0,2,32,24,32,CPU);',b'    VDP_setTileMapDataRect(BG_A,world_new_md,0,2,32,20,32,CPU);')
    assert restored==old,'Unrelated production change'
    reports=[];window_checks=0;window_tiles=0
    for root,baseline in [('validation/reward-hud-v0305-baseline04',True),('validation/reward-hud-v0306-fixed01',False)]:
        r=load(root+'/report.json');assert r['passed'] and r['baseline_bug_expected']==baseline
        assert r['md_sha256']==(before['rom_sha256'] if baseline else digest) and r['source_sha256']==sha(source)
        assert len(r['cases'])==44 and len({x['case'] for x in r['cases']})==22
        for row in r['cases']:
            name=row['case'];frame=row['frame'];sv=read(root+'/'+name+f'-sms/vram_{frame:05d}.bin');mv=read(root+'/'+name+f'-md/vram_{frame:05d}.bin');regs=read(root+'/'+name+f'-md/vdp_regs_{frame:05d}.bin')
            base=(regs[2]&56)<<10;width=[32,64,32,128][regs[16]&3]
            words=[int.from_bytes(sv[0x3d00+n*2:0x3d02+n*2],'little') for n in range(128)]
            bad=sum(int.from_bytes(mv[base+((n//32+22)*width+n%32)*2:base+((n//32+22)*width+n%32)*2+2],'little')!=translated(w) for n,w in enumerate(words))
            assert bad==row['physical_word_mismatches'] and row['semantic_state_exact'] and row['window_closed']
            if baseline:
                assert bad>0 and row['software_word_mismatches']==(1 if name.startswith('gem') else 0)
            else:
                assert bad==row['software_word_mismatches']==0 and row['source_software_hud_exact']
                assert all(sms_pixels(sv,t)==md_pixels(mv,t+16) for t in {w&511 for w in words})
        # Verify acquisition display still matches before dismissal,independently of the post-window audit.
        if not baseline:
            for name in sorted({x['case'] for x in r['cases']}):
                frame=3500 if name.startswith('item') else 3700
                sv=read(root+'/'+name+f'-sms/vram_{frame:05d}.bin');mv=read(root+'/'+name+f'-md/vram_{frame:05d}.bin');regs=read(root+'/'+name+f'-md/vdp_regs_{frame:05d}.bin')
                base=(regs[2]&56)<<10;width=[32,64,32,128][regs[16]&3];tiles=set()
                for y in range(19,24):
                    for x in range(1,31):
                        w=int.from_bytes(sv[0x3800+y*64+x*2:0x3802+y*64+x*2],'little');at=base+((y+2)*width+x)*2
                        assert int.from_bytes(mv[at:at+2],'little')==translated(w),(name,'window',x,y)
                        tiles.add(w&511);window_checks+=1
                assert all(sms_pixels(sv,t)==md_pixels(mv,t+16) for t in tiles)
                window_tiles+=len(tiles)
        reports.append(dict(trace=root,rows=44,scenarios=22,source_hud_words=5632,baseline_bug=baseline))
    root='validation/natural-dungeon-combat/md-auto-v0306-d4-rebase01';c=load(root+'/capture.json');r=load(root+'/report.json')
    assert r['passed'] and r['failure'] is None and r['rom_sha256']==digest and r['full_dungeon_cleared']
    assert r['last_state']['room']==0x10 and r['last_state']['health']==50 and r['last_state']['max_health']==64
    assert r['last_state']['crystals']==[128]*4+[0]*5 and all(r['last_state']['items'][n]==1 for n in [5,8,12,13])
    assert not r['deaths'] and not c['sram_input']
    a,writes=recording(ROOT/root,c);read(root+'/assistance.json');sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
    assert len(a['episodes'])==4 and not a['boss_assistance'] and not a['health_refills'] and not a['primary_state_imports']
    assert all(addr==sy['hero_hurt'] for _,addr,_ in writes)
    for e in a['episodes']:
        assert e['release_write_frame']<e['first_boss_combat']['frame'] and e['first_boss_combat']['hurt']==0
    assert max(f for f,_,_ in writes)==a['episodes'][-1]['release_write_frame']
    proof=root+f"-assisted-fixed-replay-{c['frames']}";p=load(proof+'/replay_report.json')
    assert p['passed'] and p['rom_sha256']==digest and p['whole_ram_bytes']==65536 and p['final_png_exact'] and not p['feedback_reads']
    for n,h in p['evidence'].items():assert sha(read(root+'/'+n))==h
    stack='validation/stack-v0306-d4-all';s=load(stack+'/stack_report.json')
    assert s['md_sha256']==digest and s['frames']==c['frames']==86364 and s['all_instructions'] and s['read_only']
    assert s['logged_assistance_replayed'] and not s['invalid_heap_examples']
    assert s['minimum_instruction_sp']==min(x['sp'] for x in s['instruction_minima'])
    assert s['minimum_sp']==min(s['minimum_instruction_sp'],s['minimum_sampled_sp'])
    margin=s['minimum_sp']-max(x['end']+2 for x in s['heap_changes']);assert margin==442
    for stem,ext in [('ram','bin'),('frame','png')]:
        file=f'/{stem}_{c["frames"]:05d}.{ext}';assert read(root+file)==read(proof+file)==read(stack+file)
    raw=read(root+f'/ram_{c["frames"]:05d}.bin');v=read(root+f'/vram_{c["frames"]:05d}.bin');regs=read(root+f'/vdp_regs_{c["frames"]:05d}.bin')
    sms=bytes(raw[(sy['sms_vram']+i)^1] for i in range(16384));base=(regs[2]&56)<<10;width=[32,64,32,128][regs[16]&3]
    for n in range(128):
        w=int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2],'little');at=base+((n//32+22)*width+n%32)*2
        assert int.from_bytes(v[at:at+2],'little')==translated(w)
    for n in range(4):
        tile,offset=source[0x1edc+n*2:0x1ede+n*2];assert sms[0x3d00+offset:0x3d02+offset]==bytes([tile,0x59])
    for n in ['tools/validate_reward_hud_restore.py','tools/summarize_reward_hud_v0306.py']:read(n)
    result=dict(passed=True,version=306,md_sha256=digest,source_sha256=sha(source),bytes=len(rom),checksum='343B',
                changed_production_sources=changed,older_numbered_roms_preserved=305,
                controlled_comparisons=reports,settled_hud_word_comparisons=5632,settled_source_tile_pixels_exact=True,
                unchanged_window_word_comparisons=window_checks,unchanged_window_tiles_exact=window_tiles,
                four_crystals_current_rom_replayed=True,current_exterior_room=0x10,current_health=50,current_max_health=64,
                current_campaign_trace=root,campaign_frames=c['frames'],whole_ram_png_cold_replay_exact=True,
                observed_instruction_stack_margin_bytes=margin,full_game_validated=False,evidence=refs,
                limits=['Explicit item-room and crystal/contact/stat fixtures compare actual SMS and MD loops in PAL/NTSC. Two items plus all nine crystals,22 scenarios,44 settled snapshots;not full-game video/audio/cadence proof.',
                        'Native1DE2 now uploads the complete24-row map,including the four restored HUD rows. Source1EB5/1EDC marker table also runs after redraw and initial/resumed HUD construction. No extra permanent RAM buffer.',
                        'Current-ROM cold execution through four crystals and exterior10 independently replays all65536RAM and finalPNG. Only logged approach hero_hurt protection;no boss protection,HP/MP/inventory/actor/progression fixtures or SRAM imports.',
                        'Instruction-stack scope86364 frames,observed margin442 bytes,heap valid. Later campaign,ending,saves,source RNG/global phase and complete SMS audio/video/hardware fidelity remain unproved.'])
    (ROOT/'analysis/reward_hud_v0306_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
    print('v306:HUD restored and nine source markers exact;22 PAL/NTSC scenarios;four-crystal cold replay exact;stack margin442 bytes')


if __name__=='__main__':main()
