"""Prepare fresh PAL D7 funding/keys/Earth route from the audited D6 exterior."""
import ast
from pathlib import Path
root=Path(__file__).resolve().parents[2];project=root/'validation/c0046-campaign01/isolated/project'
s=(root/'validation/pal318-d7-run01/run.py').read_text().replace('pal318','palc0046')
s=s.replace("default='02'","default='01'").replace('pal_d6_v0318_report.json','palc0046_d6_report.json').replace("prior['sixth_crystal_and_exterior_return']","prior['actual_sixth_crystal_and_exterior']").replace("prior['md_sha256']","prior['rom_sha256']")
a=s.index("    prefix = prior['stages']");b=s.index('    sy = symbols',a)
s=s[:a]+"""    end = dict(prior['stages'][-1]);end['frames']=end['frame']
    prefix=Path(end['trace']).name
    assert prefix=='md-pal-palc0046-d6-exit01'
    raw=evidence(ROOT/'validation/natural-dungeon-combat'/prefix/f'ram_{end["frames"]:05d}.bin')
    assert sha(raw)==prior['final_ram_sha256']
"""+s[b:]
s=s.replace('out = Path(__file__).resolve().parent',"out = ROOT/'validation/palc0046-d7-prep-sources'\n    out.mkdir(exist_ok=False)")
s=s.replace("'continue_d7_funded_v0317.py'","'continue_d7_palc0046.py'")
s=s.replace("stream=ReplayStream(out/'cold-stream')","stream=ReplayStream(ROOT/'validation/palc0046-d7-prep-cold-stream01')")
s=s.replace("for token in old] + ['--pal']","for token in old] + ['--pal','--wake-sentinels']")
p=project/'tools/continue_d7_palc0046.py';assert not p.exists();ast.parse(s);p.write_text(s)
print('PAL D7 preparation controller generated; execution requires audited D6 exterior and its exact RAM hash')
