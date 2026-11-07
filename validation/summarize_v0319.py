"""Attach scoped c0047 evidence to the byte-identical numbered v319 development ROM."""
import json,sys
from pathlib import Path
sys.path.insert(0,'tools')
from archive_lossless_evidence import sha
root=Path(__file__).resolve().parents[1];md='d3ea2a83ea24ed8a0d3c9857f9fbe70d000a4f73358452c1887f40e78966c56e'
rom=root/'gaw-megadrive.bin';data=rom.read_bytes();assert sha(data)==md and data==(root/'gaw-title-megadrive.bin').read_bytes()==(root/'versions/candidates/c0047-d3ea2a83/gaw-megadrive-c0047.bin').read_bytes()
entry=next(e for e in json.loads((root/'versions/index.json').read_bytes()) if e['sha256']==md);assert entry['version']==319 and (root/'versions'/entry['rom']).read_bytes()==data
assert len(data)==2097152 and int.from_bytes(data[0x18e:0x190],'big')==0xda29
assert (root/'megadrive/out/release/symbol.txt').read_bytes()==(root/'versions/candidates/c0047-d3ea2a83/symbol.txt').read_bytes()
assert sha((root/'input/original.sms').read_bytes())=='852e068e331dbfb01b9c38a62eecf81ce5b9f0f1bd10fff497117bd885c716c9'
refs={}
def load(name):
    p=root/name;raw=p.read_bytes();refs[name]=sha(raw);return json.loads(raw)
boot=load('analysis/c0047_boot_report.json');assert boot['passed'] and boot['md_sha256']==md and len(boot['regions'])==2
inventory=load('analysis/c0047_inventory_report.json');assert inventory['passed'] and inventory['md_sha256']==md and inventory['normal_controller_routes']==6
rebuild=load('analysis/c0047_clean_rebuild_report.json');assert rebuild['passed'] and rebuild['md_sha256']==md and rebuild['clean_rebuild_identical'] and rebuild['symbols_identical']
ending=load('analysis/c0047_palace_final_auto_report.json');assert ending['passed'] and ending['rom_sha256']==md and ending['whole_ram_bytes_exact']==65536 and ending['final_png_exact']
base=load('analysis/cold_palace_final_c0046_report.json');assert base['passed'] and base['campaign_from_new_game_completed'] and base['ending_complete'] and not base['final_boss_assistance'] and base['source_crystal_markers_exact']==9
assert ending['frames']==base['campaign_frames']==403488
save=load('analysis/c0047_real_save_report.json');assert save['passed'] and save['rom_sha256']==md and save['game_written_save'] and not save['synthetic_sram_fixture'] and save['reload_from_own_game_written_sram']
assert save['writer_whole_ram_bytes_exact']==save['reload_whole_ram_bytes_exact']==65536 and save['writer_final_png_exact'] and save['reload_final_png_exact'] and not save['reload_ram_writes']
for d in range(1,10):
    r=load(f'analysis/c0047_d{d}_auto_report.json');assert r['passed'] and r['rom_sha256']==md and r['whole_ram_bytes_exact']==65536 and r['final_png_exact']
for name in ['analysis/c0047_d1_pal_report.json']+[f'analysis/c0047_pal_d{d}_report.json' for d in (2,3,4)]:
    r=load(name);assert r['passed'] and r['rom_sha256']==md and r['whole_ram_bytes_exact']==65536 and r['final_png_exact']
load('analysis/c0046-hero-three-plane/manifest.json')
old=(root/'versions/candidates/c0046-9e747d38/gaw-megadrive-c0046.bin').read_bytes();assert data[:0x18e]==old[:0x18e] and data[0x190:len(old)]==old[0x190:] and set(data[len(old):])=={255}
result=dict(version=319,md_sha256=md,bytes=len(data),checksum='DA29',previous_version=318,previous_md_sha256='b9e1f0a0543f191e24ffd6d2740a0d717501e0fcd986f8b8953a37a1b3c416a4',
            promoted_candidate='c0047',candidate_bytes_identical=True,clean_rebuild_identical=True,symbols_identical=True,
            ntsc_new_game_campaign_complete=True,ntsc_ending_and_intro_return=True,ntsc_frames_replayed=ending['frames'],final_checkpoint_whole_ram_bytes_exact=65536,final_checkpoint_png_exact=True,
            ntsc_actual_save_and_continue=True,pal_crystals_and_exterior_returns_verified=4,pal_complete_campaign_verified=False,
            approach_assistance_used=True,boss_assistance=False,synthetic_sram_fixture=False,complete_port_verified=False,evidence=refs,
            changes=['Use resident dungeon actor pattern atlas for sprite masks, avoiding unnecessary VDP readback when no pending job owns the tile.','Replace tiny three-byte memcpy calls with direct hero pattern expansion writes.','Package2MiB ROM with explicitFF external padding; normal build and clean historical reconstruction reproduce the published candidate.'],
            remaining=['PAL D5 through ending and PAL save on these bytes.','Existing partial reveal/fade differences and global source R/IRQ phase.','Global PCM/audio/framebuffer equivalence and physical console tests are not established.'],
            limits=['Development release of exactly the tested c0047 binary. NTSC campaign uses logged approach-only hurt writes, removed before every boss; no resource,actor,progression or initial SRAM imports.','The403488-frame c0047 replay compares whole RAM and final image at its endpoint; it does not compare every emitted frame or every source state. Other milestones and source comparisons retain their separate scopes.','PAL currently covers four crystals and returns; this initial release report remains a dated checkpoint when later evidence is attached.'])
p=root/'analysis/optimization_v0319_report.json';assert not p.exists();p.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('v319 initial development-release report verified against the exact published ROM and scoped component proofs')
