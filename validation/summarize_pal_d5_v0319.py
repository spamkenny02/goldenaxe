"""Attach the audited PAL fifth-crystal milestone to unchanged numbered V319 bytes."""
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=root/'analysis/palc0046_d5_report.json';q=root/'analysis/c0047_pal_d5_report.json'
a=json.loads(p.read_bytes());b=json.loads(q.read_bytes());rom=root/'gaw-megadrive.bin';version=root/'versions/v0319-d3ea2a83/gaw-megadrive-v0319.bin'
assert a['passed'] and a['actual_fifth_crystal_and_exterior'] and a['satellites_observed']==8
assert b['passed'] and b['whole_ram_bytes_exact']==65536 and b['final_png_exact'] and b['frames']==a['campaign_frames']==137596
assert b['source_report_sha256']==sha(p) and b['reference_rom_sha256']==a['rom_sha256'] and not b['initial_sram'] and b['primary_state_imports']==0
assert rom.read_bytes()==version.read_bytes() and sha(rom)==b['rom_sha256']=='d3ea2a83ea24ed8a0d3c9857f9fbe70d000a4f73358452c1887f40e78966c56e'
r=dict(passed=True,version=319,md_sha256=sha(rom),pal_fifth_crystal_and_exterior_verified=True,frames=137596,whole_ram_bytes_exact=65536,final_png_exact=True,initial_sram=False,primary_state_imports=0,source_candidate_rom_sha256=a['rom_sha256'],controller_return_portal_detour_recovered=True,source_cold_reader_count=2,full_game_validated=False,evidence={p.relative_to(root).as_posix().replace('/',chr(92)):sha(p),q.relative_to(root).as_posix().replace('/',chr(92)):sha(q)},scope='Additional PAL D5 receipt on unchanged V319/c0047 bytes, strict full-RAM and endpoint-image replay of audited candidate campaign. Includes real boots/gifts/key purchase/healing and source-strength satellite boss, with approach-only guard removed beforehand. Remaining PAL campaign and global SMS fidelity remain open.')
report=root/'analysis/pal_d5_v0319_report.json';raw=(json.dumps(r,indent=2)+'\n').encode()
if report.exists():assert json.loads(report.read_bytes())==r,'Preserve the existing receipt if evidence changes'
else:report.write_bytes(raw)
print('V319 PAL D5 milestone receipt verified')
