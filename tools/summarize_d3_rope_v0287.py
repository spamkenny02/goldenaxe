"""Historical native v287 third dungeon and real rope, pinned to its build."""
import json
from run_core import ROOT
from rebase_natural_campaign import evidence
from archive_lossless_evidence import sha
from validate_playable_sprite_limit import symbols

def main():
 refs={}
 def read(n):
  b=evidence(ROOT/n);refs[n]=sha(b);return b
 def load(n):return json.loads(read(n))
 build=ROOT/'validation/v0287-d3-build';digest=sha(read('validation/v0287-d3-build/rom.bin'));assert digest=='58068350382a19ddc73a62eb747e42d978c36a1daf3c87f819e921f391b0065d';sy=symbols(build/'symbol.txt');stages=[]
 for base in ['natural-dungeon-route/md-v0287-d3-entry01']+['natural-dungeon-combat/md-auto-v0287-d3-'+n for n in ['rope01','evasive01','evasive02','exit05']]+['natural-rope-route/md-v0287-rope41-02']:
  base='validation/'+base;r=load(base+('/route_report.json' if '/natural-dungeon-route/' in base else '/report.json'));c=load(base+'/capture.json');a=load(base+'/assistance.json');proof=load(base+f"-assisted-fixed-replay-{c['frames']}/replay_report.json")
  assert c['rom_sha256']==r['rom_sha256']==proof['rom_sha256']==digest and proof['passed'] and proof['whole_ram_bytes']==65536 and proof['final_png_exact']
  assert not r.get('deaths',0) and r.get('failure') in [None,'frame_limit'] and len(a['episodes'])==2
  if a['release_write_frame']:assert max(v['frame'] for v in a['writes'])==a['release_write_frame']<a['first_boss_combat']['frame'] and a['first_boss_combat']['hurt']==0 and a['first_boss_damage'] is None
  stages.append(dict(trace=base,frames=c['frames'],state=r['last_state'],failure=r.get('failure'),full_ram_png_cold_replay=True,release_frame=a['release_write_frame']))
 assert stages[3]['state']['max_health']==56 and stages[3]['state']['progress']==128
 assert stages[4]['state']['dungeon']==0 and stages[4]['state']['health']==56 and stages[4]['state']['completed_dungeon_progress']==128
 comparisons=[]
 for native,source in [(stages[4]['trace'],'validation/natural-dungeon-combat/sms-auto-v0287-source-d3-exit02'),(stages[5]['trace'],'validation/natural-rope-route/sms-v0287-rope41-04')]:
  c=load(native+'/capture.json');sc=load(source+'/capture.json');b=read(native+f"/ram_{c['frames']:05d}.bin");s=read(source+f"/ram_{sc['frames']:05d}.bin");data=lambda n,k:bytes(b[(sy[n]+i)^1] for i in range(k))
  assert data('game_save_state',592)[0x50:0x150]==s[0x100:0x200] and data('sms_vram',16384)[0x3800:0x3d00]==s[0x1600:0x1b00] and data('hero_items',17)==s[0xe0:0xf1]
  comparisons.append(dict(native=native,source=source,flags_exact_bytes=256,map_exact_bytes=1280,items_exact_bytes=17))
 rope=load(stages[5]['trace']+'/report.json');source=load('validation/natural-rope-route/sms-v0287-rope41-04/report.json');normalize=lambda r:[(row['frame']-r['rope_activation_frame'],row['offset'],row['data_hex']) for row in r['rows']]
 assert normalize(rope)==normalize(source) and len(rope['rows'])==10
 stack=load('validation/stack-v0287-d3-rope-all/stack_report.json');assert stack['md_sha256']==digest and stack['all_instructions'] and not stack['invalid_heap_examples'];minimum=min(row['sp'] for row in stack['instruction_minima']);heap=stack['heap_changes'][-1]['end']+2;assert minimum>=heap
 for stem,ext in [('ram','bin'),('frame','png')]:assert read(f"validation/stack-v0287-d3-rope-all/{stem}_52989.{ext}")==read(stages[5]['trace']+f'/{stem}_52989.{ext}')
 for n in ['controls.json','ram_52989.bin','frame_52989.png']:assert read('validation/natural-rope-route/md-v0287-rope41-01/'+n)==read(stages[5]['trace']+'/'+n)
 motion=load('analysis/rope_motion_v0287_report.json');sms,md=motion['results'];ss=next(r for r in sms['rows'] if r['relative']==10);mm=next(r for r in md['rows'] if r['relative']==10);assert ss['terrain']==mm['terrain']==5 and ss['counter']==11 and mm['counter']==4
 base='validation/natural-dungeon-route/sms-v0287-source-d4-entry01';r=load(base+'/route_report.json');c=load(base+'/capture.json');proof=load(base+f"-assisted-fixed-replay-{c['frames']}/replay_report.json");assert r['reached_entrance'] and r['failure'] is None and r['live_prefix_terrain'] and proof['passed']
 result=dict(passed=True,md_sha256=digest,version=287,historical_build=True,stages=stages,source_comparisons=comparisons,rope_drawing_rows_exact=10,rope_movement_speed_mismatch_confirmed=dict(source_context=5,source_counter=11,native_counter=4,original_table_offset='33DB+5*17'),stack=dict(frames=52989,minimum_sp=minimum,heap_boundary=heap,observed_margin_bytes=minimum-heap,heap_valid=True),source_fourth_dungeon_entry=True,full_game_validated=False,evidence=refs,limits=['v287 only. Authorized approach guard ends before each boss; third boss and exit receive no new writes. The complete campaign includes assistance and is not labelled unassisted.','Third boss preserved48HP, crystal raises capacity to56; clean exit05 at56/56. Earlier blocked/dead exit controllers and log-only recovery in exit04 are retained; exit05 is a separate clean run and official replay.','Ten rope rows match source in order and one-frame cadence, but v287 walks too fast on the rope; v288 addresses the full terrain table selection.','Source comparison covers flags/map/item bytes, not all save data, encounters, remaining keys/gold, clock, waveform or hardware. Native/source fourth dungeon and remaining campaign are incomplete.'])
 (ROOT/'analysis/d3_rope_v0287_report.json').write_text(json.dumps(result,indent=2)+'\n');print('Historical v287 D3/rope proved; stack margin',minimum-heap)
if __name__=='__main__':main()
