"""Bind the acquired-canoe D5 approach to its official cold replay."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols

def main():
 refs={}
 def read(name):
  raw=evidence(ROOT/name);refs[name]=sha(raw);return raw
 def load(name):return json.loads(read(name))
 digest=sha(read('gaw-megadrive.bin'))
 assert digest==sha(read('versions/v0292-6eeb5608/gaw-megadrive-v0292.bin'))
 base='validation/natural-dungeon-route/'
 first=base+'md-v0292-d5-route03';fast=base+'md-v0292-d5-route04'
 r=load(first+'/route_report.json');c=load(first+'/capture.json')
 proof=load(first+f'-assisted-fixed-replay-{c["frames"]}/replay_report.json')
 assert r['failure'] is None and r['reached_entrance'] and r['directional_probe_succeeded'] and r['canoe_acquired_in_prefix']
 assert r['waypoints_reached']==r['waypoints_planned']==365 and not r['normal_continues']
 assert proof['passed'] and proof['whole_ram_bytes']==65536 and proof['final_png_exact'] and not proof['boss_assistance']
 assert proof['rom_sha256']==c['rom_sha256']==digest and c['sram_input'] is None
 a,w=recording(ROOT/first,c);read(first+'/assistance.json')
 assert a['boss_room']==0x163 and a['first_boss_combat'] is None and a['first_boss_entry'] is None and not a['health_refills']
 for n,h in proof['evidence'].items():assert sha(read(first+'/'+n))==h
 rf=load(fast+'/route_report.json');cf=load(fast+'/capture.json');af,wf=recording(ROOT/fast,cf);read(fast+'/assistance.json')
 assert rf==r and cf['frames']==c['frames'] and cf['rom_sha256']==digest and wf==w
 end=c['frames']
 for name in ['controls.json',f'ram_{end:05d}.bin',f'frame_{end:05d}.png']:assert read(first+'/'+name)==read(fast+'/'+name)
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');raw=read(first+f'/ram_{end:05d}.bin')
 data=lambda name,n:bytes(raw[(sy[name]+i)^1] for i in range(n))
 word=lambda name:int.from_bytes(data(name,2),'big')
 assert word('room_id')==0x186 and word('world_dungeon_number')==5 and word('hero_health')==62 and word('hero_max_health')==64
 assert data('hero_items',17)[12] and data('game_save_state',592)[0x1f:0x23]==bytes([128]*4)
 failed=load(base+'md-v0292-d5-route02/route_report.json');assert failed['failure']=='hero_died' and failed['last_state']['room']==0x48
 read('tools/natural_dungeon_route.py');read('tools/replay_assisted_prefix.py')
 report=dict(passed=True,rom_version=292,md_sha256=digest,frames=end,prefix_frame=r['prefix_end'],target_room=0x186,dungeon=5,health=62,max_health=64,canoe_acquired=True,four_previous_crystals_retained=True,assisted_approach=True,boss_room=0x163,boss_reached=False,boss_victory_validated=False,dungeon5_completed=False,ordinary_route_death_room=0x48,official_cold_replay_exact=True,whole_ram_bytes=65536,final_png_exact=True,optimized_controller_controls_ram_png_exact=True,completed_waypoints=365,source_campaign_or_global_timing_claim=False,evidence=refs)
 out=ROOT/'analysis/d5_approach_v0292_report.json';out.write_text(json.dumps(report,indent=2)+'\n');print(report)

if __name__=='__main__':main()
