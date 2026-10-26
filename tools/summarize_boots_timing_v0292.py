"""Connect real boots acquisition to SMS/native movement-table comparisons."""
import json
from run_core import ROOT
from rebase_natural_campaign import evidence
from archive_lossless_evidence import sha
from validate_playable_sprite_limit import symbols

def main():
 refs={}
 def read(name):raw=evidence(ROOT/name);refs[name]=sha(raw);return raw
 def load(name):return json.loads(read(name))
 digest=sha(read('gaw-megadrive.bin'));bench=load('analysis/terrain_walk_v0292_game_report.json');assert bench['passed'] and bench['md_sha256']==digest and bench['source_sha256']==sha(read('input/original.sms')) and bench['controlled_fixture']
 assert len(bench['cases'])==48 and len(bench['results'])==2
 for r in bench['results']:assert not r['differences'] and r['cases']==48 and r['frames']==1536
 prefix='validation/natural-dungeon-combat/md-auto-v0292-d5-boots03';c=load(prefix+'/capture.json');r=load(prefix+'/report.json');proof=load(prefix+f'-assisted-fixed-replay-{c["frames"]}/replay_report.json');assert c['rom_sha256']==digest and r['room_cleared'] and r['last_state']['item_value']==1 and proof['passed']
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');raw=read(prefix+f'/ram_{c["frames"]:05d}.bin');owned=raw[(sy['hero_items']+14)^1];speed=int.from_bytes(bytes(raw[(sy['hero_attack_speed']+i)^1] for i in range(2)),'big');assert owned==speed==1
 read('tools/validate_terrain_walk_game.py')
 report=dict(passed=True,version=292,md_sha256=digest,acquired_boots_inventory_slot=14,actual_acquired_speed_selector=speed,controlled_fixture=True,regions=['auto','pal'],cases=96,frames_compared=3072,fields=['y_fixed8_8','x_fixed8_8','direction','animation','walking_counter','dy_fixed8_8','dx_fixed8_8','terrain_context'],differences=0,global_timing_validated=False,world_transition_timing_validated=False,evidence=refs,limits=bench['limits'])
 (ROOT/'analysis/boots_timing_v0292_report.json').write_text(json.dumps(report,indent=2)+'\n');print('Boots acquisition selects original speed row;96 controlled PAL/NTSC cases,3072 frame comparisons exact')

if __name__=='__main__':main()
