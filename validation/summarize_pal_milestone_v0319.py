"""Attach a completed PAL candidate milestone and exact c0047 replay to V319."""
import argparse,hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--dungeon',type=int,choices=(6,7,8,9),required=True);args=p.parse_args();d=args.dungeon
words={6:'sixth',7:'seventh',8:'eighth',9:'ninth'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=root/f'analysis/palc0046_d{d}_report.json';replay=root/f'analysis/c0047_pal_d{d}_report.json'
a=json.loads(source.read_bytes());b=json.loads(replay.read_bytes())
assert a['passed'] and a['candidate']=='c0046' and a['region']=='pal' and a[f'actual_{words[d]}_crystal_and_exterior']
assert b['passed'] and b['candidate']=='c0047' and b['region']=='pal' and b['milestone']==f'd{d}' and b['whole_ram_bytes_exact']==65536 and b['final_png_exact']
assert b['frames']==a['campaign_frames']>0 and b['source_report_sha256']==sha(source) and b['reference_rom_sha256']==a['rom_sha256']=='9e747d38e0c6fb2d69b7c1aa8c2b296a61e8b6af41171d14e543ed9a6cb49cf5'
assert not b['initial_sram'] and b['primary_state_imports']==0
rom=root/'gaw-megadrive.bin';numbered=root/'versions/v0319-d3ea2a83/gaw-megadrive-v0319.bin'
assert rom.read_bytes()==numbered.read_bytes() and sha(rom)==b['rom_sha256']=='d3ea2a83ea24ed8a0d3c9857f9fbe70d000a4f73358452c1887f40e78966c56e'
r=dict(passed=True,version=319,md_sha256=sha(rom),pal_crystals_and_exterior_returns_verified=d,frames=b['frames'],whole_ram_bytes_exact=65536,final_png_exact=True,initial_sram=False,primary_state_imports=0,source_candidate_rom_sha256=a['rom_sha256'],full_game_validated=False,evidence={source.relative_to(root).as_posix():sha(source),replay.relative_to(root).as_posix():sha(replay)},scope=f'Additional PAL D{d} receipt on unchanged V319/c0047 bytes, strict full-RAM and endpoint-image replay of the independently audited candidate campaign. Approach-only test protection ends before each boss. This checkpoint does not prove global SMS fidelity, PCM or physical-console behavior.')
report=root/f'analysis/pal_d{d}_v0319_report.json';raw=(json.dumps(r,indent=2)+'\n').encode()
if report.exists():assert report.read_bytes()==raw,'Preserve existing receipt if evidence changes'
else:report.write_bytes(raw)
print(f'V319 PAL D{d} milestone receipt verified')
