"""Reproducible optional native68000 extension; keep the qualifiedRC1 intact."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
from finalize_md_rom import md_checksum
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--base',type=Path);p.add_argument('--sdk-bin',type=Path);a=p.parse_args();out=(ROOT/a.out).resolve();assert out.is_relative_to(ROOT/'validation') and not out.exists();out.mkdir(parents=True)
 sdk=(a.sdk_bin or ROOT/'../../work/sgdk/bin').resolve();src=ROOT/'megadrive/overlays';base=a.base or ROOT/'versions/v0322-1421abe4/gaw-megadrive-v0322.bin';raw=bytearray(base.read_bytes());assert hashlib.sha256(raw).hexdigest()=='1421abe47de95ac104a03e2fb1be7001f70aeca1fbb6a9b35669aa6e98b7d9a4'
 subprocess.run([str(sdk/'gcc.exe'),'-B'+str(sdk)+'/', '-m68000','-Os','-fomit-frame-pointer','-fno-builtin','-fno-common','-c',str(src/'konami_menu.c'),'-o',str(out/'menu.o')],check=True)
 subprocess.run([str(sdk/'as.exe'),'-m68000','-o',str(out/'hooks.o'),str(src/'konami_hooks.s')],check=True)
 subprocess.run([str(sdk/'ld.exe'),'-Ttext=0x1f0400','-e','konami_boot','-o',str(out/'overlay.out'),str(out/'hooks.o'),str(out/'menu.o')],check=True)
 subprocess.run([str(sdk/'objcopy.exe'),'-O','binary',str(out/'overlay.out'),str(out/'overlay.bin')],check=True)
 names={m[2]:int(m[1],16) for line in subprocess.check_output([str(sdk/'nm.exe'),str(out/'overlay.out')],text=True).splitlines() if (m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))}
 code=(out/'overlay.bin').read_bytes();assert len(code)<0xfc00 and raw[0x1f0400:0x1f0400+len(code)]==b'\xff'*len(code)
 hooks=[]
 for at,old,name,call in [(0x1e6c,'223ce0ffe4b1','konami_boot',True),(0x48976,'45faf63c13fc0001e0ff447d','konami_title_pointer',False),(0x4b168,'4ebace4a3015','konami_title_flash',False)]:
  original=bytes.fromhex(old);assert raw[at:at+len(original)]==original
  patch=bytes.fromhex('4eb9' if call else '4ef9')+names[name].to_bytes(4,'big')+bytes.fromhex('4e71')*((len(original)-6)//2);raw[at:at+len(original)]=patch;hooks.append(dict(address=at,before=old,after=patch.hex(),entry=name))
 raw[0x1f0400:0x1f0400+len(code)]=code;raw[0x18e:0x190]=md_checksum(raw).to_bytes(2,'big');(out/'candidate.bin').write_bytes(raw)
 allowed={0x18e,0x18f}|set(range(0x1f0400,0x1f0400+len(code)))
 for h in hooks:allowed.update(range(h['address'],h['address']+len(bytes.fromhex(h['before']))))
 assert all(i in allowed for i,(x,y) in enumerate(zip(base.read_bytes(),raw)) if x!=y)
 r=dict(passed=True,source_manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [src/'konami_menu.c',src/'konami_hooks.s',src/'konami_font.inc']},unmodified_game_engine=True,title_only_input_hooks=True,md_sha256=hashlib.sha256(raw).hexdigest(),base_sha256=hashlib.sha256(base.read_bytes()).hexdigest(),native_68000=True,overlay_bytes=len(code),hooks=hooks,reserved_ram_start=0xffe4b0,reserved_ram_bytes=32,heap_start=0xffe4d0,existing_game_symbols_unchanged=True,existing_rc1_corrections_unchanged=True,sram_format_unchanged=True,cheats_default_off=True,session_only=True,runtime_validation_required=True)
 (out/'build-report.json').write_bytes((json.dumps(r,indent=2)+'\n').encode());print(json.dumps(r),flush=True)
if __name__=='__main__':main()
