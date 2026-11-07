"""Compress inactive D4 diagnostic captures before removing verified duplicates."""
from pathlib import Path
import json
import sys
sys.path.insert(0,'tools')
from run_core import ROOT
from archive_lossless_evidence import freeze
work=Path(__file__).resolve().parent
base=work/'isolated/project/validation/natural-dungeon-combat'
folders=[base/f'md-auto-c0046-d4-exit{n:02}' for n in (1,2)]
paths=[Path(__file__).resolve()];failed=[]
for folder,reason in zip(folders,['controller_stalled','continuation_route_died']):
    assert folder.resolve().is_relative_to((work/'isolated/project/validation').resolve())
    r=json.loads((folder/'report.json').read_bytes())
    assert r['failure']==reason and not r['new_assistance_writes']
    failed.append(dict(trace=folder.relative_to(ROOT).as_posix(),failure=reason))
    paths.extend(p for p in folder.iterdir() if p.is_file())
archive=ROOT/'analysis/c0046-d4-failed-exit-captures'
freeze(ROOT,archive,paths,dict(archive_integrity_only=True,failed_trials=failed,
    scope='Inactive controller attempts; no successful-playthrough claim. Generated binary captures are removed only after full compressed readback and hash verification. Numbered ROMs, successful endpoints and the active D5 campaign are untouched.'),folders,cleanup=True)
