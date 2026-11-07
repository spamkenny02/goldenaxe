"""Losslessly archive only intermediate binary captures of the three completed D9 fights."""
import json,re,sys
from pathlib import Path
sys.path.insert(0,'tools')
from archive_lossless_evidence import freeze,sha
root=Path(__file__).resolve().parents[1];base=root/'validation/c0046-campaign01/isolated/project/validation/natural-dungeon-combat'
archives=['c0046-d9-midboss','c0046-d9-balloon','c0046-d9-campaign'];protected=set();paths={Path(__file__).resolve()}
for name in archives:
    p=root/'analysis'/name/'manifest.json';m=json.loads(p.read_bytes());assert m['passed'] and m['candidate']=='c0046'
    protected.update(m['files']);protected.update(m['compressed']);paths.add(p)
folders=[];rows=[]
for name in ['md-auto-c0046-d9-midboss01','md-auto-c0046-d9-giant01','md-auto-c0046-d9-boss01']:
    folder=(base/name).resolve();assert folder.is_relative_to(base.resolve());folders.append(folder)
    c=json.loads((folder/'capture.json').read_bytes());r=json.loads((folder/'report.json').read_bytes());f=c['frames']
    assert c['rom_sha256']==r['rom_sha256']=='9e747d38e0c6fb2d69b7c1aa8c2b296a61e8b6af41171d14e543ed9a6cb49cf5' and c['sram_input'] is None
    assert r['failure'] is None and not r['deaths'] and r['room_cleared'] and not r['new_assistance_writes']
    proof=folder.with_name(name+f'-assisted-fixed-replay-{f}');pr=json.loads((proof/'replay_report.json').read_bytes())
    assert pr['passed'] and pr['whole_ram_bytes']==65536 and pr['final_png_exact']
    for stem,ext in [('ram','bin'),('frame','png')]:assert (folder/f'{stem}_{f:05d}.{ext}').read_bytes()==(proof/f'{stem}_{f:05d}.{ext}').read_bytes()
    selected=[]
    for p in folder.glob('*.bin'):
        if not re.fullmatch(r'(ram|vram|cram|vdp_regs|vsram|zram|z80_ram)_\d+\.bin',p.name):continue
        if p.stem.endswith('_'+f'{f:05d}') or p.relative_to(root).as_posix() in protected:continue
        selected.append(p)
    assert selected
    paths.update(selected);paths.update(folder/n for n in ('capture.json','report.json','assistance.json','controls.json'))
    rows.append(dict(trace=folder.relative_to(root).as_posix(),preserved_final_frame=f,intermediate_files=len(selected),raw_bytes=sum(p.stat().st_size for p in selected)))
metadata=dict(passed=True,completed_d9_fights_only=True,preserved_all_existing_archive_references=True,preserved_final_captures_and_all_pngs=True,
              rows=rows,source_archives=archives,scope='Intermediate RAM/VRAM/register captures of already verified closed NTSC D9 fights only; no ROMs, sources, canonical endpoints, controls, PNGs or active palace/PAL captures removed.')
freeze(root,root/'analysis/c0046-d9-intermediate-captures',paths,metadata,folders,cleanup=True)
print('Closed D9 intermediate captures compressed and verified; all canonical endpoints retained',flush=True)
