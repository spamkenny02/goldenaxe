"""Lossless archive of the HUD baseline/fix and current-ROM cold campaign."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
from rebase_natural_campaign import evidence


def main():
    report=json.loads((ROOT/'analysis/reward_hud_v0306_report.json').read_bytes())
    assert report['passed'] and report['version']==306 and report['four_crystals_current_rom_replayed']
    protected=[ROOT/'input/original.sms',ROOT/'gaw-megadrive.bin',ROOT/'gaw-title-megadrive.bin',
               *sorted((ROOT/'versions').glob('*/*.bin'))]
    assert len(protected)==309
    before={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
    root=ROOT/report['current_campaign_trace'];c=json.loads((root/'capture.json').read_bytes())
    roots=[ROOT/'validation'/n for n in ['v0305-before-reward-hud-fix',
            'reward-hud-v0305-baseline01','reward-hud-v0305-baseline02','reward-hud-v0305-baseline03',
            'reward-hud-v0305-baseline04','reward-hud-v0306-fixed01','stack-v0306-d4-all']]
    roots += [root,root.with_name(root.name+f"-assisted-fixed-replay-{c['frames']}")]
    assert all(p.exists() and p.resolve().is_relative_to(ROOT/'validation') for p in roots)
    paths=[p for folder in roots for p in folder.rglob('*') if p.is_file()]
    inherited=[]
    for name,digest in report['evidence'].items():
        p=ROOT/name;assert sha(evidence(p))==digest
        if p.exists():paths.append(p)
        else:inherited.append(dict(path=name,sha256=digest))
    prefix=json.loads((ROOT/'analysis/reward_hud_v0306_worklog_prefix.json').read_bytes())
    assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['prefix_bytes']])==prefix['prefix_sha256']
    paths += [ROOT/n for n in ['README.md','analysis/world_next.md','analysis/reward_hud_v0306.md',
              'analysis/reward_hud_v0306_report.json','analysis/reward_hud_v0306_worklog_prefix.json',
              'tools/archive_reward_hud_v0306.py','tools/rebase_natural_campaign.py']]
    paths += [p for p in (ROOT/'validation').glob('*.log') if p.name.startswith(
        ('build-v0306','v0305-reward-hud','v0306-reward-hud','v0306-d4-'))]
    ready=root/f"ram_{c['frames']:05d}.bin";raw=ready.read_bytes()
    freeze(ROOT,ROOT/'analysis/reward-hud-v0306',paths,
           dict(version=306,md_sha256=report['md_sha256'],protected_sha256=before,
                inherited_evidence=inherited,worklog_prefix=prefix,
                incomplete_diagnostic_fixtures_not_promoted=True),roots,cleanup=True)
    ready.write_bytes(raw)
    assert before=={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected}
    from summarize_reward_hud_v0306 import main as summarize
    old=(ROOT/'analysis/reward_hud_v0306_report.json').read_bytes();summarize()
    assert (ROOT/'analysis/reward_hud_v0306_report.json').read_bytes()==old
    assert (ROOT/'versions/v0306-3a12380b/reward_hud_v0306_report.json').read_bytes()==old
    print('All309 original/ROM files unchanged;v306 report identical;four-crystal ready RAM retained')


if __name__=='__main__':main()
