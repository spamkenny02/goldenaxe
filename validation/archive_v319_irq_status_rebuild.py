"""Freeze the full production rebuild after the optional intro IRQ status hook."""
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import freeze,sha
work=root/'validation/v319-irq-status-rebuild01';project=work/'project'
report=json.loads((work/'report.json').read_bytes());assert report['passed'] and report['byte_identical_v319']
rom=(project/'out/release/rom.bin').read_bytes();assert rom==(root/'gaw-megadrive.bin').read_bytes()
assert sha(rom)==report['sha256']=='d3ea2a83ea24ed8a0d3c9857f9fbe70d000a4f73358452c1887f40e78966c56e'
for name,digest in report['source_sha256'].items():
 assert sha((root/'megadrive/src'/name).read_bytes())==digest
 assert (project/'src'/name).read_bytes()==(root/'megadrive/src'/name).read_bytes()
report.update(scope='Full SGDK build from current src/research/z80 copies; optional compact IRQ status provider remains unused by published V319, and the complete rebuilt2MiB ROM is byte-identical.',
 build_recipe='Copy megadrive src/research/z80 and SGDK-license.txt into a new validation project, then tools/build_private_candidate.ps1 -Project <project> -PaddingByte255.',
 binding_report='analysis/v319_irq_status_binding_report.json',archive_manifest='analysis/v319-irq-status-rebuild/manifest.json')
target=root/'analysis/v319_irq_status_rebuild_report.json';assert not target.exists();target.write_text(json.dumps(report,indent=2)+'\n')
paths={p for p in work.rglob('*') if p.is_file()}|{target,Path(__file__).resolve(),root/'tools/build_private_candidate.ps1'}
freeze(root,root/'analysis/v319-irq-status-rebuild',paths,report,[project/'out'],cleanup=True)
