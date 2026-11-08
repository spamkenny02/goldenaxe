"""Join the verified live PAL palace ending pipeline, audit its closed stream, replay on V319."""
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
    print('Following live PAL palace ending pipeline PID',a.pid,flush=True)
    assert k.WaitForSingleObject(h,0)==258,'Expected live controller'
    while k.WaitForSingleObject(h,1000)==258:pass
    code=ctypes.c_uint32();assert k.GetExitCodeProcess(h,ctypes.byref(code));assert code.value==0,('PAL palace ending pipeline failed',code.value)
finally:k.CloseHandle(h)
subprocess.run([sys.executable,'validation/c0046-campaign01/audit_pal_palace_inner.py','--through','ending'],cwd=root,check=True)
subprocess.run([sys.executable,'-u','validation/replay_c0047_pal.py','--report','analysis/palc0046_palace_ending_report.json','--milestone','ending'],cwd=root,check=True)
print('PAL palace, Death Adder, complete credits and intro return audited and replayed on V319',flush=True)
