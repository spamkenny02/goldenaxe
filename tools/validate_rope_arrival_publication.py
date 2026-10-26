"""Verify the destination rope column in actual SMS and native VDP memory."""
import json
from run_core import ROOT
from rebase_natural_campaign import evidence
from archive_lossless_evidence import sha
from audit_item_reward_visuals import sms_pixels,md_pixels

def main():
 report=json.loads((ROOT/'analysis/rope_arrival_game_v0292-01_report.json').read_bytes());assert report['passed'] and not report['missing_arrival_reproduced'];results=[]
 for case in report['results']:
  region=case['region'];direction=case['direction'];base=ROOT/'validation/rope-arrival-game-v0292-01';a=evidence(base/f'{region}-{direction}-sms/vram_03450.bin');b=evidence(base/f'{region}-{direction}-md/vram_03450.bin');software=bytes.fromhex(case['source_final']['map']);tiles=set();count=0
  # All twenty tile rows in the actual climbing column, including its anchors.
  for y in range(20):
   for x in [14,15]:
    off=y*64+x*2;w=int.from_bytes(a[0x3800+off:0x3802+off],'little');assert a[0x3800+off:0x3802+off]==software[off:off+2]
    translated=((w>>11)&1)<<13|((w>>12)&1)<<15|((w>>10)&1)<<12|((w>>9)&1)<<11|16+(w&511);p=0xe000+(y+2)*128+x*2;assert int.from_bytes(b[p:p+2],'little')==translated,(region,direction,y,x);tiles.add(w&511);count+=1
  for tile in tiles:assert sms_pixels(a,tile)==md_pixels(b,tile+16),(region,direction,tile)
  results.append(dict(region=region,direction=direction,hardware_map_words=count,referenced_tiles=len(tiles)))
 out=dict(passed=True,md_sha256=report['md_sha256'],cases=results,scope='Final destination climbing column: software map, actual VDP map words and referenced tile color indices. Intermediate scroll/DMA phase, sprites, audio and complete framebuffer are not asserted.')
 (ROOT/'analysis/rope_arrival_v0292_publication_report.json').write_text(json.dumps(out,indent=2)+'\n');print('VDP climbing columns exact',len(results))
if __name__=='__main__':main()
