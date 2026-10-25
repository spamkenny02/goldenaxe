"""Controlled fixture: unchanged SMS rope routines against production native C."""
import ctypes as c, hashlib, json, os, random, subprocess
from run_core import ROOT, run

def main():
    folder=ROOT/'validation/magic-rope';folder.mkdir(exist_ok=True)
    (folder/'types.h').write_text('#include <stdint.h>\ntypedef uint8_t u8;typedef uint16_t u16;\n')
    env=dict(os.environ);env['PATH']='C:/msys64/ucrt64/bin;'+env['PATH']
    module=ROOT/'megadrive/src/source_magic_rope.c'
    subprocess.run(['C:/msys64/ucrt64/bin/gcc.exe','-std=c99','-O2','-shared','-Wall','-Wextra','-Werror','-I'+str(folder),'-I'+str(module.parent),str(module),'-o',str(folder/'rope.dll')],env=env,check=True)
    lib=c.CDLL(str(folder/'rope.dll'));ptr=c.POINTER(c.c_uint8)
    lib.source_magic_rope_try.argtypes=[c.c_uint8]*5+[ptr,ptr]
    lib.source_magic_rope_tick.argtypes=[ptr,ptr,ptr,c.POINTER(c.c_uint16),ptr];lib.source_magic_rope_tick.restype=c.c_uint8
    original=(ROOT/'input/original.sms').read_bytes();rom=bytearray(original)
    rom[:3]=bytes.fromhex('c30030')
    # Controlled command1/2 activates source up/down. Command3/4 ticks IX workspace.
    code=bytearray();labels={};fix=[]
    def emit(h):code.extend(bytes.fromhex(h))
    def label(n):labels[n]=0x3000+len(code)
    def jump(op,n):emit(op);fix.append((len(code),n));emit('0000')
    emit('f331e0dfaf3200c0')
    label('wait');emit('3a00c0b7');jump('ca','wait')
    emit('dd2100c3fe01');jump('ca','up');emit('fe02');jump('ca','down')
    emit('dd2198c0fe03');jump('ca','tickup');emit('cd406d');jump('c3','done')
    label('tickup');emit('cd2c6d');jump('c3','done')
    label('up');emit('cdac38');jump('c3','done')
    label('down');emit('cdf638')
    label('done');emit('af3200c0');jump('c3','wait')
    for at,name in fix:code[at:at+2]=labels[name].to_bytes(2,'little')
    rom[0x3000:0x3000+len(code)]=code
    for start,end in [(0x38ac,0x393a),(0x6d2c,0x6d54),(0x6da6,0x6dea),(0x232f,0x234a)]:assert rom[start:end]==original[start:end]
    cartridge=folder/'controlled.sms';cartridge.write_bytes(rom)
    rng=random.Random(0x38ac);meta=rng.randbytes(2048);cases=[]
    # Include every integer x/y alignment, early rejects, edges and long columns.
    for direction in [0,1]:
        for x in range(0,256,8):
            for y in range(0,160,8):
                cells=bytearray([12]*256);idx=(((y-16)&240) if not direction else y&240)|(x>>4)
                cells[idx]=2 if not direction else 12
                if direction and idx+48<256:cells[idx+48]=2
                cases.append((direction+1,0,1,x,y,bytes(cells),rng.randbytes(4)))
    for i in range(256):
        direction=i&1;x=rng.randrange(256);y=rng.randrange(256)
        cells=bytearray(rng.choices([2,12,7,12],k=256))
        cases.append((direction+1,rng.choice([0,0,1,2]),rng.choice([0,1,255]),x,y,bytes(cells),rng.randbytes(4)))
    # Real source progressive drawing on valid visible row geometry.
    for state in [3,4]:
        for x in range(0,256,16):
            for y in range(0,160,8):
                cases.append((state,0,1,x,y,rng.randbytes(256),bytes([state,rng.choice([1,2,20,255]),y,x])))
    pending=[];checked=[]
    def prepare(i,frame):
        cmd,kind,owned,x,y,cells,work=cases[i]
        alignment=((x&8)>>3)|((y&8)>>2)|(128 if (x|y)&7 else 0)
        pending[:]=[(frame,0x900,meta),(frame,0x1600,bytes([0xa5])*1280),(frame,0x1c00,cells),(frame,0x40,bytes([kind])),(frame,0xed,bytes([owned])),(frame,0x6b,bytes([alignment])),(frame,0x311,bytes([y])),(frame,0x313,bytes([x])),(frame,0x98,work),(frame,0,bytes([cmd]))]
    def observe(frame,ram):
        if frame<10:return
        i=frame-10
        if i>=len(cases):return
        cmd,kind,owned,x,y,cells,work=cases[i]
        a=(c.c_uint8*256).from_buffer_copy(cells);w=(c.c_uint8*4).from_buffer_copy(work)
        assert ram[0]==0,('command',i)
        if cmd<3:lib.source_magic_rope_try(cmd-1,kind,owned,x,y,a,w)
        else:
            row=(c.c_uint8*4)();offset=c.c_uint16();m=(c.c_uint8*2048).from_buffer_copy(meta)
            assert lib.source_magic_rope_tick(a,m,w,c.byref(offset),row)
            assert ram[0x1600+offset.value:0x1604+offset.value]==bytes(row),('shadow row',i,offset.value)
            expected=bytearray([0xa5]*1280);expected[offset.value:offset.value+4]=bytes(row)
            assert ram[0x1600:0x1b00]==expected,('shadow extra writes',i)
        assert ram[0x1c00:0x1d00]==bytes(a),('cells',i)
        assert ram[0x98:0x9c]==bytes(w),('work',i,ram[0x98:0x9c].hex(),bytes(w).hex())
        checked.append(i)
        if i+1<len(cases):prepare(i+1,frame+1)
    prepare(0,10)
    run(cartridge,len(cases)+9,folder/'sms',set(),[],ram_writes=pending,skip_intro=False,ram_observer=observe)
    assert len(checked)==len(cases)
    report=dict(passed=True,cases=len(cases),tries=sum(t[0]<3 for t in cases),animation_rows=sum(t[0]>=3 for t in cases),source_sha256=hashlib.sha256(original).hexdigest(),module_sha256=hashlib.sha256(module.read_bytes()).hexdigest(),unchanged_source=['38AC..3939','6D2C..6D53','6DA6..6DE9','232F cell lookup'],checked=['all256 cells','all4 work bytes','entire1280-byte software map on drawing'],limits=['Controlled RAM inputs and boot wrapper, not a natural campaign proof.','Native VBlank publication and actual game rope use require integrated tests.'])
    (ROOT/'analysis/magic_rope_rules_report.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
