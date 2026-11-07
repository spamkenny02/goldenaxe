"""Continue only after the currently running, identified D9 process exits successfully."""
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
    assert info['Name']=='python.exe' and 'tools/continue_d9_finish_c0046.py' in info['CommandLine']
    print('Waiting on verified D9 process',a.wait_for_pid,flush=True)
    while k.WaitForSingleObject(h,2000)==258:pass
    code=ctypes.c_uint32();assert k.GetExitCodeProcess(h,ctypes.byref(code)) and code.value==0,code.value
finally:k.CloseHandle(h)
stream=json.loads((project/'validation/c0046-d9-sources04/finish-cold-stream/completed.json').read_bytes())
assert stream['passed'] and len(stream['checkpoints'])==12 and all(s['whole_ram_png_exact'] for s in stream['checkpoints'])
commands=[(project,'tools/summarize_d9_balloon_c0046.py',[]),
          (root,'validation/c0046-campaign01/archive_d9_finish.py',['--balloon-only']),
          (project,'tools/summarize_d9_campaign_c0046.py',[]),
          (root,'validation/c0046-campaign01/archive_d9_finish.py',[]),
          (root,'validation/replay_c0047_d1.py',['auto','--dungeon','9']),
          (project,'tools/continue_after_d9_c0046.py',['palace']),
          (project,'tools/summarize_palace_entry_c0046.py',[]),
          (project,'tools/continue_palace_giant_c0046.py',[]),
          (project,'tools/summarize_palace_giant_c0046.py',[])]
for cwd,tool,args in commands:
    print('D9 FOLLOWUP START',tool,*args,flush=True)
    subprocess.run([sys.executable,'-u',tool,*args],cwd=cwd,check=True)
    print('D9 FOLLOWUP PASSED',tool,flush=True)
print('D9 audit, c0047 replay, owned overview, palace entry and first giant verified; finale still open',flush=True)
