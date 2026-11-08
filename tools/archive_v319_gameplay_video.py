"""Preserve the final deliverable and capture evidence; remove exact intermediates."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
from archive_lossless_evidence import freeze,sha
out=ROOT/'videos/v0319';report=json.loads((out/'report.json').read_bytes());movie=Path(report['movie']).resolve()
assert movie.is_relative_to(out.resolve()) and sha(movie.read_bytes())==report['movie_sha256'] and report['passed'] and report['all_video_packets_read'] and report['full_audio_decoded'] and report['final_campaign_ram_and_picture_exact']
folders=[ROOT/'validation'/name for name in ('v319-video-encoder01','v319-video-intro01','v319-video-intro02','v319-video-intro03','v319-video-intro-complete01','v319-video-intro-complete02','v319-video-gameplay01')]
paths={Path(__file__).resolve(),ROOT/'tools/record_v319_gameplay.py',ROOT/'tools/finalize_v319_gameplay_video.py',ROOT/'tools/run_core.py'}
removed=[]
for folder in folders:
 folder=folder.resolve();assert folder.is_relative_to((ROOT/'validation').resolve())
 for path in folder.rglob('*'):
  if not path.is_file():continue
  if path.suffix.lower() in ('.mp4','.wav'):
   resolved=path.resolve();assert resolved.is_relative_to(folder) and resolved!=movie
   removed.append(dict(path=resolved.relative_to(ROOT).as_posix(),bytes=resolved.stat().st_size,sha256=sha(resolved.read_bytes())))
  else:paths.add(path)
report['intermediate_cleanup']=dict(removed=removed,bytes=sum(x['bytes'] for x in removed),retained_final_sha256=report['movie_sha256'],scope='Generated encoder probes,duplicate intro clips,segment MP4s,silent video and rawWAV. Final verified MP4 retained. This is intermediate cleanup,not a lossless source-audio archive.')
report['local_browser_upload_blocker']='cua.getTab returned: Local browser use is disabled in Work settings. User reported a signed-in session, but the agent could not access it. No upload or visibility change made.'
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
target=ROOT/'analysis/v319_gameplay_video_report.json';assert not target.exists();target.write_text(json.dumps(report,indent=2)+'\n');paths.add(target)
paths.update(p for p in out.iterdir() if p.is_file() and p!=movie)
freeze(ROOT,ROOT/'analysis/v319-gameplay-video',paths,report,folders,cleanup=False)
# Verify deliverable again before deleting individually checked temporary files.
assert sha(movie.read_bytes())==report['movie_sha256']
for item in removed:
 path=(ROOT/item['path']).resolve();assert path.is_relative_to((ROOT/'validation').resolve()) and path!=movie and sha(path.read_bytes())==item['sha256'];path.unlink()
print('Final movie retained:',movie);print('Generated intermediate bytes removed:',report['intermediate_cleanup']['bytes'])
