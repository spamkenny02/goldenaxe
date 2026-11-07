"""Freeze the actual c0046 game-written nine-crystal save and normal Continue proof."""
import json,sys
from pathlib import Path
sys.path.insert(0,'tools')
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols
work=Path(__file__).resolve().parent;project=work/'isolated/project';reference=ROOT/'analysis/game_written_save_c0046_nine_crystals_report.json';paths={Path(__file__).resolve(),work/'prepare_candidate_save.py',reference}
def read(p):paths.add(p);return p.read_bytes()
def load(p):return json.loads(read(p))
r=load(reference);digest=sha((project/'gaw-megadrive.bin').read_bytes());assert r['passed'] and r['candidate']=='c0046' and r['md_sha256']==r['rom_sha256']==digest
assert r['game_written_save'] and not r['synthetic_sram_fixture'] and r['raw_sram_fixed_replay_exact'] and r['save_whole_ram_png_exact'] and r['serialized_payload_bytes']==592 and r['source_crystal_markers_exact']==9
assert r['reload_primary_sram_imports']==1 and not r['reload_ram_writes'] and r['physical_hud_words_exact']==128
source=(project/'validation'/r['source_trace']).resolve();fixed=(project/r['fixed_replay_trace']).resolve();loader=(project/r['reload_trace']).resolve()
assert all(p.is_relative_to(project/'validation') for p in (source,fixed,loader))
c=load(source/'capture.json');s=load(source/'report.json');a,w=recording(source,c);sy=symbols(project/'megadrive/out/release/symbol.txt')
assert c['rom_sha256']==digest and c['sram_input'] is None and s['passed'] and s['game_written_save'] and s['payload_source_ram_exact'] and not s['primary_state_imports'] and not s['new_assistance_writes']
assert not a['primary_state_imports'] and not a['health_refills'] and not a['boss_assistance'] and all(addr==sy['hero_hurt'] and value in (b'\0\0',b'\0\x81') for _,addr,value in w)
sram=(project/s['sram_file']).resolve();assert sram.is_relative_to(source)
raw=read(sram);assert sha(raw)==r['source_sram_sha256'] and raw==read(fixed/'replayed.srm')
payload=read(source/'serialized-payload.bin');assert len(payload)==592 and payload[0x1f:0x28]==bytes([128]*9)
pr=load(fixed/'replay_report.json');assert pr['passed'] and pr['rom_sha256']==digest and pr['whole_ram_bytes']==65536 and pr['final_png_exact'] and pr['raw_sram_exact'] and not pr['feedback_reads']
f=c['frames']
for stem,ext in [('ram','bin'),('frame','png')]:assert read(source/f'{stem}_{f:05d}.{ext}')==read(fixed/f'{stem}_{f:05d}.{ext}')
lc=load(loader/'capture.json');lr=load(loader/'report.json');assert all(r[k]==v for k,v in lr.items())
assert Path(lc['sram_input']).resolve()==sram and not lc['test_ram_writes'] and lr['movement_verified_frame']>lr['reload_ready_frame'] and lr['last_state']['health']>0
validator=project/'tools/validate_candidate_game_written_save_c0046.py';assert sha(read(validator))==r['driver_sha256']
base=project/'validation/c0046-after-d9-sources';snapshot=base/'save'
for name,h in load(snapshot/'source_index.json').items():assert sha(read(snapshot/name))==h and sha(read(project/'tools'/name))==h
stream=load(base/'save-cold-stream/completed.json');assert stream['passed'] and stream['cold_boot_count']==1 and stream['rom_sha256']==digest and len(stream['checkpoints'])==1 and stream['checkpoints'][0]['whole_ram_png_exact']
for folder in (source,fixed,loader):paths.update(p for p in folder.rglob('*') if p.is_file())
out=ROOT/'analysis/c0046-real-save'
result=dict(r,source_trace=source.relative_to(ROOT).as_posix(),fixed_replay_trace=fixed.relative_to(ROOT).as_posix(),reload_trace=loader.relative_to(ROOT).as_posix(),source_verifier_report=reference.relative_to(ROOT).as_posix(),archive_manifest=(out/'manifest.json').relative_to(ROOT).as_posix())
freeze(ROOT,out,paths,result,[work])
(ROOT/'analysis/c0046_real_save_report.json').write_text(json.dumps(result,indent=2)+'\n')
print('Actual c0046 nine-crystal SRAM write and normal Continue archived; reload import explicitly retained',flush=True)
