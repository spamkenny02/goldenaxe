"""Check actual VDP publication of every changed axe-fixture metatile."""
import json
from run_core import ROOT
from rebase_natural_campaign import evidence
from archive_lossless_evidence import sha
from audit_item_reward_visuals import sms_pixels,md_pixels

def main():
 report=json.loads((ROOT/'analysis/axe_terrain_game_v0291-02_report.json').read_bytes());assert report['passed'];results=[]
 for region in ['auto','pal']:
  base=ROOT/'validation/axe-terrain-game-v0291-02';rows=json.loads(evidence(base/f'{region}-sms/observations.json'))
  for i,case in enumerate(report['cases']):
   if case['kind'] or case['prior']:continue
   initial=bytearray(160)
   for index in case['indices']:
    initial[index]=case['record'][0]
    if index+16<160:initial[index+16]=case['record'][2]
   final=bytes.fromhex(rows[i*40+39]['cells']);changed=[n for n in range(160) if initial[n]!=final[n]];assert changed
   frame=3100+(i+1)*40;a=evidence(base/f'{region}-sms/vram_{frame:05d}.bin');b=evidence(base/f'{region}-md/vram_{frame:05d}.bin');software=bytes.fromhex(rows[i*40+39]['map']);tiles=set()
   for index in changed:
    for dy in range(2):
     for dx in range(2):
      y=(index>>4)*2+dy;x=(index&15)*2+dx;p=0x3800+y*64+x*2;w=int.from_bytes(a[p:p+2],'little');assert a[p:p+2]==software[y*64+x*2:y*64+x*2+2]
      translated=((w>>11)&1)<<13|((w>>12)&1)<<15|((w>>10)&1)<<12|((w>>9)&1)<<11|16+(w&511);p=0xe000+(y+2)*128+x*2;assert int.from_bytes(b[p:p+2],'little')==translated,(region,i,index,y,x);tiles.add(w&511)
   for tile in tiles:assert sms_pixels(a,tile)==md_pixels(b,tile+16),(region,i,tile)
   results.append(dict(region=region,case=i,changed_cells=changed,hardware_map_words=len(changed)*4,referenced_tiles=len(tiles)))
 out=dict(passed=True,md_sha256=report['md_sha256'],cases=results,scope='Every changed metatile in the controlled axe cases: final software map, actual SMS/native VDP words and referenced tile color indices. Intermediate DMA/IRQ phase and audio waveform are not asserted.')
 (ROOT/'analysis/axe_terrain_publication_v0291_report.json').write_bytes((json.dumps(out,indent=2)+'\n').encode());print('VDP publication exact',len(results))
if __name__=='__main__':main()
