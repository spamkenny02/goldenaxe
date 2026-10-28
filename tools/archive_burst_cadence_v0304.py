"""Freeze completed297..304 cadence experiments and fresh D1 evidence."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze,sha


def main():
    report=json.loads((ROOT/'analysis/burst_cadence_v0304_report.json').read_bytes())
    assert report['passed'] and report['version']==304 and report['controlled_burst_cadence_fixed']
    assert report['fresh_first_crystal_and_exit'] and not report['full_game_validated']
    protected=[ROOT/'input/original.sms',ROOT/'gaw-megadrive.bin',ROOT/'gaw-title-megadrive.bin',*sorted((ROOT/'versions').glob('*/*.bin'))]
    assert len(protected)==307
    before={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
    labels=[f'v{n:04d}' for n in range(297,305)]
    roots=[]
    for p in (ROOT/'validation').iterdir():
        if not p.is_dir():continue
        if any(p.name.startswith(prefix+label) for label in labels for prefix in
               ['cost-','instruction-','sprite-mask-cache-host-','sprite-mask-cache-host-candidate-',
                'sprite-mask-cache-gameplay-','sprite-rows-','world-frame-coherence-','stack-']):roots.append(p)
        elif p.name.startswith(('v0296-baseline-burst-','v0304-burst-','v0304-sources')):roots.append(p)
    for family in ['natural-dungeon-route','natural-dungeon-combat']:
        roots += [p for p in (ROOT/'validation'/family).iterdir() if p.is_dir() and p.name.startswith(('md-v0304-','md-auto-v0304-'))]
    assert roots and all(p.resolve().is_relative_to(ROOT/'validation') for p in roots)
    paths=[p for root in roots for p in root.rglob('*') if p.is_file()]
    paths += [ROOT/n for n in report['evidence']]
    # Preserve remaining intermediate reports and tool source as well as the selected proof.
    paths += [p for p in (ROOT/'analysis').iterdir() if p.is_file() and (any(label in p.name for label in labels) or p.name in ['burst_instruction_cost_v0296_report.json','burst_variant_7c_v0296_baseline_diagnostic.json'])]
    paths += [p for p in (ROOT/'validation').iterdir() if p.is_file() and (any(label in p.name for label in labels) or p.name=='v0296-burst-instructions.log')]
    paths += [ROOT/'README.md',ROOT/'analysis/world_next.md',ROOT/'analysis/readme_history_through_v0296.md',
              ROOT/'analysis/readme_history_through_v0296_manifest.json',ROOT/'tools/archive_burst_cadence_v0304.py',ROOT/'tools/rebase_natural_campaign.py']
    prefix=json.loads((ROOT/'analysis/burst_cadence_v0304_worklog_prefix.json').read_bytes())
    assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['prefix_bytes']])==prefix['prefix_sha256']
    history=json.loads((ROOT/'analysis/readme_history_through_v0296_manifest.json').read_bytes())
    raw=(ROOT/history['preserved_file']).read_bytes()
    assert sha(raw)==history['preserved_file_sha256'] and sha(raw[-history['original_section_bytes']:])==history['original_section_sha256']
    latest=ROOT/'validation/natural-dungeon-combat/md-auto-v0304-d1-exit01/ram_14583.bin';ready=latest.read_bytes()
    freeze(ROOT,ROOT/'analysis/burst-cadence-v0304',paths,
           dict(version=304,md_sha256=report['md_sha256'],protected_sha256=before,
                controlled_cadence_fixed=True,full_game_validated=False,worklog_prefix=prefix),roots,cleanup=True)
    latest.write_bytes(ready)
    assert before=={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
    from summarize_burst_cadence_v0304 import main as summary
    old=(ROOT/'analysis/burst_cadence_v0304_report.json').read_bytes();summary()
    assert (ROOT/'analysis/burst_cadence_v0304_report.json').read_bytes()==old
    assert (ROOT/'versions/v0304-b7b4e150/burst_cadence_v0304_report.json').read_bytes()==old
    print('All307 original/ROM files unchanged; report identical after cleanup; current D1 exit RAM retained')


if __name__=='__main__':main()
