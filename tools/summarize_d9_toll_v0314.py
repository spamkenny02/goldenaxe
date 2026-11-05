"""Verify real exterior coin earnings before the D9 coastal fare."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from assisted_prefix import recording,EPISODE_KEYS
from rebase_natural_campaign import evidence
from validate_playable_sprite_limit import symbols

def main():
 refs={}
 def read(p):
  raw=evidence(p);refs[p.relative_to(ROOT).as_posix()]=sha(raw);return raw
 def load(p):return json.loads(read(p))
 prior=load(ROOT/'analysis/d8_campaign_v0314_report.json');assert prior['passed']
 source=ROOT/prior['current_campaign_trace'];pc=load(source/'capture.json');pa,pw=recording(source,pc)
 root=ROOT/'validation/natural-service-route/md-v0314-d9-earned-toll10';c=load(root/'capture.json');r=load(root/'report.json');a,w=recording(root,c)
 digest=sha((ROOT/'gaw-megadrive.bin').read_bytes());assert digest==prior['md_sha256']==c['rom_sha256']==r['rom_sha256']
 assert r['passed'] and not r['failure'] and r['source_prefix']==source.name and not c['sram_input']
 assert not r['currency_or_inventory_fixtures'] and not r['primary_state_imports'] and not r['rom_modifications']
 assert c['frames']>pc['frames'] and w[:len(pw)]==pw and len(a['episodes'])==11
 for before,after in zip(pa['episodes'],a['episodes'][:-1]):assert all(before[k]==after[k]for k in EPISODE_KEYS)
 assert a['activation_after_frame']==pc['frames'] and a['boss_room']==0x1ac and all(a[k]is None for k in ['first_boss_entry','release_write_frame','first_boss_combat','first_boss_damage'])
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');assert all(addr==sy['hero_hurt']and value in(b'\0\0',b'\0\x81')for _,addr,value in w)
 proof=root.with_name(root.name+'-assisted-fixed-replay-'+str(c['frames']));p=load(proof/'replay_report.json');assert p['passed']and p['whole_ram_bytes']==65536 and p['final_png_exact']and not p['feedback_reads']and p['rom_sha256']==digest
 for name,h in p['evidence'].items():assert sha(read(root/name))==h
 for stem,ext in [('ram','bin'),('frame','png')]:
  name=f'{stem}_{c["frames"]:05d}.{ext}';assert read(root/name)==read(proof/name)
 raw=read(root/f'ram_{c["frames"]:05d}.bin');data=lambda n,k:bytes(raw[(sy[n]+i)^1]for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
 assert r['first_state']['gold']==8 and word('hero_gold')==r['last_state']['gold']>=10 and word('hero_health')>0 and word('room_id')<256
 assert data('game_save_state',592)[0x1f:0x28]==bytes([128]*8+[0]) and word('hero_max_health')==96
 e=load(root/'events.json');assert any(coin['type']in(8,9)for row in e for coin in row['loot'])
 result=dict(passed=True,md_sha256=digest,version=314,trace=root.relative_to(ROOT).as_posix(),frames=c['frames'],gold_before=8,gold_after=word('hero_gold'),health=word('hero_health'),room=word('room_id'),primary_state_imports=0,resource_writes=0,approach_only_guard_writes=len(w)-len(pw),whole_ram_png_exact=True,full_game_validated=False,evidence=refs,scope='Real exterior combat and dropped coin pickups. Explicitly declared approach protection only; no resources,actors,progression or SRAM imported. D9 guardians and main boss remain to validate.')
 (ROOT/'analysis/d9_toll_v0314_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print('Actual coin earnings and cold RAM/PNG proof verified:',result['gold_after'])
if __name__=='__main__':main()
