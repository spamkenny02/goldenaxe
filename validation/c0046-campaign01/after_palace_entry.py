"""Continue after the identified D9-to-palace pipeline exits successfully."""
import argparse,ctypes,json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
project=root/'validation/c0046-campaign01/isolated/project'
p=argparse.ArgumentParser();p.add_argument('--wait-for-pid',type=int,required=True);a=p.parse_args()
# Hold the exact Windows process handle, so PID reuse cannot satisfy this wait.
k=ctypes.WinDLL('kernel32',use_last_error=True)
k.OpenProcess.argtypes=(ctypes.c_uint32,ctypes.c_bool,ctypes.c_uint32);k.OpenProcess.restype=ctypes.c_void_p
k.WaitForSingleObject.argtypes=(ctypes.c_void_p,ctypes.c_uint32);k.WaitForSingleObject.restype=ctypes.c_uint32
k.GetExitCodeProcess.argtypes=(ctypes.c_void_p,ctypes.POINTER(ctypes.c_uint32));k.GetExitCodeProcess.restype=ctypes.c_bool
k.CloseHandle.argtypes=(ctypes.c_void_p,)
h=k.OpenProcess(0x100000|0x1000,False,a.wait_for_pid)
assert h,ctypes.get_last_error()
try:
    cmd=f"Get-CimInstance Win32_Process -Filter 'ProcessId={a.wait_for_pid}' | Select-Object Name,CommandLine | ConvertTo-Json -Compress"
    info=json.loads(subprocess.run(['powershell','-NoProfile','-Command',cmd],check=True,capture_output=True,text=True).stdout)
    assert info['Name']=='python.exe' and 'validation/c0046-campaign01/after_d9_finish.py' in info['CommandLine']
    print('Waiting on verified D9-to-palace process',a.wait_for_pid,flush=True)
    while k.WaitForSingleObject(h,2000)==258:pass
    code=ctypes.c_uint32();assert k.GetExitCodeProcess(h,ctypes.byref(code)) and code.value==0,code.value
finally:k.CloseHandle(h)
print('Starting palace finale only after the successful first-giant audit',flush=True)
subprocess.run([sys.executable,'-u','validation/c0046-campaign01/finish_palace.py'],cwd=root,check=True)
