"""Run current D9 stages sequentially, stopping on any failed gameplay/audit gate."""
import argparse,json,subprocess,sys,time
from run_core import ROOT
from archive_lossless_evidence import sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--wait-for-toll-pid',type=int);a=p.parse_args()
 digest='c53381c459a1e6254a8c9f1cfad1b8cda482cc0614697ad566133b28335e07a7'
 assert sha((ROOT/'gaw-megadrive.bin').read_bytes())==digest
 if a.wait_for_toll_pid:
  command=f"Get-CimInstance Win32_Process -Filter 'ProcessId={a.wait_for_toll_pid}' | Select-Object ProcessId,Name,CommandLine | ConvertTo-Json -Compress"
  def process():
   r=subprocess.run(['powershell','-NoProfile','-Command',command],capture_output=True,text=True,check=True)
   return json.loads(r.stdout)if r.stdout.strip()else None
  current=process()
  if current:assert current['Name']=='python.exe'and 'tools/guarded_exterior_toll_v0314.py'in current['CommandLine']
  print('Waiting for verified toll process',a.wait_for_toll_pid,flush=True)
  while current:
   time.sleep(2);current=process()
  print('Toll process terminal; inspecting actual report',flush=True)
 toll=json.loads((ROOT/'validation/natural-service-route/md-v0314-d9-earned-toll09/report.json').read_bytes())
 assert toll['passed']and not toll['failure']and toll['rom_sha256']==digest and toll['last_state']['gold']>=10
 assert not toll['currency_or_inventory_fixtures']and not toll['primary_state_imports']
 tools=['continue_d9_entry_v0314.py','summarize_d9_toll_v0314.py','summarize_d9_entry_v0314.py','summarize_d9_midboss_v0314.py','continue_d9_finish_v0314.py','summarize_d9_balloon_v0314.py','summarize_d9_campaign_v0314.py']
 for tool in tools:
  assert sha((ROOT/'gaw-megadrive.bin').read_bytes())==digest
  print('PIPELINE START',tool,flush=True)
  subprocess.run([sys.executable,'-u',str(ROOT/'tools'/tool)],cwd=ROOT,check=True)
  print('PIPELINE PASSED',tool,flush=True)
 print('D9 CURRENT-ROM CAMPAIGN AND AUDITS COMPLETE',flush=True)
if __name__=='__main__':main()
