"""Compare normalized rendered cold-boot images and their run durations."""
from pathlib import Path
from compression import zstd
import json,difflib,hashlib,argparse
p=argparse.ArgumentParser();p.add_argument('--out',default='v320-visual-comparison02');p.add_argument('--md-ntsc',default='v320-visual-md-ntsc02');p.add_argument('--md-pal',default='v320-visual-md-pal01');options=p.parse_args()
ROOT=Path(__file__).resolve().parents[1];out=(ROOT/'validation'/options.out).resolve();assert out.is_relative_to(ROOT/'validation') and not out.exists();out.mkdir()
def load(tag):
 p=ROOT/'validation'/tag;report=json.loads((p/'report.json').read_bytes());assert report['noncanonical_color_frames']==0,tag
 rows=json.loads(zstd.decompress((p/'frames.json.zst').read_bytes()));seen=False;reset=False;end=len(rows)+1
 for r in rows:
  if r['line']==65:seen=True
  if seen and r['line']<65:reset=True
  if reset and r['line']==1:end=r['frame'];break
 rows=[r for r in rows if r['frame']<end]

 runs=[]
 for r in rows:
  if runs and runs[-1]['hash']==r['hash']:runs[-1]['end']=r['frame'];runs[-1]['duration']+=1
  else:runs.append(dict(hash=r['hash'],start=r['frame'],end=r['frame'],duration=1,nonblack_pixels=r['nonblack_pixels']))
 return p,report,rows,runs,end
results=[]
for region,mdtag in [('ntsc',options.md_ntsc),('pal',options.md_pal)]:
 a,ar,source,sr,se=load('v320-visual-sms-'+region+'01');b,br,native,nr,ne=load(mdtag);assert ar['fps']==br['fps']
 by_source={};by_native={}
 for r in source:
  if r['running'] and 1<=r['line']<=65:by_source.setdefault(r['line'],[]).append(r)
 for r in native:
  if r['running'] and 1<=r['line']<=65:by_native.setdefault(r['line'],[]).append(r)
 lines=[]
 for n in range(1,66):
  x=by_source[n];y=by_native[n];hashes={r['hash'] for r in x};matches=sum(r['hash'] in hashes for r in y)
  lines.append(dict(line=n,source_start=x[0]['frame'],native_start=y[0]['frame'],start_delta=y[0]['frame']-x[0]['frame'],source_frames=len(x),native_frames=len(y),native_frames_with_exact_picture_in_source_line=matches,native_frame_count_without_exact_picture_in_source_line=len(y)-matches))
 matcher=difflib.SequenceMatcher(None,[r['hash'] for r in sr],[r['hash'] for r in nr],autojunk=False);matches=[]
 for block in matcher.get_matching_blocks():
  for k in range(block.size):
   x=sr[block.a+k];y=nr[block.b+k];matches.append(dict(source_start=x['start'],native_start=y['start'],delta=y['start']-x['start'],source_duration=x['duration'],native_duration=y['duration'],same_duration=x['duration']==y['duration'],nonblack_pixels=y['nonblack_pixels'],hash=y['hash']))
 title=[r for r in matches if r['source_start']>=5900 and r['native_start']>=5900]
 results.append(dict(region=region,fps=ar['fps'],source_next_story_first_line=se,native_next_story_first_line=ne,next_story_first_line_delta_frames=ne-se,story_line_starts_exact=all(r['start_delta']==0 for r in lines),lines=lines,source_unique_pictures=len({r['hash'] for r in source}),native_unique_pictures=len({r['hash'] for r in native}),source_picture_runs=len(sr),native_picture_runs=len(nr),exact_matching_picture_runs=len(matches),matched_picture_runs_with_different_duration=sum(not r['same_duration'] for r in matches),title_matches=title,all_matches=matches,source_folder=str(a.relative_to(ROOT)),native_folder=str(b.relative_to(ROOT))))
 print(region,'cycle',se,ne,'line starts exact',all(r['start_delta']==0 for r in lines),'picture runs',len(sr),len(nr),'matched',len(matches),'duration mismatches',sum(not r['same_duration'] for r in matches));print('title',[(r['source_start'],r['native_start'],r['source_duration'],r['native_duration']) for r in title[:16]])
hashes={json.loads((ROOT/'validation'/tag/'report.json').read_bytes())['rom_sha256'] for tag in (options.md_ntsc,options.md_pal)};assert len(hashes)==1,'Regions must use the same ROM'
report=dict(passed_capture_integrity=True,md_sha256=hashes.pop(),graphics_complete=False,results=results,limits=['Exact palette-level correspondence removes only known SMS/MD DAC output scaling;unknown source color values rejected. Pixel layout and whole-image hashes are compared.','Sequence alignment matches identical images in order;does not prove unmatched frames or every possible input. Post-render logical metadata can precede publication.','Cold boot intro/title only;heroes/gameplay/transitions/PNJ/bosses and hardware still need comprehensive per-frame graphics/animation audit.'])
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
