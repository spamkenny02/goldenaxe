"""Read-only original IRQ status, VDP registers and live logical VRAM snapshots."""
import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from archive_lossless_evidence import sha
out=root/'validation/v319-chip-status-observer01';assert not out.exists();out.mkdir()
core=root.parents[1]/'work/genesis-plus-gx';source=core/'core/z80/z80.c';target=core/'genesis_plus_gx_v319_chip_status_libretro.dll';assert not target.exists()
original=source.read_bytes();needle=b'static void gaw_timing_observe(unsigned pc)\r\n{'
if needle not in original:needle=needle.replace(b'\r\n',b'\n')
assert original.count(needle)==1
observer=b'''struct gaw_chip_record {unsigned status,hardware,lines,line,delta,height;unsigned char regs[16],vram[16384];};
static struct gaw_chip_record gaw_chip_records[8];static unsigned gaw_chip_count,gaw_chip_errors;
__declspec(dllexport) void gaw_chip_reset(void) {gaw_chip_count=gaw_chip_errors=0;}
__declspec(dllexport) unsigned gaw_chip_size(void) {return gaw_chip_count;}
__declspec(dllexport) unsigned gaw_chip_errors_get(void) {return gaw_chip_errors;}
__declspec(dllexport) unsigned gaw_chip_stride(void) {return sizeof(struct gaw_chip_record);}
__declspec(dllexport) const unsigned char *gaw_chip_data(void) {return (const unsigned char *)gaw_chip_records;}
static void gaw_chip_observe(unsigned pc) {
 struct gaw_chip_record *e;if(pc!=0x137) return;
 if(gaw_chip_count>=8) {gaw_chip_errors++;return;}
 e=gaw_chip_records+gaw_chip_count++;e->status=work_ram[0x1b];e->hardware=system_hw;
 e->lines=lines_per_frame;e->line=v_counter;e->delta=Z80.cycles-mcycles_vdp;e->height=bitmap.viewport.h;
 memcpy(e->regs,reg,16);memcpy(e->vram,vram,16384);
}
'''
changed=original.replace(needle,observer+needle+b'\n gaw_chip_observe(pc);')
(out/'z80-before.c').write_bytes(original);(out/'z80-observer.c').write_bytes(changed)
try:
 source.write_bytes(changed)
 subprocess.run([sys.executable,str(root/'tools/build_timing_core.py'),'--target',target.name,'--log',str(out/'build.log'),'--force-source','core/z80/z80.c'],cwd=root,check=True)
finally:source.write_bytes(original)
assert source.read_bytes()==original
(out/'report.json').write_text(json.dumps(dict(passed=True,core=str(target),core_sha256=sha(target.read_bytes()),original_source_sha256=sha(original),original_source_restored=True,emulated_state_modifications=0,emulated_clock_modifications=0),indent=2)+'\n')
