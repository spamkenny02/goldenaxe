"""Check the opened bridge in actual VDP maps and referenced tile pixels."""
import json
from run_core import ROOT
from rebase_natural_campaign import evidence
from archive_lossless_evidence import sha
from audit_item_reward_visuals import sms_pixels,md_pixels

def main():
 game=json.loads((ROOT/'analysis/crystal_bridge_game_v0293-current01_report.json').read_bytes());assert game['passed'] and not game['baseline_missing'];results=[]
 for region in ['auto','pal']:
  root=ROOT/'validation/crystal-bridge-game-v0293-current01';rows=json.loads((root/f'{region}-sms/observations.json').read_bytes())
  for case in [3,4]:
   row=rows[case];f=row['frame']+1;a=evidence(root/f'{region}-sms/vram_{f:05d}.bin');b=evidence(root/f'{region}-md/vram_{f:05d}.bin');software=bytes.fromhex(row['map']);tiles=set();count=0
   for y in range(8,12):
    for x in [20,21]:
     off=y*64+x*2;w=int.from_bytes(a[0x3800+off:0x3802+off],'little');assert a[0x3800+off:0x3802+off]==software[off:off+2]
     translated=((w>>11)&1)<<13|((w>>12)&1)<<15|((w>>10)&1)<<12|((w>>9)&1)<<11|16+(w&511);p=0xe000+(y+2)*128+x*2
     assert int.from_bytes(b[p:p+2],'little')==translated,(region,case,x,y,hex(w),b[p:p+2].hex());tiles.add(w&511);count+=1
   for tile in tiles:assert sms_pixels(a,tile)==md_pixels(b,tile+16),(region,case,tile)
   results.append(dict(region=region,case=case,hardware_map_words=count,referenced_tiles=len(tiles)))
 report=dict(passed=True,md_sha256=game['md_sha256'],cases=results,scope='Settled opened bridge: eight actual VDP words and referenced tile color indices per case. No intermediate transfer timing,sprites,audio or full-framebuffer claim.')
 (ROOT/'analysis/crystal_bridge_publication_v0293_report.json').write_text(json.dumps(report,indent=2)+'\n');print('Opened bridge VDP words/pixels exact:',len(results),'cases')

if __name__=='__main__':main()
