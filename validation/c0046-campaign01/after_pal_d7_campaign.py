"""Join the verified live D7 campaign controller, audit its closed stream, replay on V319."""
import argparse,ctypes,json,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[2]
k=ctypes.WinDLL('kernel32',use_last_error=True)
k.OpenProcess.argtypes=[ctypes.c_uint32,ctypes.c_int,ctypes.c_uint32];k.OpenProcess.restype=ctypes.c_void_p
k.WaitForSingleObject.argtypes=[ctypes.c_void_p,ctypes.c_uint32];k.WaitForSingleObject.restype=ctypes.c_uint32
k.GetExitCodeProcess.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_uint32)];k.CloseHandle.argtypes=[ctypes.c_void_p]
h=k.OpenProcess(0x100000|0x1000,False,a.pid)
assert h,'Controller handle missing: inspect terminal session before retrying; no automatic restart'
try:
    print('Following live D7 pipeline PID',a.pid,flush=True)
    assert k.WaitForSingleObject(h,0)==258,'Expected live controller'
    while k.WaitForSingleObject(h,1000)==258:pass
    code=ctypes.c_uint32();assert k.GetExitCodeProcess(h,ctypes.byref(code));assert code.value==0,('D7 campaign controller failed',code.value)
finally:k.CloseHandle(h)
r=json.loads((root/'analysis/pal_d7_v0319_report.json').read_bytes())
assert r['passed'] and r['pal_crystals_and_exterior_returns_verified']==7 and r['md_sha256']=='d3ea2a83ea24ed8a0d3c9857f9fbe70d000a4f73358452c1887f40e78966c56e'
project=root/'validation/c0046-campaign01/isolated/project'
assert not (project/'validation/palc0046-d8-entry-sources').exists()
subprocess.run([sys.executable,'-u','tools/continue_d8_entry_palc0046.py'],cwd=project,check=True)
