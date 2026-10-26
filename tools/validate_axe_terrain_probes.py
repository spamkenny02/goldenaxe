"""Execute source axe dispatch and232F; compare native cell probe indices."""
import contextlib,ctypes as c,io,itertools,json,os,subprocess
from run_core import ROOT,run
from archive_lossless_evidence import sha

def main():
 folder=ROOT/'validation/axe-terrain-probes-v0291-02';assert not folder.exists();folder.mkdir();module=ROOT/'megadrive/src/source_axe_terrain.c';(folder/'types.h').write_text('typedef unsigned char u8;\n');env=dict(os.environ);env['PATH']='C:/msys64/ucrt64/bin;'+env['PATH'];subprocess.run(['C:/msys64/ucrt64/bin/gcc.exe','-shared','-std=c99','-O2','-Wall','-Wextra','-Werror','-I'+str(folder),str(module),'-o',str(folder/'probes.dll')],env=env,check=True);lib=c.CDLL(str(folder/'probes.dll'));fn=lib.source_axe_terrain_probes;fn.argtypes=[c.c_ubyte]*5+[c.POINTER(c.c_ubyte)];fn.restype=c.c_ubyte
 source=(ROOT/'input/original.sms').read_bytes();rom=bytearray(source);code=bytearray();labels={};fix=[]
 def emit(h):code.extend(bytes.fromhex(h))
 def label(n):labels[n]=0x3000+len(code)
 def jp(op,n):emit(op);fix.append((len(code),n));emit('0000')
 emit('f331e0dfaf3200c0');label('wait');emit('3a00c0b7');jp('ca','wait');emit('dd2100c3af3290c0cdd334af3200c0');jp('c3','wait')
 for p,n in fix:code[p:p+2]=labels[n].to_bytes(2,'little')
 rom[:3]=bytes.fromhex('c30030');rom[0x3000:0x3000+len(code)]=code
 # Only intercept358D's terrain side effect. Actual table dispatch, edge
 # guards and original232F coordinate arithmetic execute unchanged.
 patch=bytes.fromhex('cd2f23453a90c05f16002191c01970'+'3a90c03c3290c0c9');rom[0x358d:0x358d+len(patch)]=patch
 (folder/'source.sms').write_bytes(rom)
 cases=list(itertools.product([0,1,2],[6,7,8],range(4),[0,7,8,16,24,120,128,232,240,248,255],[0,7,8,16,24,32,144,152,160,168,255]));pending=[];checked=[]
 def prepare(i,f):
  kind,phase,direction,x,y=cases[i];alignment=((x&8)>>3)|((y&8)>>2)|(128 if (x|y)&7 else 0)
  pending[:]=[(f,0x40,bytes([kind])),(f,0x30e,bytes([phase])),(f,0x30a,bytes([direction])),(f,0x311,bytes([y])),(f,0x313,bytes([x])),(f,0x6b,bytes([alignment])),(f,0x90,bytes(3)),(f,0,b'\1')]
 prepare(0,1)
 def observe(f,r):
  i=f-1
  if i>=len(cases):return
  assert not r[0]
  out=(c.c_ubyte*2)();count=fn(*cases[i],out);expected=bytes(r[0x91:0x91+r[0x90]]);actual=bytes(out[:count]);assert expected==actual,(cases[i],expected.hex(),actual.hex());checked.append(i)
  if i+1<len(cases):prepare(i+1,f+1)
 with contextlib.redirect_stdout(io.StringIO()):run(folder/'source.sms',len(cases)+1,folder/'sms',set(),[],skip_intro=False,ram_writes=pending,ram_observer=observe)
 assert len(checked)==len(cases)
 report=dict(passed=True,cases=len(cases),source_sha256=sha(source),native_c_sha256=sha(module.read_bytes()),scope='Original34D3 gate,34F0 jump table,3510..358D guard/probe dispatch and232F arithmetic;358D side effect intercepted to record indices. Tree mutation and hardware publication require separate game-loop tests.')
 (ROOT/'analysis/axe_terrain_probes_v0291_report.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print(report)
if __name__=='__main__':main()
