"""Private native candidate for empty-word wrapping; never replace published aliases."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
from finalize_md_rom import md_checksum


def main():
    p = argparse.ArgumentParser(); p.add_argument('--out', required=True);p.add_argument('--base',type=Path);p.add_argument('--sdk-bin',type=Path);a = p.parse_args()
    out = (ROOT / 'validation' / a.out).resolve()
    assert out.is_relative_to(ROOT / 'validation') and not out.exists(); out.mkdir()
    base = (a.base or ROOT / 'versions/v0321-89c58333/gaw-megadrive-v0321.bin').read_bytes()
    digest = hashlib.sha256(base).hexdigest()
    assert digest == '89c5833351312ffaa591efb1939161910a298af06437080e2cf84fb3fb8ac86e'
    sdk = a.sdk_bin or ROOT.parents[1] / 'work/sgdk/bin'
    source = ROOT / 'megadrive/overlays/dialogue_empty_width.s'
    subprocess.run([str(sdk/'as.exe'), '-m68000', '-o', str(out/'overlay.o'), str(source)], check=True)
    subprocess.run([str(sdk/'ld.exe'), '-Ttext=0x1f0200', '-e', 'dialogue_empty_width', '-o', str(out/'overlay.out'), str(out/'overlay.o')], check=True)
    subprocess.run([str(sdk/'objcopy.exe'), '-O', 'binary', str(out/'overlay.out'), str(out/'overlay.bin')], check=True)
    code = (out/'overlay.bin').read_bytes(); assert len(code) < 128
    names = {m[2]: int(m[1],16) for line in subprocess.check_output([str(sdk/'nm.exe'),str(out/'overlay.out')],text=True).splitlines()
             if (m := re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))}
    raw = bytearray(base); assert raw[0x1f0200:0x1f0200+len(code)] == b'\xff' * len(code)
    # D2 contains width; displaced comparison supplies flags to BGT at29626.
    assert raw[0x29620:0x29626].hex() == '0c85000000cf'
    raw[0x29620:0x29626] = bytes.fromhex('4ef9001f0200')
    # Compiler's special zero-terminator path must also bypass empty wrapping.
    assert raw[0x29b3e:0x29b46].hex() == '0c4700cf6300009c'
    raw[0x29b3e:0x29b46] = bytes.fromhex('4ef9') + names['dialogue_empty_terminator'].to_bytes(4,'big') + bytes.fromhex('4e71')
    raw[0x1f0200:0x1f0200+len(code)] = code
    raw[0x18e:0x190] = md_checksum(raw).to_bytes(2, 'big')
    allowed = {0x18e,0x18f} | set(range(0x29620,0x29626)) | set(range(0x29b3e,0x29b46)) | set(range(0x1f0200,0x1f0200+len(code)))
    assert all(n in allowed for n, (x,y) in enumerate(zip(base,raw)) if x != y)
    (out/'candidate.bin').write_bytes(raw)
    report = dict(private_candidate=True, base_sha256=digest,
                  md_sha256=hashlib.sha256(raw).hexdigest(), overlay_bytes=len(code),
                  all_other_bytes_identical=True, title_and_credits_overlays_unchanged=True,
                  source_basis='Original 05B2..05D0 dispatches empty/control characters before width checks; 066B only adds6 to X. Native empty word wrap adds an extra line before FF.',
                  selected_for_release=False, runtime_validation_required=True)
    report['scope']='Private room31 experiment, while house_dialogue_active is set. Other rooms and opening-story layout unchanged; not a general released repair.'
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__': main()
