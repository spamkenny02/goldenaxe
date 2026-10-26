"""Execute original 7A09..7B30 decisions against the shared native C function."""
import contextlib,ctypes as c,io,itertools,json,subprocess
from run_core import ROOT,run
from archive_lossless_evidence import sha

def main():
 folder=ROOT/'validation/spell-teacher-v0289-policy';assert not folder.exists();folder.mkdir()
 rows=[]
 def add(t,level=0,hp=72,cap=24,gold=100,accept=1,intro=1,oil=1,crystals=128):
  state=[0]*21;state[t]=level;state[4:12]=[oil,intro,intro,0,hp,cap,7,gold];state[12:21]=[crystals]*9;rows.append(state+[t,255 if accept else 0]+[0]*9)
 for t,level,hp,gold,accept in itertools.product(range(4),[0,1,2,255],[0,71,72,255],[0,49,50,99,100,255],[0,1]):add(t,level,hp,gold=gold,accept=accept)
 for t,level,cap,intro,oil,crystals in itertools.product(range(4),[0,1],[0,24,103,104,127,128,232,255],[0,1,255],[0,1,255],[0,127,128,255]):add(t,level,cap=cap,intro=intro,oil=oil,crystals=crystals)
 for missing in range(9):
  add(2,1);rows[-1][12+missing]=127
 source=(ROOT/'input/original.sms').read_bytes();image=bytearray(source)+bytearray(0x80000);code=bytearray();labels={};fix=[]
 def emit(h):code.extend(bytes.fromhex(h))
 def label(n):labels[n]=0x3000+len(code)
 def jp(op,n):emit(op);fix.append((len(code),n));emit('0000')
 emit('f331f0df2100c01101c001ff1f3600edb0af32fcff32fdff3e0132feff3e04d3bf3e80d3bfafd3bf3e81d3bf2100802206c03e0a3208c0')
 label('case');emit('af3202c03290c03291c03292c03293c03a08c032ffffdd2a06c0')
 for i in range(32):emit(f'dd7e{i:02x}32{0x80+i:02x}c0')
 addresses=[0xe4,0xe5,0xe6,0xe7,0xe8,0xf3,0xf4,0xf5,0xda,0xdc,0xdb,0xdd]+list(range(0xcf,0xd8))
 for i,a in enumerate(addresses):emit(f'3a{0x80+i:02x}c032{a:02x}c0')
 # Reset recorded prompt PCs after the temporary row bytes have been consumed.
 emit('af3290c03291c03292c03293c03a95c0')
 for t,entry in enumerate([0x7a09,0x7a56,0x7ac8,0x7b09]):
  emit(f'fe{t:02x}');jp('c2',f'next{t}');emit('cd'+entry.to_bytes(2,'little').hex());jp('c3','ready');label(f'next{t}')
 label('ready');emit('3e013202c00603');label('hold');emit('dbbfe680');jp('ca','hold');emit('05');jp('c2','hold')
 emit('2a06c011200019cb74');jp('ca','pointer');emit('2100803a08c03c3208c0');label('pointer');emit('2206c02a00c0232200c001'+len(rows).to_bytes(2,'little').hex()+'b7ed42');jp('c2','case');emit('af3202c03e013204c0');label('done');jp('c3','done')
 for p,n in fix:code[p:p+2]=labels[n].to_bytes(2,'little')
 image[:3]=bytes.fromhex('c30030');image[0x3000:0x3000+len(code)]=code;image[0x28000:0x28000+len(rows)*32]=bytes(v for row in rows for v in row)
 image[0x779b:0x779f]=bytes.fromhex('2290c0c9');image[0x7444:0x7448]=bytes.fromhex('2292c0c9');image[0x77b1:0x77b7]=bytes.fromhex('3a96c0feffc9');image[0x1e41]=0xc9
 (folder/'source.sms').write_bytes(image);(folder/'cases.json').write_text(json.dumps(rows)+'\n');expected={};done=[]
 def observe(f,r):
  if r[4]:done.append(f)
  if r[2]:expected.setdefault(int.from_bytes(r[:2],'little'),(bytes(r[a] for a in addresses),int.from_bytes(r[0x90:0x92],'little'),int.from_bytes(r[0x92:0x94],'little')))
 with contextlib.redirect_stdout(io.StringIO()):run(folder/'source.sms',len(rows)*6+200,folder/'sms',set(),[],skip_intro=False,ram_observer=observe)
 assert done and len(expected)==len(rows),(len(expected),len(rows))
 (folder/'types.h').write_text('typedef unsigned char u8;typedef unsigned short u16;\n')
 gcc='C:/msys64/ucrt64/bin/gcc.exe';subprocess.run([gcc,'-shared','-O2','-std=c99','-I'+str(folder),str(ROOT/'megadrive/src/source_spell_teacher.c'),'-o',str(folder/'policy.dll')],check=True)
 lib=c.CDLL(str(folder/'policy.dll'));fn=lib.source_spell_teacher;fn.argtypes=[c.c_ubyte,c.c_ubyte,c.POINTER(c.c_ubyte),c.POINTER(c.c_ushort)];fn.restype=c.c_ushort
 for i,row in enumerate(rows):
  state=(c.c_ubyte*21)(*row[:21]);prompt=c.c_ushort();text=fn(row[21],bool(row[22]),state,c.byref(prompt));actual=(bytes(state),prompt.value,text);assert actual==expected[i],(i,row,expected[i],actual)
 report=dict(passed=True,cases=len(rows),source_sha256=sha(source),native_c_sha256=sha((ROOT/'megadrive/src/source_spell_teacher.c').read_bytes()),source_patches=['779B records prompt HL;7444 records final text HL;77B1 supplies explicit acceptance;1E41 returns instead of updating gold HUD. Original gold decrement loop and all policy branches remain.'],scope='Original isolated teacher decision routines versus compiled native C; service presentation, natural reachability and release ROM integration are not proven.',native_rom_integration=False)
 (ROOT/'analysis/spell_teacher_policy_report.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
