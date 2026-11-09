"""Read-only PSG registers; restore upstream source even after build failure."""
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    path = ROOT.parents[1]/'work/genesis-plus-gx/core/sound/psg.c'
    original = path.read_bytes()
    existing = b'__declspec(dllexport) const int *gaw_psg_regs(void) { return psg.regs; }'
    assert b'gaw_psg_regs' not in original or original.count(existing) == 1
    try:
        if b'gaw_psg_regs' not in original:
            path.write_bytes(original + b'\n__declspec(dllexport) const int *gaw_psg_regs(void) {return psg.regs;}\n')
        subprocess.run([sys.executable, str(ROOT/'tools/build_timing_core.py'),
                        '--target', 'genesis_plus_gx_psg_registers_libretro.dll',
                        '--force-source', 'core/sound/psg.c',
                        '--force-source', 'core/m68k/m68kcpu.c',
                        '--force-source', 'core/m68k/s68kcpu.c'], check=True)
    finally:
        path.write_bytes(original)
    assert path.read_bytes() == original
    print('Upstream PSG source restored:', hashlib.sha256(original).hexdigest())


if __name__ == '__main__':
    main()
