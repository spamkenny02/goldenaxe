"""Validate current-ROM palace and ending only after the D9 campaign audit passes."""
import argparse,json,subprocess,sys,time
from run_core import ROOT
from archive_lossless_evidence import sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--wait-for-d9-pid',type=int);p.add_argument('--after-entry',action='store_true');p.add_argument('--after-giant',action='store_true');a=p.parse_args()
 assert not(a.after_entry and a.after_giant)
 digest='7694654ec85dd6626c0e17ff1834e5893d4eb35481400a4725eac6b6f3503294'
 assert sha((ROOT/'gaw-megadrive.bin').read_bytes())==digest
 if a.wait_for_d9_pid:
  command=f"Get-CimInstance Win32_Process -Filter 'ProcessId={a.wait_for_d9_pid}' | Select-Object Name,CommandLine | ConvertTo-Json -Compress"
  def process():
   r=subprocess.run(['powershell','-NoProfile','-Command',command],capture_output=True,text=True,check=True)
   return json.loads(r.stdout)if r.stdout.strip()else None
  current=process()
  if current:assert current['Name']=='python.exe'and 'tools/run_d9_v0317.py'in current['CommandLine']
  print('Waiting for verified D9 pipeline',a.wait_for_d9_pid,flush=True)
  while current:time.sleep(2);current=process()
 receipt=json.loads((ROOT/'analysis/d9_campaign_v0317_report.json').read_bytes())
 assert receipt['passed']and receipt['md_sha256']==digest and receipt['ninth_crystal_and_exterior_return']
 commands=[['continue_after_d9_v0317.py','palace'],['summarize_palace_entry_v0317.py'],['continue_palace_giant_v0317.py'],['summarize_palace_giant_v0317.py'],['continue_palace_inner_v0317.py'],['summarize_palace_inner_v0317.py'],['continue_palace_guardian_v0317.py'],['summarize_palace_guardian_v0317.py'],['continue_palace_final_v0317.py'],['summarize_palace_final_v0317.py'],['continue_after_d9_v0317.py','save']]
 if a.after_entry:
  entry=json.loads((ROOT/'analysis/cold_palace_entry_v0317_report.json').read_bytes())
  assert entry['passed'] and entry['md_sha256']==digest and entry['cold_palace_entered']
  commands=commands[2:]
 if a.after_giant:
  giant=json.loads((ROOT/'analysis/cold_palace_giant_v0317_report.json').read_bytes())
  assert giant['passed'] and giant['md_sha256']==digest and giant['cold_palace_giant_defeated']
  commands=commands[4:]
 for tool,*args in commands:
  assert sha((ROOT/'gaw-megadrive.bin').read_bytes())==digest
  print('PALACE PIPELINE START',tool,*args,flush=True)
  subprocess.run([sys.executable,'-u',str(ROOT/'tools'/tool),*args],cwd=ROOT,check=True)
  print('PALACE PIPELINE PASSED',tool,*args,flush=True)
 print('PALACE, ENDING AND NINE-CRYSTAL SAVE BRANCH VERIFIED; global fidelity audit remains separate',flush=True)
if __name__=='__main__':main()
