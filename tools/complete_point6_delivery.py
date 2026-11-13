"""Run dependent delivery gates in order; stop on the first failure."""
import argparse,subprocess,sys,json,time
from run_core import ROOT

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--from-stage',type=int,choices=range(1,9),default=1);args=parser.parse_args()
 print('WAITING FOR FINAL PRODUCER PROOFS',flush=True)
 for attempt in range(240):
  paths=[ROOT/'analysis'/name for name in ['md_fresh_save_2e_campaign.json','md_save_slots_2e_campaign.json','md_merchant_variant_magic32-poor.json']]
  if all(p.exists() and json.loads(p.read_bytes()).get('passed') for p in paths):break
  time.sleep(5)
 else:raise TimeoutError('Final producer proofs not completed within20minutes')
 fresh=json.loads((ROOT/'analysis/md_fresh_save_2e_campaign.json').read_bytes());slots=json.loads((ROOT/'analysis/md_save_slots_2e_campaign.json').read_bytes());magic=json.loads((ROOT/'analysis/md_merchant_variant_magic32-poor.json').read_bytes());assert fresh['passed'] and slots['passed'] and magic['passed']
 stages=[('summarize_md_annex_replay.py',[]),('reconcile_md_selected_goals.py',[]),('collect_md_proof_videos.py',[]),('build_md_proof_montage.py',[]),('verify_md_montage_boundaries.py',[]),('finalize_rc_release.py',[]),('version_rom.py',['--release-candidate','rc1','--report','analysis/rc1_release_report.json','--notes','RC1 : parcours PAL/NTSC et 145 objectifs retenus rejoues ; montages SMS/MD livres. Limites de couverture et fidelite documentees. Binaire V322 identique.']),('publish_point6_summary.py',[])]
 for number,(tool,stage_args) in enumerate(stages,1):
  if number<args.from_stage:continue
  print('DELIVERY STAGE',number,len(stages),tool,flush=True)
  (ROOT/'validation/point6-delivery-progress.json').write_bytes((json.dumps(dict(stage=tool,number=number,total=len(stages),started=time.time()))+'\n').encode())
  with (ROOT/'validation'/('point6-delivery-'+tool.removesuffix('.py')+'.log')).open('w') as log:subprocess.run([sys.executable,str(ROOT/'tools'/tool),*stage_args],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
  print('DELIVERY STAGE PASSED',tool,flush=True)
 print('ALL POINT6 DELIVERY GATES PASSED',flush=True)
if __name__=='__main__':main()
