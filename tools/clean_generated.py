"""Remove untracked project captures/caches only; preserve every tracked file."""
import argparse
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--execute', action='store_true')
    a = p.parse_args()
    top = Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=ROOT,text=True).strip()).resolve()
    assert top == ROOT.resolve(), 'Not the intended project Git root'
    if a.execute:
        subprocess.run(['git','diff','--quiet','HEAD'],cwd=ROOT,check=True)
        head = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT)
        assert head == subprocess.check_output(['git','rev-parse','origin/main'],cwd=ROOT), 'Push before cleanup'
    tracked = {s.casefold() for s in subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0') if s}
    result = dict(executed=a.execute, files=0, bytes=0, skipped_links=0, errors=[],
                  targets=['validation','analysis','videos','handoff','megadrive/out','versions'])
    before = shutil.disk_usage(ROOT).free
    last = time.monotonic()

    def visit(folder):
        nonlocal last
        if folder.is_symlink() or os.path.isjunction(folder):
            result['skipped_links'] += 1
            return
        assert folder.resolve().is_relative_to(ROOT.resolve()), 'Outside project'
        with os.scandir(folder) as entries:
            for entry in entries:
                path = Path(entry.path)
                if entry.is_symlink() or os.path.isjunction(path):
                    result['skipped_links'] += 1
                    continue
                if entry.is_dir(follow_symlinks=False):
                    visit(path)
                elif entry.is_file(follow_symlinks=False) and path.relative_to(ROOT).as_posix().casefold() not in tracked:
                    size = entry.stat().st_size
                    try:
                        if a.execute:
                            path.unlink()
                        result['files'] += 1
                        result['bytes'] += size
                    except OSError as error:
                        result['errors'].append(dict(path=str(path.relative_to(ROOT)),error=str(error)))
                if time.monotonic()-last > 25:
                    print(json.dumps({k:result[k] for k in ['files','bytes','skipped_links']}),flush=True)
                    last = time.monotonic()
        if a.execute:
            try:
                folder.rmdir()  # Empty directories only. Never recurse through a link.
            except OSError:
                pass

    for name in result['targets']:
        target = ROOT / name
        assert target.resolve().is_relative_to(ROOT.resolve())
        if target.exists():
            visit(target)
    result['disk_free_increase_bytes'] = shutil.disk_usage(ROOT).free-before
    report = ROOT / 'reports/project-closure-2026-11-13'
    report.mkdir(exist_ok=True)
    (report / ('cleanup.json' if a.execute else 'cleanup-plan.json')).write_text(json.dumps(result,indent=2)+'\n',newline='\n')
    print(json.dumps(result),flush=True)


if __name__ == '__main__':
    main()
