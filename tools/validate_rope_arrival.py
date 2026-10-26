"""Original19AB/19C6 rope arrival against production native C."""
import argparse,contextlib,ctypes as c,io,json,os,random,subprocess
from run_core import ROOT,run
from archive_lossless_evidence import sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--trial',default='01');a=p.parse_args();folder=ROOT/f'validation/rope-arrival-v0292-{a.trial}';assert not folder.exists();folder.mkdir();(folder/'types.h').write_text('typedef unsigned char u8;typedef unsigned short u16;typedef signed short s16;\n');module=ROOT/'megadrive/src/source_magic_rope.c';env=dict(os.environ);env['PATH']='C:/msys64/ucrt64/bin;'+env['PATH'];subprocess.run(['C:/msys64/ucrt64/bin/gcc.exe','-shared','-std=c99','-O2','-Wall','-Wextra','-Werror','-I'+str(folder),str(module),'-o',str(folder/'rope.dll')],env=env,check=True);lib=c.CDLL(str(folder/'rope.dll'));fn=lib.source_magic_rope_arrive;fn.argtypes=[c.c_ubyte]*4+[c.POINTER(c.c_ubyte)]
 original=(ROOT/'input/original.sms').read_bytes();rom=bytearray(original);code=bytes.fromhex('f331e0dfaf3200c03a00c0b728facdab19af3200c0c30830');rom[:3]=bytes.fromhex('c30030');rom[0x3000:0x3000+len(code)]=code;assert rom[0x19ab:0x1a02]==original[0x19ab:0x1a02];(folder/'source.sms').write_bytes(rom);rng=random.Random(0x19c6);cases=[]
 for direction in range(4):
  for x in range(0,256,8):
   for count in range(11):
    for terminal in [0,2,4]:
     cells=bytearray(256);col=x>>4
     for n in range(count):cells[(9-n if not direction else n)*16+col]=12
     if not direction:
      if count<10:cells[(9-count)*16+col]=terminal
     else:cells[count*16+col]=terminal
     cases.append((0,5,direction,x,bytes(cells)))
 for _ in range(720):cases.append((rng.choice([1,2,255]),rng.choice([0,3,4,5,255]),rng.randrange(4),rng.randrange(256),rng.randbytes(256)))
 for _ in range(512):cases.append((rng.choice([0,0,1]),rng.choice([0,5,5]),rng.randrange(4),rng.randrange(256),bytes(rng.choice([0,2,12,12,12,77]) for n in range(256))))
 pending=[];checked=[]
 def prepare(i,f):
  high,terrain,direction,x,cells=cases[i];pending[:]=[(f,0x40,b'\0'),(f,0xb9,bytes([0x95,high])),(f,0x41,bytes([terrain])),(f,0x30a,bytes([direction])),(f,0x313,bytes([x])),(f,0x1c00,cells),(f,0,b'\1')]
 prepare(0,1)
 def observe(f,r):
  i=f-1
  if i>=len(cases):return
  assert r[0]==0
  high,terrain,direction,x,cells=cases[i];native=(c.c_ubyte*256).from_buffer_copy(cells);fn(high,terrain,direction,x,native);assert bytes(native)==r[0x1c00:0x1d00],(i,cases[i][:4]);checked.append(i)
  if i+1<len(cases):prepare(i+1,f+1)
 with contextlib.redirect_stdout(io.StringIO()):run(folder/'source.sms',len(cases)+1,folder/'sms',set(),[],skip_intro=False,ram_writes=pending,ram_observer=observe)
 assert len(checked)==len(cases);report=dict(passed=True,cases=len(cases),source_sha256=sha(original),native_c_sha256=sha(module.read_bytes()),scope='Actual original19AB gate and19C6..1A01 execution compared over256 cell bytes. Production C preserves bounded map/scratch output; unusual original accesses beyond this map alias and DD00 queue timing are not asserted.')
 (ROOT/'analysis/rope_arrival_v0292_unit_report.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print(report)
if __name__=='__main__':main()
