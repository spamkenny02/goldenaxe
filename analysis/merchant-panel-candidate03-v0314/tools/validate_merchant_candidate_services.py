"""Run existing merchant transactions against an isolated candidate cartridge."""
import argparse
import shutil
import sys
from pathlib import Path

import validate_all_merchants as checks
from run_core import ROOT


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    project, out = args.project.resolve(), args.out.resolve()
    assert project.is_relative_to(ROOT/'validation')
    assert out.is_relative_to(ROOT/'validation') and not out.exists()
    for source, target in [
        (project/'out/release/rom.bin', out/'gaw-megadrive.bin'),
        (project/'out/release/symbol.txt', out/'megadrive/out/release/symbol.txt'),
        *[(ROOT/name, out/name) for name in (
            'input/original.sms', 'analysis/merchant_assets.json',
            'analysis/doors_reference.json', 'validation/sms-save-slot-0.srm',
            'validation/md-save-slot-0.srm')]]:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    # The existing suite deliberately uses synthetic service fixtures. These
    # never enter the natural campaign, whose core, paths and ROM stay separate.
    checks.ROOT = out
    sys.argv = [__file__]
    checks.main()


if __name__ == '__main__':
    main()
