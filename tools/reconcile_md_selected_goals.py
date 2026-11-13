"""Reconcile selected gameplay goals without relabelling diagnostic SMS traces as replayed.

The409-trace ledger remains an exact-reference diagnostic. This second register
checks retained business actions, their real native predicates, cold witnesses
and decoded movies. Different progression amounts are explicitly preserved.
"""
import json,hashlib,re
from pathlib import Path
from run_core import ROOT
from rebase_natural_campaign import evidence
from validate_playable_sprite_limit import symbols
SHA='1421abe47de95ac104a03e2fb1be7001f70aeca1fbb6a9b35669aa6e98b7d9a4'
def load(p):return json.loads(p.read_bytes())
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 ledger=load(ROOT/'analysis/md_annex_replay_coverage.json');selected=load(ROOT/'analysis/sms_points_3_4_closure.json')['selected_receipts'];direct={r['sms_trace']:r for r in ledger['cases']};videos={};sy=symbols(ROOT/'megadrive/out/release/symbol.txt');cache={}
 for p in sorted((ROOT/'videos/md-annexes-2026-11-12').glob('*/report.json')):
  v=load(p)
  if v.get('passed') and v.get('rom_sha256')==SHA:videos[v['trace']]=(p,v)
 def verified(trace,exterior=True):
  if trace in cache:return cache[trace]
  extension='natural-service-route/md-settled-'+trace.split('/')[-1]
  if extension in videos:
   er=load(ROOT/'validation'/extension/'report.json');assert er['settled_exit_extension_of']==trace
   ev,r=verified(extension,exterior);ev=dict(ev,superseded_partial_trace=trace);cache[trace]=(ev,r);return ev,r
  p,v=videos[trace];assert v['full_audio_video_decoded'] and v['final_ram_and_pixels_exact'] and not v['boss_assistance'];assert sha(ROOT/v['movie'])==v['movie_sha256']
  folder=ROOT/'validation'/trace;r=load(folder/'report.json');cap=load(folder/'capture.json');assert r['passed'] and cap['rom_sha256']==SHA and not r.get('primary_state_imports',0) and not r.get('sram_checkpoint_injection',False)
  proofs=list(folder.parent.glob(folder.name+'*-replay*/replay_report.json'));proof=next(x for x in proofs if sha(x)==v['proof_sha256']);w=load(proof);assert w['passed'] and w['final_png_exact'] and w['rom_sha256']==SHA
  raw=(folder/f'ram_{cap["frames"]:05d}.bin').read_bytes();word=lambda n:raw[sy[n]]|(raw[sy[n]+1]<<8)
  if exterior:assert word('resume_phase')==word('world_graphics_class')==0 and not raw[sy['door_transition_loading']^1]
  result=dict(trace=trace,video_report=p.relative_to(ROOT).as_posix(),video_report_sha256=sha(p),movie_sha256=v['movie_sha256'],producer_report_sha256=sha(folder/'report.json'),cold_replay_report=proof.relative_to(ROOT).as_posix(),cold_replay_sha256=sha(proof),source_capture_sha256=sha(folder/'capture.json'))
  cache[trace]=(result,r);return result,r
 bridges={}
 def add(source,trace,kind):bridges[source]=(trace,kind)
 ns='natural-service-route/'
 gifts={'sms-npc-equipment-27-gift01':'early-equipment-equipment-27','sms-npc-equipment-50-gift01':'early-equipment-equipment-50','sms-npc-d8-dragonmail-gift01':'late-equipment-equipment-b1','sms-npc-d8-flamesword-gift01':'late-equipment-equipment-6a','sms-npc-dragon-shield-gift02':'late-equipment-equipment-4c','sms-npc-hidden-rewards-92-gift01':'late-equipment-equipment-92','sms-npc-hidden-rewards-55-gift01':'late-equipment-equipment-55','sms-sms-npc-villagec7-oil02':'before-apple-saylun-apple'}
 for s,t in gifts.items():add(ns+s,ns+'md-annex-'+t+'-gift01','gift')
 for row in load(ROOT/'analysis/md_inn_campaign.json')['completed_visits']:
  s='sms-npc-paid-healer-2e-01' if row['outside']==0x2e else f"sms-npc-inn-location-{row['outside']:02x}-accept01";add(ns+s,row['trace'],'inn')
 for row in load(ROOT/'analysis/md_passage_campaign.json')['completed_visits']:
  s=next(x for x in selected if x.startswith(ns+f"sms-npc-passage-census-{row['outside']:02x}-pay"));add(s,row['trace'],'passage')
 for row in load(ROOT/'analysis/md_save_locations_campaign.json')['completed_locations']:
  s=ns+f"sms-npc-save-location-{row['outside']:02x}-slot0-01"
  if s in selected:add(s,row['save_trace'],'save')
 for name,kind in [('md_poor_services_campaign','poor'),('md_passage_refusals_campaign','passage_no'),('md_knight_shield_campaign','shield'),('md_inn_repeat_campaign','inn'),('md_curse_remedy_campaign','curse')]:
  p=ROOT/f'analysis/{name}.json'
  if not p.exists():continue
  j=load(p)
  for row in j.get('completed_visits',[j]):
   if row.get('sms_reference'):add(row['sms_reference'],row['trace'],kind)
 p=ROOT/'analysis/md_save_slots_2e_campaign.json'
 if p.exists():
  for row in load(p)['completed']:
   add(ns+f"sms-npc-save-2e-slot{row['slot']}-01",row['trace'],'save')
   if row['slot']==0:add(ns+'sms-npc-save-overwrite-2e-slot0-01',row['trace'],'save')
 for p in (ROOT/'analysis').glob('md_merchant_variant_*.json'):
  j=load(p)
  if j.get('passed'):add(j['sms_reference'],j['trace'],'merchant')
 j=load(ROOT/'analysis/md_lucky_card_campaign.json');add(j['sms_reference'],j['trace'],'lucky')
 rows=[]
 for source in selected:
  d=direct[source];item=dict(sms_trace=source,verified=False)
  if d['md_passed'] and d['fixed_replay_passed'] and d['video_verified']:
   item.update(verified=True,method='exact_source_reference',evidence=d['md_evidence'])
  elif source in bridges:
   trace,kind=bridges[source]
   if trace not in videos:rows.append(item);continue
   ev,r=verified(trace,kind!='curse');sr=json.loads(evidence(ROOT/'validation'/source/'report.json'));assert sr['passed'];detail={}
   if kind=='gift':
    assert r['outside']==sr.get('outside',sr.get('first_state',{}).get('outside')) and not r['new_assistance_writes'] and r['complete_frame']
    if 'gift_field' in r:
     field=r['gift_field'];assert r['reward_observed'] and r['first_state'][field]<r['expected_level']==r['last_state'][field];detail.update(field=field,level=r['expected_level'])
    else:
     assert r['reward_inventory_offset'] in (2,8) and r['visited']==[31,15,r['outside']] and r['first_state']['oil']==0 and r['last_state']['oil']==1;detail.update(reward=r['reward_name'],inventory_offset=r['reward_inventory_offset'],legacy_state_key='oil')
    assert r['last_state']['flags']&2
   elif kind=='inn':
    a,b=r['first_state'],r['last_state'];assert r['outside']==sr['outside'] and r['price']==sr['price'] and r['night_frame'] and r['reply_frame'] and r['complete_frame'];assert b['health']==b['max_health'] and a['gold']-b['gold']==r['price'] and a['magic']==b['magic'] and a['items']==b['items']
    detail.update(native_health_before=a['health'],native_max_health=a['max_health'],sms_health_before=sr.get('health_before'),native_actual_health_restoration=b['health']>a['health'],same_handler_damaged_restore_proof='natural-service-route/md-annex-inn-2e-pay01',frame_or_full_state_identity_claimed=False)
    if 'inn-repeat' in source:assert trace.startswith(ns+'md-annex-inn-repeat-')
   elif kind in ('passage','passage_no'):
    assert r['outside']==sr['outside'] and r['price']==10 and r['last_state']['room']==r['target'] and r['first_state']['gold']-r['last_state']['gold']==10 and not r['new_assistance_writes']
    if kind=='passage_no':assert r['no_resources_flags_and_passage_blocking_unchanged'] and r['no_confirmation_frame']<r['walked_away_before_return_frame']<r['complete_frame']
   elif kind=='save':
    assert r['slot']==sr['slot'] and r['game_written_save'] and r['payload_source_ram_exact'] and r['normal_exterior_exit_requested'] and not r['new_assistance_writes'];assert sha(ROOT/r['sram_file'])==r['sram_sha256']
    if 'overwrite' in source:assert r['overwrite_requested']
    related=[]
    for p in (ROOT/'videos/md-annexes-2026-11-12').glob('*/report.json'):
     v=load(p)
     if v.get('genuine_game_written_continue'):
      cr=load(ROOT/'validation'/v['trace']/'report.json')
      if cr.get('source_trace',cr.get('trace'))==trace:
       assert cr['passed'] and cr['raw_sram_fixed_replay_exact'] and cr['save_whole_ram_png_exact'] and cr['source_sram_sha256']==r['sram_sha256'] and cr['reload_ram_writes']==0
       assert v['passed'] and v['full_audio_video_decoded'] and v['final_ram_and_pixels_exact'] and sha(ROOT/v['movie'])==v['movie_sha256'];related.append(p.relative_to(ROOT).as_posix())
    assert related,'Every mapped save requires its own genuine normal Continue video'
    detail.update(slot=r['slot'],normal_continue_videos=related,sram_sha256=r['sram_sha256'])
   elif kind=='poor':assert r['resources_and_flags_unchanged'] and r['poor_sms_bitmap_exact_frame'] and r['gold']<r['cost'] and not r['new_assistance_writes']
   elif kind=='shield':assert r['first_state']['shield']==1 and r['last_state']['shield']==2 and r['first_state']['gold']-r['last_state']['gold']==250 and not r['new_assistance_writes']
   elif kind=='merchant':assert r['choices']==sr['choices'] and len(r['completed'])==len(sr['choices']) and all(v['bitmap_exact_bytes']==1040 for v in r['completed']) and not r['new_assistance_writes']
   elif kind=='lucky':assert r['lucky_card_observed'] and any(o['special_card']==0x38 for o in r['outcomes']) and not r['new_assistance_writes']
   elif kind=='curse':
    j=load(ROOT/'analysis/md_curse_remedy_campaign.json');assert j['passed'] and j['first_curse']['frame']<j['first_cure']['frame'] and j['resource_or_actor_writes']==0;detail.update(first_curse=j['first_curse'],first_cure=j['first_cure'])
   else:raise AssertionError(kind)
   item.update(verified=True,method='typed_gameplay_predicates',predicate=kind,evidence=[ev],details=detail,sms_producer_sha256=hashlib.sha256(evidence(ROOT/'validation'/source/'report.json')).hexdigest())
  rows.append(item)
 cohorts=[]
 for name,field,count in [('md_plain_house_census_campaign','completed_houses',41),('md_service_refusal_campaign','completed_visits',48),('md_gold_house_campaign','completed_houses',31),('md_magic_fairy_campaign','completed_visits',12),('md_reward_returns_campaign','completed_visits',12)]:
  path=ROOT/f'analysis/{name}.json';j=load(path);entries=j[field];assert len(entries)==count
  claims=[]
  for row in entries:
   ev,r=verified(row['trace']);claims.append(ev)
   if name=='md_plain_house_census_campaign':assert all(v['bitmap_exact_bytes']==1040 and v['acknowledged_and_walked_away_frame'] for v in row['conversations'])
  if name=='md_plain_house_census_campaign':assert sum(len(v['conversations']) for v in entries)==65
  cohorts.append(dict(report=path.relative_to(ROOT).as_posix(),report_sha256=sha(path),known_contexts=count,evidence=claims))
 completed=sum(x['verified'] for x in rows);report=dict(passed=completed==len(selected),md_sha256=SHA,required_selected_gameplay_goals=len(selected),verified_selected_gameplay_goals=completed,cases=rows,supplemental_known_context_cohorts=cohorts,all_npcs_complete=False,exact_reference_ledger='analysis/md_annex_replay_coverage.json',diagnostic_recording_traces=len(ledger['cases']),scope='Actual selected gameplay actions, not frame-identical SMS states. Typed bridges retain different progression amounts; exact-reference409-trace ledger is not overwritten. No missing technical checkpoint is silently credited.',known_limits=['Untriggered SMS DA58/DA7C/ED3C are not declared unused.','Two unlocated money table rows remain unresolved.','Saylun owned-apple final SMS duplicate suffix differs; complete original phrase matches at formatter return.'])
 (ROOT/'analysis/md_selected_gameplay_goal_closure.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print(json.dumps(dict(passed=report['passed'],verified=completed,required=len(selected),missing=[r['sms_trace'] for r in rows if not r['verified']])),flush=True)
if __name__=='__main__':main()
