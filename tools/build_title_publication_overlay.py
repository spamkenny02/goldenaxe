"""Apply the title-only native 68000 publication fix to the exact V320.

Keep all other code, data, IRQs and the V320 credits overlay in place.
No whole-game relink. Reject any different base or unexpected hook opcode.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from finalize_md_rom import md_checksum

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out', required=True)
    p.add_argument('--base', type=Path, help='Exact rebuilt V320; checked by SHA-256')
    options = p.parse_args()
    out = (ROOT / options.out).resolve()
    assert out.is_relative_to(ROOT / 'validation') and not out.exists()
    out.mkdir(parents=True)
    base_path = options.base or ROOT/'versions/v0320-9e5b0abe/gaw-megadrive-v0320.bin'
    if base_path.exists():
        base = base_path.read_bytes()
    else:
        assert not options.base, 'Requested base ROM does not exist'
        base = subprocess.check_output(['git', 'show', '1c7d39cfcfd2fcc2a7fff3de6feb159e49f3d24b:versions/v0320-9e5b0abe/gaw-megadrive-v0320.bin'], cwd=ROOT)
    assert hashlib.sha256(base).hexdigest() == '9e5b0abed80678ce864a0bb796c17e97047d1d34e5227a5275bf9336129ceaff'
    raw = bytearray(base)
    sdk = ROOT.parents[1] / 'work/sgdk/bin'
    source = ROOT / 'megadrive/overlays/title_publication.s'
    shutil.copyfile(source, out / source.name)
    subprocess.run([str(sdk/'as.exe'), '-m68000', '-o', str(out/'overlay.o'), str(source)], check=True)
    subprocess.run([str(sdk/'ld.exe'), '-Ttext=0x1f0100', '-e', 'title_publish_row', '-o', str(out/'overlay.out'), str(out/'overlay.o')], check=True)
    subprocess.run([str(sdk/'objcopy.exe'), '-O', 'binary', str(out/'overlay.out'), str(out/'overlay.bin')], check=True)
    payload = (out / 'overlay.bin').read_bytes()
    assert len(payload) < 256
    assert raw[0x1F0100:0x1F0100+len(payload)] == bytes([255])*len(payload)
    # All calls below are in the title's inlined copy_rows expansions.
    # Includes wrap and DMA-bank-split branches, not just observed branches.
    sites = [0x4AD3C, 0x4AD5E, 0x4ADDC, 0x4AE12, 0x4AE36,
             0x4B11E, 0x4B140, 0x4B40E, 0x4B42E, 0x4B49E,
             0x4B4C0, 0x4B4E6]
    hooks = []
    for site, expected in [(n, '4eb900026754') for n in sites] + [(0x4AEF6, '49f900026754')]:
        assert raw[site:site+6].hex() == expected, hex(site)
        replacement = bytes.fromhex(expected[:4]) + (0x1F0100).to_bytes(4, 'big')
        raw[site:site+6] = replacement
        hooks.append(dict(site=site, original=expected, replacement=replacement.hex()))
    # Full warrior-map restoration uses a generic SGDK function. Its last
    # argument becomes CPU=0 rather than DMA_QUEUE=2; same stack footprint.
    site = 0x4AAE8
    assert raw[site:site+4].hex() == '48780002'
    raw[site:site+4] = bytes.fromhex('42a74e71')  # CLR.L -(SP); NOP
    hooks.append(dict(site=site, original='48780002', replacement='42a74e71'))
    raw[0x1F0100:0x1F0100+len(payload)] = payload
    raw[0x18E:0x190] = md_checksum(raw).to_bytes(2, 'big')
    allowed = {0x18E, 0x18F} | set(range(0x1F0100, 0x1F0100+len(payload)))
    for h in hooks:
        allowed.update(range(h['site'], h['site']+len(bytes.fromhex(h['original']))))
    changed = [n for n, (a, b) in enumerate(zip(base, raw)) if a != b]
    assert all(n in allowed for n in changed)
    assert raw[0x1F0000:0x1F0100] == base[0x1F0000:0x1F0100]
    (out/'gaw-megadrive-candidate.bin').write_bytes(raw)
    report = dict(base_sha256=hashlib.sha256(base).hexdigest(),
                  md_sha256=hashlib.sha256(raw).hexdigest(),
                  source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  overlay_address=0x1F0100, overlay_bytes=len(payload), hooks=hooks,
                  changed_bytes=len(changed), all_other_bytes_identical=True,
                  credits_overlay_unchanged=True, checksum=raw[0x18E:0x190].hex().upper(),
                  runtime_validation_required=True)
    (out/'build-report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
