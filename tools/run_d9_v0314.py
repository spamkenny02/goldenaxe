"""Run current D9 stages sequentially, stopping on any failed gameplay/audit gate."""
import argparse,json,subprocess,sys,time
from run_core import ROOT
from archive_lossless_evidence import sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--wait-for-recovery-pid',type=int);p.add_argument('--wait-for-entry-pid',type=int);a=p.parse_args()
 assert not(a.wait_for_recovery_pid and a.wait_for_entry_pid)
 wait_pid=a.wait_for_entry_pid or a.wait_for_recovery_pid
 expected_tool='tools/continue_d9_entry_v0314.py'if a.wait_for_entry_pid else'tools/continue_d9_recovery_v0314.py'
 digest='c53381c459a1e6254a8c9f1cfad1b8cda482cc0614697ad566133b28335e07a7'
 assert sha((ROOT/'gaw-megadrive.bin').read_bytes())==digest
 if wait_pid:
  command=f"Get-CimInstance Win32_Process -Filter 'ProcessId={wait_pid}' | Select-Object ProcessId,Name,CommandLine | ConvertTo-Json -Compress"
  def process():
   r=subprocess.run(['powershell','-NoProfile','-Command',command],capture_output=True,text=True,check=True)
   return json.loads(r.stdout)if r.stdout.strip()else None
  current=process()
  if current:assert current['Name']=='python.exe'and expected_tool in current['CommandLine']
  print('Waiting for verified stage process',wait_pid,flush=True)
  while current:
   time.sleep(2);current=process()
  print('Stage process terminal; inspecting actual reports',flush=True)
 receipt=json.loads((ROOT/'analysis/d9_recovery_v0314_report.json').read_bytes())
 assert receipt['passed'] and receipt['md_sha256']==digest and receipt['eight_crystals_preserved'] and not receipt['currency_or_inventory_fixtures']
 tools=['continue_d9_entry_v0314.py','summarize_d9_entry_v0314.py','summarize_d9_midboss_v0314.py','continue_d9_finish_v0314.py','summarize_d9_balloon_v0314.py','summarize_d9_campaign_v0314.py']
 if a.wait_for_entry_pid:tools=tools[1:]
 for tool in tools:
  assert sha((ROOT/'gaw-megadrive.bin').read_bytes())==digest
  print('PIPELINE START',tool,flush=True)
  subprocess.run([sys.executable,'-u',str(ROOT/'tools'/tool)],cwd=ROOT,check=True)
  print('PIPELINE PASSED',tool,flush=True)
 print('D9 CURRENT-ROM CAMPAIGN AND AUDITS COMPLETE',flush=True)
if __name__=='__main__':main()
