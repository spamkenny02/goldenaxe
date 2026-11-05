"""Verify the startup candidate's eight-crystal cold replay before promotion."""
import json
from archive_lossless_evidence import sha
from assisted_prefix import recording
from rebase_natural_campaign import evidence
from run_core import ROOT
from validate_playable_sprite_limit import symbols


def main():
    refs={}
    def read(path):
        raw=evidence(ROOT/path);refs[path]=sha(raw);return raw
    def load(path):return json.loads(read(path))
    prior=load('analysis/d8_campaign_v0312_report.json')
    title=load('analysis/title_boot_candidate_v0312_report.json')
    assert prior['passed'] and prior['eighth_crystal_and_exterior_return'] and title['passed']
    project='validation/title-boot-phase-v0312/candidate02/'
    trace=project+'validation/natural-dungeon-combat/md-auto-title-boot-candidate02-d8-replay01'
    report,cap=load(trace+'/report.json'),load(trace+'/capture.json')
    digest=sha(read(project+'gaw-megadrive.bin'));assert digest==title['md_sha256']==cap['rom_sha256']==report['md_sha256']
    assert report['passed'] and report['failure'] is None and not report['deaths']
    assert not cap['sram_input'] and report['terminal_field_mismatches']==[] and report['terminal_png_exact']
    assert report['full_dungeon_cleared'] and report['dungeon_exit_verified']
    assert len(report['checked_bosses'])==10 and all(row['passed'] and row['hurt']==0 for row in report['checked_bosses'])
    assert report['last_state']['crystals']==[128]*8+[0] and report['last_state']['room']==0x29
    assert report['last_state']['health']==report['last_state']['max_health']==96
    frame=cap['frames'];proof_root=trace+f'-assisted-fixed-replay-{frame}'
    proof=load(proof_root+'/replay_report.json')
    assert proof['passed'] and proof['rom_sha256']==digest and proof['whole_ram_bytes']==65536
    assert proof['final_png_exact'] and not proof['feedback_reads']
    for name in ('capture.json','controls.json','assistance.json'):
        assert proof['evidence'][name]==sha(read(trace+'/'+name))
    for stem,ext in [('ram','bin'),('frame','png')]:
        filename=f'/{stem}_{frame:05d}.{ext}';assert read(trace+filename)==read(proof_root+filename)
    sy=symbols(ROOT/(project+'megadrive/out/release/symbol.txt'))
    oldsy=symbols(ROOT/'analysis/title-boot-candidate-v0312/base-symbols.txt')
    current=read(trace+f'/ram_{frame:05d}.bin')
    old=read(prior['current_campaign_trace']+f'/ram_{frame:05d}.bin')
    matched={}
    for name,size in [('game_rng_seed',2),('randbase',2),('vtimer',4),('world_actor_state',768),('sms_vram',16384)]:
        a=bytes(old[(oldsy[name]+i)^1] for i in range(size));b=bytes(current[(sy[name]+i)^1] for i in range(size))
        assert a==b,(name,'continuation drift');matched[name]=dict(bytes=size,sha256=sha(b))
    aid,writes=recording(ROOT/trace,cap)
    assert not aid['primary_state_imports'] and not aid['boss_assistance'] and not aid['health_refills']
    assert all(addr==sy['hero_hurt'] and value in (b'\0\0',b'\0\x81') for _,addr,value in writes)
    source=ROOT/'megadrive/src';candidate=ROOT/(project+'megadrive/src')
    names=sorted(p.relative_to(source).as_posix() for p in source.rglob('*') if p.is_file())
    assert names==sorted(p.relative_to(candidate).as_posix() for p in candidate.rglob('*') if p.is_file())
    changed=[name for name in names if (source/name).read_bytes()!=(candidate/name).read_bytes()]
    assert changed==['intro.inc']
    result=dict(passed=True,md_sha256=digest,source_rom_sha256=prior['md_sha256'],candidate_private=True,
                current_campaign_trace=trace,campaign_frames=frame,eighth_crystal_and_exterior_return=True,
                checked_boss_entries=10,terminal_gameplay_fields_match_v0312=True,terminal_png_matches_v0312=True,
                independent_whole_ram_png_replay_exact=True,continuation_state_matches_v0312=matched,
                changed_native_sources=changed,native_source_files_checked=len(names),primary_state_imports=0,
                full_game_validated=False,evidence=refs,
                limits=['Eight-crystal candidate proof with declared approach guards; no state/resource/actor imports.',
                        'D9, palace, ending, saving, complete audiovisual/R/IRQ phase and hardware still require verification.'])
    (ROOT/'analysis/title_boot_candidate_d8_report.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Startup candidate: eight crystals, ten boss entries and deterministic continuation verified')


if __name__=='__main__':main()
