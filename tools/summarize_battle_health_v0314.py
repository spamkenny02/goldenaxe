"""Account for observed battle HP losses/recoveries without inferring from final HP."""
import argparse,json
from run_core import ROOT
from archive_lossless_evidence import sha
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols
from continue_d8_entry_v0314 import assert_canonical

def main():
 p=argparse.ArgumentParser();p.add_argument('--trace',required=True);p.add_argument('--out',required=True);a=p.parse_args()
 folder=(ROOT/'validation'/a.trace).resolve();out=(ROOT/a.out).resolve();assert folder.is_relative_to(ROOT/'validation')and out.is_relative_to(ROOT/'analysis')and not out.exists()
 cap=json.loads((folder/'capture.json').read_bytes());r=json.loads((folder/'report.json').read_bytes());assist,writes=recording(folder,cap);sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
 digest=sha((ROOT/'gaw-megadrive.bin').read_bytes());assert cap['rom_sha256']==r['rom_sha256']==digest and cap['sram_input']is None and r['failure']is None
 assert not assist['health_refills']and not assist['primary_state_imports']and not assist['boss_assistance']
 assert all(addr==sy['hero_hurt']and data in(b'\0\0',b'\0\x81')for _,addr,data in writes)
 assert_canonical(folder.parent.name,folder.name)
 first=r['first_intermediate_combat'];assert first and first['health']>0
 events=json.loads((folder/'events.json').read_bytes());rows=[e for e in events if'health'in e];assert rows and all(a['frame']<=b['frame']for a,b in zip(rows,rows[1:]))
 losses=[];heals=[]
 for before,after in zip(rows,rows[1:]):
  delta=after['health']-before['health']
  change=dict(frame=after['frame'],room=after['room'],before=before['health'],after=after['health'],amount=abs(delta))
  if delta<0:losses.append(change)
  elif delta>0:heals.append(dict(**change,loot_before=before.get('loot',[]),loot_after=after.get('loot',[]),reward_active=after.get('reward_active')))
 approach=[e for e in losses if e['frame']<first['frame']];combat=[e for e in losses if e['frame']>=first['frame']and e['room']==first['room']]
 result=dict(passed=True,version=314,md_sha256=digest,trace=a.trace,frames=cap['frames'],first_combat=first,observed_losses=losses,approach_losses=approach,combat_room_losses=combat,observed_recoveries=heals,observed_net_combat_room_hp_loss=sum(e['amount']for e in combat),no_observed_hp_loss=not losses,final_health=r['last_state']['health'],resource_fixture_writes=0,whole_ram_png_exact=True,events_sha256=sha((folder/'events.json').read_bytes()),source_report_sha256=sha((folder/'report.json').read_bytes()),scope='Observed frame-end HP changes. Final HP does not establish a damage-free fight; recovery and pre-boss floor losses are separate. No per-instruction damage cancellation or unobserved intermediate-frame claim.')
 out.write_text(json.dumps(result,indent=2)+'\n');print('HP accounting:',len(approach),'approach drops,',len(combat),'combat-room drops,',len(heals),'recoveries; final',result['final_health'])
if __name__=='__main__':main()
