"""Validate current-ROM palace and ending only after the D9 campaign audit passes."""
import argparse,json,subprocess,sys,time
from run_core import ROOT
from archive_lossless_evidence import sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--wait-for-d9-pid',type=int);a=p.parse_args()
 digest='c53381c459a1e6254a8c9f1cfad1b8cda482cc0614697ad566133b28335e07a7'
 assert sha((ROOT/'gaw-megadrive.bin').read_bytes())==digest
 if a.wait_for_d9_pid:
  command=f"Get-CimInstance Win32_Process -Filter 'ProcessId={a.wait_for_d9_pid}' | Select-Object Name,CommandLine | ConvertTo-Json -Compress"
  def process():
   r=subprocess.run(['powershell','-NoProfile','-Command',command],capture_output=True,text=True,check=True)
   return json.loads(r.stdout)if r.stdout.strip()else None
  current=process()
  if current:assert current['Name']=='python.exe'and 'tools/run_d9_v0314.py'in current['CommandLine']
  print('Waiting for verified D9 pipeline',a.wait_for_d9_pid,flush=True)
  while current:time.sleep(2);current=process()
 receipt=json.loads((ROOT/'analysis/d9_campaign_v0314_report.json').read_bytes())
 assert receipt['passed']and receipt['md_sha256']==digest and receipt['ninth_crystal_and_exterior_return']
 commands=[['continue_after_d9_v0314.py','palace'],['summarize_palace_entry_v0314.py'],['continue_palace_giant_v0314.py'],['summarize_palace_giant_v0314.py'],['continue_palace_inner_v0314.py'],['summarize_palace_inner_v0314.py'],['continue_palace_guardian_v0314.py'],['summarize_palace_guardian_v0314.py'],['continue_palace_final_v0314.py'],['summarize_palace_final_v0314.py'],['continue_after_d9_v0314.py','save']]
 for tool,*args in commands:
  assert sha((ROOT/'gaw-megadrive.bin').read_bytes())==digest
  print('PALACE PIPELINE START',tool,*args,flush=True)
  subprocess.run([sys.executable,'-u',str(ROOT/'tools'/tool),*args],cwd=ROOT,check=True)
  print('PALACE PIPELINE PASSED',tool,*args,flush=True)
 print('PALACE, ENDING AND NINE-CRYSTAL SAVE BRANCH VERIFIED; global fidelity audit remains separate',flush=True)
if __name__=='__main__':main()
