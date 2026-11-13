"""Fit a boot-only bitmap/DAC presentation in the unused space of the exactV323 cartridge."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
from finalize_md_rom import md_checksum
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--diagnostic',action='store_true');p.add_argument('--sdk-bin',type=Path);a=p.parse_args();out=(ROOT/a.out).resolve();assert out.is_relative_to(ROOT/'validation') and not out.exists();out.mkdir(parents=True)
 sdk=(a.sdk_bin or ROOT/'../../work/sgdk/bin').resolve();src=ROOT/'megadrive/overlays';assets=ROOT/'megadrive/presentation';base=ROOT/'versions/v0323-9fcee16d/gaw-megadrive-v0323.bin';original=base.read_bytes();assert hashlib.sha256(original).hexdigest()=='9fcee16dc12028138712564ebd7123d99a25d1ef8f6e54d9799f02ceddaacd99'
 lines=['.section .rodata','.balign 4']
 for name,file in [('tiles','tiles.bin'),('map','map.bin'),('palette','palette.bin'),('ntsc','voice-ntsc.pcm'),('pal','voice-pal.pcm')]:
  lines += ['.balign 4',f'.global presentation_{name},presentation_{name}_end',f'presentation_{name}:',f'.incbin "{(assets/file).as_posix()}"',f'presentation_{name}_end:']
 if a.diagnostic:
  (out/'diagnostic-font.bin').write_bytes((assets/'diagnostic-font.bin').read_bytes())
  lines+=['.balign 4','.global presentation_diagnostic_font','presentation_diagnostic_font:',f'.incbin "{(out/"diagnostic-font.bin").as_posix()}"']
 (out/'assets.s').write_text('\n'.join(lines)+'\n',newline='\n')
 subprocess.run([str(sdk/'gcc.exe'),'-B'+str(sdk)+'/', *(['-DPRESENTATION_DIAGNOSTIC']if a.diagnostic else []),'-m68000','-Os','-fomit-frame-pointer','-fno-builtin','-fno-common','-c',str(src/'presentation.c'),'-o',str(out/'screen.o')],check=True)
 for name,file in [('hooks',src/'presentation_hooks.s'),('assets',out/'assets.s')]:subprocess.run([str(sdk/'as.exe'),*(['--defsym','PRESENTATION_DIAGNOSTIC=1']if a.diagnostic else []),'-m68000','-o',str(out/(name+'.o')),str(file)],check=True)
 extra=[]
 if a.diagnostic:
  for source,compiler,flags in [('presentation_diagnostic.c','gcc.exe',['-B'+str(sdk)+'/','-m68000','-Os','-fomit-frame-pointer','-fno-builtin','-c']),('presentation_diagnostic.s','as.exe',['-m68000'])]:
   target=out/(source+'.o');subprocess.run([str(sdk/compiler),*flags,str(src/source),'-o',str(target)],check=True);extra.append(str(target))
 subprocess.run([str(sdk/'ld.exe'),'-Ttext=0x120000','-e','presentation_entry','-o',str(out/'overlay.out'),str(out/'hooks.o'),str(out/'screen.o'),str(out/'assets.o'),*extra],check=True)
 subprocess.run([str(sdk/'objcopy.exe'),'-O','binary',str(out/'overlay.out'),str(out/'overlay.bin')],check=True);code=(out/'overlay.bin').read_bytes();assert len(code)<0xd0000
 names={m[2]:int(m[1],16) for line in subprocess.check_output([str(sdk/'nm.exe'),str(out/'overlay.out')],text=True).splitlines()if(m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))}
 raw=bytearray(original);assert raw[0x4876a:0x48772].hex()=='4e56ff4048e73f3c';raw[0x4876a:0x48772]=bytes.fromhex('4ef9')+names['presentation_entry'].to_bytes(4,'big')+bytes.fromhex('4e71')
 assert raw[0x120000:0x120000+len(code)]==b'\xff'*len(code)
 raw[0x120000:0x120000+len(code)]=code;raw[0x18e:0x190]=md_checksum(raw).to_bytes(2,'big');(out/'candidate.bin').write_bytes(raw)
 diagnostic_sites={0x4881e:('301008000000','presentation_diag_audio'),0x491b0:('301008000000','presentation_diag_audio'),0x4883a:('4eb900004bfc','presentation_diag_irq'),0x4891a:('4eb900032054','presentation_diag_sram'),0x48988:('4eb900009b6e','presentation_diag_intro')} if a.diagnostic else {}
 for site,(expected,name) in diagnostic_sites.items():
  assert original[site:site+6].hex()==expected
  raw[site:site+6]=bytes.fromhex('4eb9')+names[name].to_bytes(4,'big')
 if a.diagnostic:
  raw[0x18e:0x190]=md_checksum(raw).to_bytes(2,'big');(out/'candidate.bin').write_bytes(raw)
 allowed={site+j for site in diagnostic_sites for j in range(6)}|{0x18e,0x18f}|set(range(0x4876a,0x48772))|set(range(0x120000,0x120000+len(code)))
 assert all(i in allowed for i,(x,y)in enumerate(zip(original,raw))if x!=y)
 r=dict(passed=True,md_sha256=hashlib.sha256(raw).hexdigest(),base_sha256=hashlib.sha256(original).hexdigest(),bytes=len(raw),overlay_bytes=len(code),diagnostic=a.diagnostic,new_boot_only=not a.diagnostic,existing_game_and_konami_bytes_preserved=not a.diagnostic,sram_header_preserved=raw[0x1b0:0x1bc]==original[0x1b0:0x1bc],rom_resource_base=0x120000,unused_rom_bytes_before=0xd0000,unused_rom_bytes_after=0xd0000-len(code),quality_reduction_for_size=False,checksum=f'{md_checksum(raw):04X}',assets=json.loads((assets/'assets.json').read_bytes()),source_manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [src/'presentation.c',src/'presentation_hooks.s',*([src/'presentation_diagnostic.c',src/'presentation_diagnostic.s']if a.diagnostic else []),*assets.glob('*.bin'),*assets.glob('*.pcm')]},runtime_validation_required=True)
 (out/'build-report.json').write_text(json.dumps(r,indent=2)+'\n',newline='\n');print(json.dumps({k:v for k,v in r.items()if k not in ['source_manifest','assets']}),flush=True)
if __name__=='__main__':main()
