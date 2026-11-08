"""Build exact native credits-only overlay on auditedV319,without relinking game logic."""
import argparse,subprocess,json,hashlib,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--out',required=True);options=p.parse_args()
out=(ROOT/options.out).resolve();assert out.is_relative_to(ROOT/'validation') and not out.exists();out.mkdir(parents=True)
base=ROOT/'versions/v0319-d3ea2a83/gaw-megadrive-v0319.bin';raw=bytearray(base.read_bytes());assert hashlib.sha256(raw).hexdigest()=='d3ea2a83ea24ed8a0d3c9857f9fbe70d000a4f73358452c1887f40e78966c56e'
sdk=ROOT.parents[1]/'work/sgdk/bin';source=ROOT/'megadrive/overlays/credits_border.s';shutil.copyfile(source,out/source.name)
subprocess.run([str(sdk/'as.exe'),'-m68000','-o',str(out/'overlay.o'),str(out/source.name)],check=True)
subprocess.run([str(sdk/'ld.exe'),'-Ttext=0x1f0000','-e','credits_border_enter','-o',str(out/'overlay.out'),str(out/'overlay.o')],check=True)
subprocess.run([str(sdk/'objcopy.exe'),'-O','binary',str(out/'overlay.out'),str(out/'overlay.bin')],check=True)
symbols={r.split()[-1]:int(r.split()[0],16) for r in subprocess.check_output([str(sdk/'nm.exe'),str(out/'overlay.out')]).decode().splitlines() if len(r.split())==3}
payload=(out/'overlay.bin').read_bytes();assert len(payload)<512 and raw[0x1f0000:0x1f0000+len(payload)]==bytes([255])*len(payload)
hooks=[]
for site,expected,target in [(0x2144e,'47f900037bd6','credits_border_enter'),(0x226f6,'47f900037bd6','credits_border_enter'),(0x221e2,'4239e0ff2b78','credits_border_exit')]:
 assert raw[site:site+6].hex()==expected,(hex(site),raw[site:site+6].hex())
 replacement=bytes.fromhex('4eb9')+symbols[target].to_bytes(4,'big');raw[site:site+6]=replacement;hooks.append(dict(site=site,original=expected,replacement=replacement.hex(),target=symbols[target]))
raw[0x1f0000:0x1f0000+len(payload)]=payload
from finalize_md_rom import md_checksum
raw[0x18e:0x190]=md_checksum(raw).to_bytes(2,'big')
rom=out/'gaw-megadrive-candidate.bin';rom.write_bytes(raw)
allowed={0x18e,0x18f}|set(range(0x1f0000,0x1f0000+len(payload)))|{x for h in hooks for x in range(h['site'],h['site']+6)}
changed=[i for i,(a,b) in enumerate(zip(base.read_bytes(),raw)) if a!=b];assert all(i in allowed for i in changed)
report=dict(passed=True,md_sha256=hashlib.sha256(raw).hexdigest(),base_sha256=hashlib.sha256(base.read_bytes()).hexdigest(),overlay_sha256=hashlib.sha256(payload).hexdigest(),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),overlay_address=0x1f0000,overlay_bytes=len(payload),hooks=hooks,changed_bytes=len(changed),all_other_bytes_identical=True,checksum=raw[0x18e:0x190].hex().upper(),scope='Native68000 code only at two original credits-entry LEAs and one shared normal-exit CLR. Exact base and stolen instructions checked. Full game logic/audio/source arithmetic retain original binary layout and instruction work before credits.')
(out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
