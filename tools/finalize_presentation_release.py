"""Publish the requested2MiB presentation only after real boot/game/save gates pass."""
import json,hashlib,shutil
from pathlib import Path
from run_core import ROOT
from finalize_md_rom import md_checksum

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 rom=ROOT/'validation/presentation06-2m/candidate.bin';raw=rom.read_bytes();digest=sha(rom);base=ROOT/'versions/v0323-9fcee16d/gaw-megadrive-v0323.bin';assert len(raw)==2097152 and raw[0x1a4:0x1a8]==bytes.fromhex('001fffff') and md_checksum(raw)==int.from_bytes(raw[0x18e:0x190],'big')
 assert digest==sha(ROOT/'validation/presentation07-repro/candidate.bin');assert sha(base)=='9fcee16dc12028138712564ebd7123d99a25d1ef8f6e54d9799f02ceddaacd99'
 files={'build':'validation/presentation07-repro/build-report.json','boot':'validation/presentation06-bootproof/report.json','campaign-ntsc':'validation/presentation06-campaign-ntsc/report.json','campaign-pal':'validation/presentation06-campaign-pal/report.json','konami':'validation/presentation06-menu/report.json','continue':'analysis/presentation06-continue-report.json','video':'videos/v0324/report.json'}
 folder=ROOT/'reports/presentation-v0324-2026-11-13';folder.mkdir(exist_ok=True);reports={}
 for name,path in files.items():
  source=ROOT/path;r=json.loads(source.read_bytes());assert r['passed'] and r.get('md_sha256',r.get('rom_sha256'))==digest;reports[name]=r;shutil.copyfile(source,folder/(name+'.json'))
 for reg in ['ntsc','pal']:
  r=reports['campaign-'+reg];assert r['ending_seen'] and not r['normal_deaths'] and not r['live_boss_guard_overlap_frames'] and r['final']['crystals']==9 and r['cheats_disabled_every_frame_checked']
 for r in reports['boot']['cases']:assert r['tiles_and_map_exact'] and r['waveform_correlation']>.96 and abs(r['voice_seconds']-3.631)<.01 and r['no_digital_clipping']
 assert reports['konami']['case_count']==12 and len(reports['continue']['cases'])==4 and reports['video']['cold_replay_whole_ram_pixels_and_audio_exact'] and reports['video']['full_audio_video_decoded']
 shutil.copyfile(ROOT/'validation/presentation06-bootproof/ntsc/frame_00100.png',folder/'presentation.png');shutil.copyfile(ROOT/'validation/presentation06-bootproof/ntsc/frame_00400.png',folder/'retour-intro.png')
 r=dict(passed=True,version=324,md_sha256=digest,base_sha256=sha(base),bytes=len(raw),checksum=f'{md_checksum(raw):04X}',image_and_voice_in_rom=True,source_image_sha256=reports['build']['assets']['source_image_sha256'],source_audio_sha256=reports['build']['assets']['source_audio_sha256'],fades_in_and_out=True,once_per_boot=True,original_intro_after_presentation=True,pal_ntsc_normal_campaigns_to_ending=True,konami_preserved=True,real_save_continue_verified=True,rom_size_limit_respected=2097152,uses_existing_unused_rom_padding=True,additional_quality_loss_for_2mib=False,proofs={name:dict(file=(folder/(name+'.json')).relative_to(ROOT).as_posix(),sha256=sha(folder/(name+'.json')))for name in files},scope='Boot-only native68000 bitmap and YM2612DAC voice, with region-correct playback and a preserved virtual game epoch. Game and Konami logic remain byte-identical outside the displaced main prologue. Normal campaigns retain the previously declared approach guard, removed before live bosses. Not a new global100percent NPC/visual/hardware certification.')
 (ROOT/'analysis/presentation_v0324_report.json').write_text(json.dumps(r,indent=2)+'\n',newline='\n');shutil.copyfile(ROOT/'analysis/presentation_v0324_report.json',folder/'VALIDATION.json')
 shutil.copyfile(rom,ROOT/'gaw-megadrive.bin');shutil.copyfile(rom,ROOT/'gaw-title-megadrive.bin');print(json.dumps({k:v for k,v in r.items()if k not in ['scope','proofs']}),flush=True)
if __name__=='__main__':main()
