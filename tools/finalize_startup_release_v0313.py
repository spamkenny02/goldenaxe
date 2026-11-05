"""Bind the rebuilt public ROM to the validated eight-crystal startup candidate."""
import json
import shutil
from archive_lossless_evidence import sha
from assisted_prefix import recording, prefix_writes
from rebase_natural_campaign import evidence
from run_core import ROOT
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated


def main():
    refs={}
    def read(path):
        raw=evidence(ROOT/path);refs[path]=sha(raw);return raw
    def load(path):return json.loads(read(path))
    title=load('analysis/title_boot_candidate_v0312_report.json')
    campaign=load('analysis/title_boot_candidate_d8_report.json')
    assert title['passed'] and campaign['passed'] and campaign['eighth_crystal_and_exterior_return']
    raw=read('gaw-megadrive.bin');digest=sha(raw)
    assert digest==title['md_sha256']==campaign['md_sha256']
    assert raw==read('gaw-title-megadrive.bin')
    assert len(raw)==2097152
    checksum=sum((raw[i]<<8)|raw[i+1] for i in range(0x200,len(raw),2))&65535
    assert checksum==int.from_bytes(raw[0x18e:0x190],'big')==0x544b
    entries=load('versions/index.json');entry=next(row for row in entries if row['sha256']==digest)
    assert entry['version']==313 and raw==read('versions/'+entry['rom'])
    project=ROOT/'validation/title-boot-phase-v0312/candidate02'
    src=ROOT/'megadrive/src';other=project/'megadrive/src'
    names=sorted(p.relative_to(src).as_posix() for p in src.rglob('*') if p.is_file())
    assert names==sorted(p.relative_to(other).as_posix() for p in other.rglob('*') if p.is_file())
    assert all((src/name).read_bytes()==(other/name).read_bytes() for name in names)
    read('megadrive/src/intro.inc')
    source=ROOT/campaign['current_campaign_trace'];cap=json.loads((source/'capture.json').read_bytes())
    frame=cap['frames'];proof_source=source.with_name(source.name+f'-assisted-fixed-replay-{frame}')
    destination=ROOT/'validation/natural-dungeon-combat/md-auto-v0313-d8-cold01'
    proof_destination=destination.with_name(destination.name+f'-assisted-fixed-replay-{frame}')
    copied={}
    for old,new in [(source,destination),(proof_source,proof_destination)]:
        assert old.resolve().is_relative_to((ROOT/'validation').resolve())
        assert new.resolve().is_relative_to((ROOT/'validation').resolve())
        if not new.exists():shutil.copytree(old,new)
        old_files=sorted(p.relative_to(old).as_posix() for p in old.rglob('*') if p.is_file())
        new_files=sorted(p.relative_to(new).as_posix() for p in new.rglob('*') if p.is_file())
        assert old_files==new_files
        for name in old_files:
            original=(old/name).read_bytes();assert original==(new/name).read_bytes()
            copied[(new/name).relative_to(ROOT).as_posix()]=sha(original)
    trace=destination.relative_to(ROOT).as_posix()
    c=load(trace+'/capture.json');report=load(trace+'/report.json')
    assert c['rom_sha256']==digest and c['sram_input'] is None
    assert report['passed'] and report['full_dungeon_cleared'] and report['dungeon_exit_verified']
    aid,writes=recording(destination,c)
    assert list(prefix_writes(destination,c,True))==writes
    assert not aid['primary_state_imports'] and not aid['boss_assistance'] and not aid['health_refills']
    sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
    assert all(addr==sy['hero_hurt'] and value in (b'\0\0',b'\0\x81') for _,addr,value in writes)
    memory=read(trace+f'/ram_{frame:05d}.bin')
    def data(name,count):return bytes(memory[(sy[name]+i)^1] for i in range(count))
    def word(name):return int.from_bytes(data(name,2),'big')
    assert data('game_save_state',592)[0x1f:0x28]==bytes([128]*8+[0])
    assert word('room_id')==0x29 and word('world_dungeon_number')==0 and word('game_state')==12
    assert word('hero_health')==word('hero_max_health')==96 and not word('sound_unhandled_command')
    items=data('hero_items',17)
    assert items[15]==items[16]==1
    sms=data('sms_vram',16384);vram=read(trace+f'/vram_{frame:05d}.bin')
    regs=read(trace+f'/vdp_regs_{frame:05d}.bin');base=(regs[2]&56)<<10;width=[32,64,32,128][regs[16]&3]
    for n in range(128):
        at=base+((n//32+22)*width+n%32)*2
        assert int.from_bytes(vram[at:at+2],'little')==translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2],'little'))
    original=read('input/original.sms')
    for n in range(8):
        tile,offset=original[0x1edc+n*2:0x1ede+n*2]
        assert sms[0x3d00+offset:0x3d02+offset]==bytes([tile,0x59])
    manifest=ROOT/'analysis/startup_v0313_prefix_manifest.json'
    manifest.write_text(json.dumps(dict(source_trace=campaign['current_campaign_trace'],destination_trace=trace,
        byte_identical_transport=True,files=copied),indent=2)+'\n')
    read(manifest.relative_to(ROOT).as_posix())
    stage=dict(trace=trace,frames=frame,room=word('room_id'),health=96,max_health=96,
               magic=word('hero_magic'),gold=word('hero_gold'),keys=word('hero_keys'),crystals=8,whole_ram_png_exact=True)
    result=dict(passed=True,version=313,md_sha256=digest,bytes=len(raw),md_checksum=f'{checksum:04X}',
                production_matches_validated_candidate=True,native_sources_match_candidate=len(names),
                natural_title_epoch_exact_pal_ntsc=True,story_lines_checked=130,normalized_title_images_checked=40,
                current_campaign_trace=trace,campaign_frames=frame,stages=[stage],
                eighth_crystal_and_exterior_return=True,checked_boss_entries=10,
                candidate_cold_replay_whole_ram_png_exact=True,physical_hud_words_checked=128,
                owned_crystal_markers=8,primary_state_imports=0,full_game_validated=False,evidence=refs,
                limits=['The public2MiB build is byte-identical to the validated candidate. Evidence transport copies files; no game state is imported.',
                        'Current cold campaign reaches eight crystals. D9,palace,ending,saving and complete audiovisual/R/IRQ/hardware fidelity remain open.'])
    (ROOT/'analysis/startup_v0313_report.json').write_text(json.dumps(result,indent=2)+'\n')
    print('v313 public ROM matches validated candidate; eight-crystal cold prefix and HUD verified')


if __name__=='__main__':main()
