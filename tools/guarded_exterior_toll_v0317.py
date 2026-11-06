"""Declared D9 approach protection around real exterior combat; no resource writes."""
import json,sys
import natural_exterior_toll_v0317 as coins
import natural_dungeon_route as world
import assisted_boss_route as guard
from run_core import ROOT
from assisted_prefix import recording
coins.GUARDED=True
coins.TRIAL='md-v0317-d9-earned-toll10'
coins.run=lambda *a,**k:world.run(*a,**k)
world.main=coins.main
if __name__=='__main__':
 sys.argv=[sys.argv[0],'--boss-room','0x1ac','--world-route','--release-near-coins','--new-assistance-episode','--assisted-prefix','--prefix-combat','md-auto-v0317-d8-exit01']
 guard.main()
 out=ROOT/'validation/natural-service-route'/coins.TRIAL
 r=json.loads((out/'route_report.json').read_bytes());cap=json.loads((out/'capture.json').read_bytes());a,w=recording(out,cap)
 r['new_assistance_writes']=len(w)-len(json.loads((ROOT/'validation/natural-dungeon-combat/md-auto-v0317-d8-exit01/assistance.json').read_bytes())['writes'])
 r['approach_protection_declared']=True
 r['scope']='Real exterior foes, ordinary inventory/directional/C inputs and coin pickups, with declared approach-only hero_hurt writes. No currency, health, inventory, actor, progression, SRAM or primary-state import.'
 (out/'report.json').write_bytes((json.dumps(r,indent=2)+'\n').encode())
 assert r['passed'],r
