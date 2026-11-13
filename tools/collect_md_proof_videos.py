"""Select independently proved MD movies with completed selected actions for the delivery."""
import hashlib,json
from pathlib import Path
from run_core import ROOT
from validate_playable_sprite_limit import symbols
from build_sms_proof_montage import title
SHA='1421abe47de95ac104a03e2fb1be7001f70aeca1fbb6a9b35669aa6e98b7d9a4'
def load(p):return json.loads(p.read_bytes())
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');clips=[];excluded=[];seen=set()
 for p in sorted((ROOT/'videos/md-annexes-2026-11-12').glob('*/report.json')):
  v=load(p);trace=v['trace'];reason=None
  if not v.get('passed') or v['rom_sha256']!=SHA:reason='unqualified_or_other_rom'
  elif 'stream-video-check' in trace:reason='technical_recorder_test'
  elif abs(v['fps']-59.92274339771384)>.000001:reason='PAL_evidence_retained_separately'
  folder=ROOT/'validation'/trace
  if reason:excluded.append(dict(trace=trace,reason=reason));continue
  r=load(folder/'report.json');cap=load(folder/'capture.json');raw=(folder/f'ram_{cap["frames"]:05d}.bin').read_bytes();word=lambda n:raw[sy[n]]|(raw[sy[n]+1]<<8)
  if not r.get('passed'):reason='approach_only_driver_without_selected_goal'
  remedy=trace=='natural-dungeon-combat/md-auto-annex-curse-remedy-contact-and-cure03' and r.get('curse_remedy_passed')
  if remedy:assert r['first_curse']['frame']<r['first_cure']['frame'] and not r['resource_or_actor_writes']
  interior_save=r.get('game_written_save') and r.get('payload_source_ram_exact') and not r.get('normal_exterior_exit_requested')
  if interior_save:assert r['save_written_frame'] and r['complete_frame'] and r['last_state']['phase']==0 and r['last_state']['room']==r['first_state']['room']
  if word('resume_phase') or (word('world_graphics_class') and not (remedy or interior_save)) or raw[sy['door_transition_loading']^1]:reason='exit_or_reveal_not_finished'
  if r.get('stop_on_lucky_requested') and not r.get('lucky_card_observed'):reason='unsuccessful_lucky_search_not_needed'
  if reason:excluded.append(dict(trace=trace,reason=reason));continue
  assert v['full_audio_video_decoded'] and v['final_ram_and_pixels_exact'] and not v['boss_assistance'];assert sha(ROOT/v['movie'])==v['movie_sha256'] and r['passed']
  proof=next(q for q in folder.parent.glob(folder.name+'*-replay*/replay_report.json') if sha(q)==v['proof_sha256']);w=load(proof);assert w['passed'] and w['final_png_exact'] and w['rom_sha256']==SHA
  if v['movie_sha256'] in seen:continue
  seen.add(v['movie_sha256']);economic=v.get('currency_assisted_component_test',False)
  if economic:assert trace=='natural-service-route/md-annex-key-capacity99-buy01' and w['inventory_actor_health_and_quest_writes']==0 and w['currency_refills']==99
  persistent=v.get('genuine_game_written_continue',False)
  if persistent:assert r['game_written_save'] and not r['synthetic_sram_fixture'] and not r['reload_ram_writes'] and r['raw_sram_fixed_replay_exact']
  heading=title(trace)
  if 'plain-' in trace:heading='Dialogue ordinaire : '+trace.split('plain-',1)[1]
  if 'gold-houses' in trace:heading='Maison : argent et retour sans recompense'
  if 'refusals' in trace and 'passage' not in trace or 'services-' in trace:heading='Service : refus puis sortie normale'
  if 'fairy' in trace:heading='Fee : capacite ou retour apres recompense'
  if 'teacher' in trace or 'learn' in trace:heading='Enseignement : apprentissage ou retour'
  if 'curse-remedy' in trace:heading='Corrosion : coup reel puis remede a l huile'
  if 'inn-' in trace:heading='Auberge : repos, paiement et retour'
  if 'save-' in trace or 'eren-' in trace:heading='Sauvegarde : ecriture ou Continuer normal'
  if 'passage-refusals' in trace:heading='Passage : Non, retour, paiement et traversee'
  clips.append(dict(trace=trace,report=p.relative_to(ROOT).as_posix(),movie=str((ROOT/v['movie']).resolve()),movie_sha256=v['movie_sha256'],frames=v['frames'],fps=v['fps'],title=heading,currency_assisted_component_test=economic,persistence_branch=persistent,proof_sha256=v['proof_sha256']))
 goals=load(ROOT/'analysis/md_selected_gameplay_goal_closure.json');included={r['report'] for r in clips};missing=[]
 for row in goals['cases']:
  if not row['verified']:missing.append(row['sms_trace']);continue
  paths={e.get('video_report',e.get('report')) for e in row['evidence']}
  if not paths&included:missing.append(row['sms_trace'])
 result=dict(passed=goals['passed'] and not missing,md_sha256=SHA,completed_clips=clips,excluded=excluded,missing_selected_goal_movies=missing,all_npcs_complete=False,scope='Finished actual native actions (stable interior save services need not leave the house), each cold replayed and fully AV-decoded. Failed searches, technical recorder clips, unfinished reveals and PAL clips are excluded from NTSC delivery.')
 (ROOT/'analysis/md_selected_proof_video_collection.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps(dict(passed=result['passed'],clips=len(clips),excluded=len(excluded),missing=missing)),flush=True)
if __name__=='__main__':main()
