"""Execute original 698B/193D and compare the production native decision."""
import argparse,contextlib,ctypes as c,io,json,subprocess
from run_core import ROOT,run
from archive_lossless_evidence import sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--trial',required=True);a=p.parse_args()
 folder=ROOT/('validation/crystal-bridge-policy-v0293-'+a.trial);assert not folder.exists();folder.mkdir()
 rows=[(hero,gem,flags,0) for hero in [0,1,5,9] for gem in [0,1,127,128,255] for flags in range(256)]
 original=(ROOT/'input/original.sms').read_bytes();image=bytearray(original)+bytearray(0x80000);code=bytearray();labels={};fix=[]
 def emit(s):code.extend(bytes.fromhex(s))
 def label(n):labels[n]=0x3000+len(code)
 def jp(op,n):emit(op);fix.append((len(code),n));emit('0000')
 emit('f331f0df2100c01101c001ff1f3600edb0af32fcff32fdff3e0132feff3e0a3208c0')
 # Original class0 mask table and unmodified 698B/193D remain in banks0/1.
 emit('2100802206c03e4932b9c0')
 label('case');emit('af3202c03205c03a08c032ffffdd2a06c0')
 emit('dd7e003201c3dd7e0132d3c0dd7e023249c1cd8b693e013202c00603')
 label('hold');emit('dbbfe680');jp('ca','hold');emit('05');jp('c2','hold')
 emit('2a06c011040019cb74');jp('ca','pointer');emit('2100803a08c03c3208c0')
 label('pointer');emit('2206c02a00c0232200c001'+len(rows).to_bytes(2,'little').hex()+'b7ed42');jp('c2','case')
 emit('af3202c03e013204c0');label('done');jp('c3','done')
 for p,n in fix:code[p:p+2]=labels[n].to_bytes(2,'little')
 image[:3]=bytes.fromhex('c30030');image[0x3000:0x3000+len(code)]=code
 image[0x28000:0x28000+len(rows)*4]=bytes(v for row in rows for v in row)
 # Intercept only the redraw/sound sink. The gate and original flag routine run.
 image[0x5e8b:0x5e91]=bytes.fromhex('3e013205c0c9')
 (folder/'source.sms').write_bytes(image);(folder/'cases.json').write_text(json.dumps(rows)+'\n');expected={};done=[]
 def observe(f,r):
  if r[4]:done.append(f)
  if r[2]:expected.setdefault(int.from_bytes(r[:2],'little'),(r[0x149],r[5]))
 with contextlib.redirect_stdout(io.StringIO()):run(folder/'source.sms',len(rows)*6+200,folder/'sms',set(),[],skip_intro=False,ram_observer=observe)
 assert done and len(expected)==len(rows),(len(expected),len(rows))
 (folder/'types.h').write_text('typedef unsigned char u8;typedef unsigned short u16;\n')
 subprocess.run(['C:/msys64/ucrt64/bin/gcc.exe','-shared','-O2','-std=c99','-I'+str(folder),str(ROOT/'megadrive/src/source_crystal_bridge.c'),'-o',str(folder/'policy.dll')],check=True)
 lib=c.CDLL(str(folder/'policy.dll'));fn=lib.source_crystal_bridge;fn.argtypes=[c.c_ushort,c.c_ubyte,c.POINTER(c.c_ubyte)];fn.restype=c.c_ushort
 for i,(hero,gem,flag,_) in enumerate(rows):
  value=c.c_ubyte(flag);redraw=fn(hero,gem,c.byref(value));assert (value.value,redraw)==expected[i],(i,rows[i],expected[i],value.value,redraw)
 report=dict(passed=True,cases=len(rows),source_sha256=sha(original),native_c_sha256=sha((ROOT/'megadrive/src/source_crystal_bridge.c').read_bytes()),source_patch='Only5E8B redraw/sound sink records one request;698B gate and193D flag side effect execute unchanged.',limits=['Controlled policy fixture; full redraw,VDP,sound and natural integration require separate game-loop evidence.'])
 (ROOT/'analysis/crystal_bridge_policy_v0293_report.json').write_text(json.dumps(report,indent=2)+'\n');print(report)

if __name__=='__main__':main()
