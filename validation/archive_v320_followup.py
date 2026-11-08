"""Archive additional tests of the published,unchangedV320."""
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path('tools').resolve()))
from archive_lossless_evidence import freeze,sha
root=Path('.').resolve();digest='9e5b0abed80678ce864a0bb796c17e97047d1d34e5227a5275bf9336129ceaff';assert sha((root/'gaw-megadrive.bin').read_bytes())==digest
pal=root/'validation/v320-pal-campaign01';p=json.loads((pal/'report.json').read_bytes());assert p['passed'] and p['md_sha256']==digest and p['region']=='pal' and p['frames']==382208 and p['credit_states']==7424 and p['borders_black_all_states'] and p['final']['crystals']==[128]*9
reference=root/'validation/c0046-campaign01/isolated/project/validation/natural-dungeon-combat/md-auto-palc0046-palace-ending01/frame_382208.png';assert (pal/'frame_382208.png').read_bytes()==reference.read_bytes()
cap=json.loads((pal/'capture.json').read_bytes());assert cap['core_options']['genesis_plus_gx_region_detect']=='pal' and 49<cap['fps']<51
results=[];folders=[pal]
for region in ('ntsc','pal'):
 folder=root/'validation'/('v320-postcredits-'+region+'01');folders.append(folder);r=json.loads((folder/'report.json').read_bytes());assert r['passed'] and r['md_sha256']==digest and r['restarted']>r['returned'] and len(r['states'])==7424
 assert not r['bottom_nonblack_frames'] and all(x['top_nonblack']==0 for x in r['states'].values())
 assert r['final']['game']==12 and r['final']['health']>0 and r['final']['crystals']==[0]*9 and not r['final']['audio_error']
 v=(folder/'vram_17000.bin').read_bytes();regs=(folder/'vdp_regs_17000.bin').read_bytes();base=(regs[4]&7)<<13;width=[32,64,32,128][regs[16]&3];assert regs[18]==0
 for row in (26,27):assert v[base+row*width*2:base+row*width*2+64]==bytes(64)
 results.append(dict(region=region,credits_states=7424,credits_borders_black=True,normal_acknowledgment=r['returned'],new_game_playable=r['restarted'],final=r['final'],bottom_bg_b_restored_to_zero=True,window_mask_disabled=True,post_ending_ram_writes=0))
report=dict(passed=True,version=320,md_sha256=digest,rom_changed=False,pal_campaign=p,pal_fps=cap['fps'],pal_final_picture_exact_to_v319_reference=True,postcredits_new_game=results,limits=['Full recorded PAL campaign uses authorized approach-only protection,removed before bosses; no progression/save imports.','New-game-after-credits tests use a controlled terminal-boss fixture before the complete production ending; no RAM writes after setup.','No exhaustive side-route,physical hardware or exact PCM fidelity certificate.'],archive_manifest='analysis/v320-followup-tests/manifest.json')
target=root/'analysis/v320_followup_tests_report.json';assert not target.exists();target.write_text(json.dumps(report,indent=2)+'\n')
paths={target,Path(__file__).resolve(),root/'validation/validate_v320_pal_campaign.py',root/'validation/validate_v320_postcredits_newgame.py'}
for folder in folders:paths.update(p for p in folder.rglob('*') if p.is_file())
freeze(root,root/'analysis/v320-followup-tests',paths,report,folders,cleanup=True)
