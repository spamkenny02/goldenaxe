"""Freeze D3 exploration and v287 release evidence before generated-file cleanup."""
import json
from run_core import ROOT
from archive_lossless_evidence import freeze,sha

def main():
    report=json.loads((ROOT/'analysis/magic_rope_v0287_report.json').read_bytes());assert report['passed'] and report['md_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes())
    prefix=json.loads((ROOT/'analysis/magic_rope_v0287_worklog_prefix.json').read_bytes());assert sha((ROOT/'analysis/world_next.md').read_bytes()[:prefix['bytes']])==prefix['sha256']
    protected=[ROOT/'input/original.sms',ROOT/'gaw-megadrive.bin',ROOT/'gaw-title-megadrive.bin',*sorted((ROOT/'versions').glob('*/*.bin'))]
    before={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in protected};assert len(protected)==290
    roots=[]
    for family in ['natural-dungeon-route','natural-dungeon-combat']:
        roots.extend(p for p in (ROOT/'validation'/family).glob('*v0286-d3*') if p.is_dir())
        roots.extend(p for p in (ROOT/'validation'/family).glob('*v0287*') if p.is_dir())
    for pattern in ['magic-rope','magic-rope-game','stack-v0287*','rebase-v0287*']:
        roots.extend(p for p in (ROOT/'validation').glob(pattern) if p.is_dir())
    paths=[p for d in roots for p in d.rglob('*') if p.is_file()]
    paths.extend(ROOT/n for n in report['evidence'] if (ROOT/n).exists())
    paths.extend(p for p in (ROOT/'validation').glob('*.log') if any(t in p.name for t in ['d3','v0287','magic-rope']))
    paths.extend(ROOT/'megadrive/out/release'/n for n in ['rom.bin','rom.out','symbol.txt'])
    paths.extend(ROOT/'megadrive/src'/n for n in ['main.c','source_magic_rope.c','source_magic_rope.h'])
    paths.extend(ROOT/'tools'/n for n in ['assisted_prefix.py','assisted_boss_route.py','natural_dungeon_combat.py','validate_magic_rope.py','validate_magic_rope_game.py','summarize_magic_rope_v0287.py','archive_magic_rope_v0287.py','profile_playable_stack.py','run_core.py'])
    paths.extend(ROOT/n for n in ['README.md','analysis/world_next.md','analysis/magic_rope_v0287.md','analysis/magic_rope_v0287_report.json','analysis/magic_rope_v0287_worklog_prefix.json'])
    archive=ROOT/'analysis/magic-rope-v0287'
    manifest=freeze(ROOT,archive,paths,dict(md_sha256=report['md_sha256'],full_game_validated=False,numbered_roms_preserved=287,protected_sha256=before),roots,cleanup=True)
    for name,digest in before.items():assert sha((ROOT/name).read_bytes())==digest
    from summarize_magic_rope_v0287 import main as summarize
    raw=(ROOT/'analysis/magic_rope_v0287_report.json').read_bytes();summarize();assert (ROOT/'analysis/magic_rope_v0287_report.json').read_bytes()==raw
    print('Verified cleanup bytes:',sum(r['bytes'] for r in manifest['removed_verified_generated']))
if __name__=='__main__':main()
