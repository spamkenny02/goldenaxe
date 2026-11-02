"""Freeze the scope of controlled palace phase1; never a full-campaign claim."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from assisted_prefix import recording,prefix_writes
from validate_playable_sprite_limit import symbols

CASES=[
 ('controlled-palace-route-v0309-02','palace entrance'),
 ('natural-dungeon-combat/md-auto-controlled-v0309-palace-panel16d01','inner room combat'),
 ('natural-dungeon-combat/md-auto-controlled-v0309-palace-switch16d01','western passage switch'),
 ('natural-dungeon-combat/md-auto-controlled-v0309-palace-pre-giant03','northern passage switch; hazards remain'),
 ('natural-dungeon-combat/md-auto-controlled-v0309-palace-giant-release01','guard release before giant'),
 ('natural-dungeon-combat/md-auto-controlled-v0309-palace-giant02','unassisted giant victory'),
 ('natural-dungeon-combat/md-auto-controlled-v0309-palace-approach-resume01','guard resumed after verified victory'),
 ('natural-dungeon-combat/md-auto-controlled-v0309-palace-portal14e01','live navigation checkpoint; controller stalled'),
 ('natural-dungeon-combat/md-auto-controlled-v0309-palace-portal14e02','arrival with one living secondary-slot enemy'),
 ('natural-dungeon-combat/md-auto-controlled-v0309-palace-clear14e01','all sixteen enemy slots checked empty'),
 ('natural-dungeon-combat/md-auto-controlled-v0309-palace-earth14e02','Earth and second portal'),
 ('natural-dungeon-combat/md-auto-controlled-v0309-palace-room11a01','live combat checkpoint; frame limit'),
 ('natural-dungeon-combat/md-auto-controlled-v0309-palace-earth11a01','Earth and southern passage'),
 ('natural-dungeon-combat/md-auto-controlled-v0309-palace-switch12901','live navigation checkpoint; controller stalled'),
 ('natural-dungeon-combat/md-auto-controlled-v0309-palace-switch12902','remote switch activated and return traversed')]


def main():
 rom=ROOT/'gaw-megadrive.bin';digest=sha(rom.read_bytes());assert digest=='7270576d6eeb2aee641776a3e364f2f3f320711d70bb91a566d7578161261049'
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');files={};stages=[];raws={};reports={};assists={}
 for relative,label in CASES:
  folder=ROOT/'validation'/relative;cap=json.loads((folder/'capture.json').read_bytes());r=json.loads((folder/'report.json').read_bytes());assist,writes=recording(folder,cap);assert cap['rom_sha256']==digest and cap['sram_input'] is not None and r['controlled_sram_fixture'] and r['natural_campaign_proof'] is False
  assert all(a==sy['hero_hurt'] and v in [b'\0\0',b'\0\x81'] for _,a,v in writes);assert prefix_writes(folder,cap,True,controlled=True)
  cold=folder.with_name(folder.name+'-assisted-fixed-replay-'+str(cap['frames']));proof=json.loads((cold/'replay_report.json').read_bytes());assert proof['passed'] and proof['controlled_sram_fixture'] and proof['primary_state_imports']==1 and proof['whole_ram_bytes']==65536 and proof['final_png_exact']
  for stem,ext in [('ram','bin'),('frame','png')]:assert (folder/f'{stem}_{cap["frames"]:05d}.{ext}').read_bytes()==(cold/f'{stem}_{cap["frames"]:05d}.{ext}').read_bytes()
  raw=(folder/f'ram_{cap["frames"]:05d}.bin').read_bytes();raws[relative]=raw;reports[relative]=r;assists[relative]=assist
  stages.append(dict(trace='validation/'+relative,scope=label,frames=cap['frames'],state=r['last_state'],whole_ram_png_exact=True,initial_state_imports=1,post_boot_resource_writes=0))
  for p in [folder/'capture.json',folder/'report.json',folder/'controls.json',folder/'assistance.json',folder/f'ram_{cap["frames"]:05d}.bin',folder/f'frame_{cap["frames"]:05d}.png',cold/'replay_report.json']:files[p.relative_to(ROOT).as_posix()]=sha(p.read_bytes())
 gate=reports[CASES[0][0]];assert gate['passed'] and gate['gate_opened']['frame']-gate['gate_started']['frame']==289
 giant=CASES[5][0];assert reports[giant]['room_cleared'] and reports[giant]['failure'] is None and reports[giant]['new_assistance_writes']==0
 assert reports[giant]['first_intermediate_combat']['hurt']==18 and reports[giant]['extension_guard_checks_through_frame']==stages[5]['frames']
 assert max(w['frame'] for w in assists[giant]['writes'])==14646
 r=raws[CASES[8][0]];a=bytes(r[(sy['world_actor_state']+i)^1] for i in range(768));assert a[14*48]==0x4c and a[14*48+24]==6
 r=raws[CASES[9][0]];a=bytes(r[(sy['world_actor_state']+i)^1] for i in range(768));assert not any(a[i] for i in range(0,768,48))
 for index in [10,12]:assert reports[CASES[index][0]]['earth_route_passed']
 assert reports[CASES[14][0]]['contact_route_passed']
 sram=ROOT/reports[CASES[0][0]]['sram_fixture'];assert all(x['sram_sha256']==sha(sram.read_bytes()) for x in reports.values())
 for name in ['analysis/palace_save_fixture_v0309-02_report.json','analysis/controlled_prefix_mode_v0309_report.json','tools/summarize_controlled_palace_phase1_v0309.py','megadrive/src/main.c','versions/v0309-7270576d/gaw-megadrive-v0309.bin']:files[name]=sha((ROOT/name).read_bytes())
 report=dict(passed=True,version=309,md_sha256=digest,controlled_sram_fixture=True,game_written_save=False,natural_campaign_proof=False,full_game_validated=False,initial_state_imports=1,post_boot_health_inventory_progression_writes=0,approach_guards_only=True,intermediate_boss_assistance=False,giant_prediction_windows=209,stages=stages,latest_trace=stages[-1]['trace'],latest_frames=stages[-1]['frames'],sram_sha256=sha(sram.read_bytes()),evidence=files,limits=['Synthetic Continue record derived from actual v306 nine-crystal RAM. Not a current-ROM campaign from New Game.','Live incomplete checkpoints in the input chain are identified explicitly; they are not victories.','The former first-eight-slots clear predicate stopped with a child4C alive. The child is killed in the following verified stage; all sixteen slots are checked.','Golden Axe,guardian7C,final boss,ending,full current cold campaign and global fidelity remain unvalidated by this phase.'])
 (ROOT/'analysis/controlled_palace_phase1_v0309_report.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print('Controlled palace phase1 verified:',len(stages),'independent full-RAM/PNG replays')

if __name__=='__main__':main()
