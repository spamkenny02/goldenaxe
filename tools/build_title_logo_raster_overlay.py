"""Build a private title raster candidate on exact V321; no relink."""
import argparse,hashlib,json,subprocess,shutil
from run_core import ROOT
from finalize_md_rom import md_checksum
p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();out=(ROOT/a.out).resolve();assert out.is_relative_to(ROOT/'validation') and not out.exists();out.mkdir(parents=True)
base=(ROOT/'versions/v0321-89c58333/gaw-megadrive-v0321.bin').read_bytes();assert hashlib.sha256(base).hexdigest()=='89c5833351312ffaa591efb1939161910a298af06437080e2cf84fb3fb8ac86e';raw=bytearray(base);sdk=ROOT.parents[1]/'work/sgdk/bin';source=ROOT/'megadrive/overlays/title_logo_raster.s'
subprocess.run([str(sdk/'as.exe'),'-m68000','-o',str(out/'overlay.o'),str(source)],check=True)
subprocess.run([str(sdk/'ld.exe'),'-Ttext=0x1f0200','-e','title_copy_logo_row','-o',str(out/'overlay.out'),str(out/'overlay.o')],check=True)
subprocess.run([str(sdk/'objcopy.exe'),'-O','binary',str(out/'overlay.out'),str(out/'overlay.bin')],check=True)
shutil.copyfile(source,out/source.name)
payload=(out/'overlay.bin').read_bytes();assert len(payload)<4096;assert raw[0x1f0200:0x1f0200+len(payload)]==bytes([255])*len(payload)
assert raw[0x4af7c:0x4af82].hex()=='4eb9000005e8';raw[0x4af7c:0x4af82]=bytes.fromhex('4eb9001f0200');raw[0x1f0200:0x1f0200+len(payload)]=payload;raw[0x18e:0x190]=md_checksum(raw).to_bytes(2,'big');(out/'gaw-megadrive-candidate.bin').write_bytes(raw)
report=dict(md_sha256=hashlib.sha256(raw).hexdigest(),base_sha256=hashlib.sha256(base).hexdigest(),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),overlay_bytes=len(payload),runtime_validation_required=True,selected_for_release=False,experimental_lead_in_nops=454,source_irq_phase_model_complete=False);(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
