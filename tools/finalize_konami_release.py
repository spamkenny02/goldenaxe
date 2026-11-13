"""Publish the optional title feature only after concrete runtime gates pass."""
import json,hashlib,shutil
from run_core import ROOT
from finalize_md_rom import md_checksum

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 rom=ROOT/'validation/konami04/candidate.bin';digest=sha(rom);raw=rom.read_bytes();assert len(raw)==2097152 and md_checksum(raw)==int.from_bytes(raw[0x18e:0x190],'big')
 assert digest==sha(ROOT/'validation/konami05-repro/candidate.bin');base=ROOT/'versions/v0322-1421abe4/gaw-megadrive-v0322.bin';assert sha(base)=='1421abe47de95ac104a03e2fb1be7001f70aeca1fbb6a9b35669aa6e98b7d9a4'
 files={'build':'validation/konami05-repro/build-report.json','ui':'validation/konami04-ui-cases/report.json','life-contact':'analysis/konami_life_contact_v0323_report.json','continue':'analysis/konami_continue_v0323_report.json','campaign-ntsc':'validation/konami04-campaign-ntsc/report.json','campaign-pal':'validation/konami04-campaign-pal/report.json','six-purchases':'validation/natural-service-route/md-konami04-six-keys02/report.json','six-purchases-fixed':'validation/natural-service-route/md-konami04-six-keys02-fixed-replay/replay_report.json','boot-fixed':'validation/natural-service-route/md-konami-boot-on01-fixed-replay/replay_report.json'}
 folder=ROOT/'reports/konami-v0323-2026-11-13';folder.mkdir(exist_ok=True);reports={}
 for name,path in files.items():
  source=ROOT/path;r=json.loads(source.read_bytes());assert r['passed'] and r.get('md_sha256',r.get('rom_sha256'))==digest;reports[name]=r;shutil.copyfile(source,folder/(name+'.json'))
 assert reports['ui']['case_count']==12
 for region in ['ntsc','pal']:
  r=reports['campaign-'+region];assert r['ending_seen'] and not r['normal_deaths'] and not r['live_boss_guard_overlap_frames'] and r['final']['crystals']==9 and r['cheats_disabled_every_frame_checked']
 assert len(reports['continue']['cases'])==4
 r=reports['six-purchases'];assert r['keys_bought']==6 and r['first_state']['gold']==r['last_state']['gold']==255 and r['last_state']['keys']-r['first_state']['keys']==6 and r['unit_price']*6>255 and not r['ram_injections']
 assert reports['six-purchases-fixed']['whole_ram_bytes']==65536 and reports['six-purchases-fixed']['final_png_exact']
 shutil.copyfile(ROOT/'validation/natural-service-route/md-konami-boot-on01/frame_01000.png',folder/'ecran-konami.png')
 r=dict(passed=True,md_sha256=digest,base_sha256=sha(base),version=323,bytes=len(raw),checksum=f'{md_checksum(raw):04X}',feature='Konami title options',sequence=['UP','UP','DOWN','DOWN','LEFT','RIGHT','LEFT','RIGHT','B','A','START'],life_infinite=True,gold_refilled_to=255,default_off=True,session_only=True,source_rebuild_exact=True,sram_format_unchanged=True,original_rc1_preserved=True,normal_campaigns_pal_ntsc_completed=True,ui_cases=12,continue_cases=4,real_enemy_contact_and_real_six_purchases=True,proofs={name:dict(file=(folder/(name+'.json')).relative_to(ROOT).as_posix(),sha256=sha(folder/(name+'.json'))) for name in files},scope='Optional native68000 extension toV322RC1, with original game engine and existing corrections unchanged. Normal campaigns replayed with the same declared approach guard and no live boss guard. UI/cheat/contact/purchase cases use actual controller input with no external RAM fixtures. Not a new qualification of every329RC1annex or console hardware.')
 (ROOT/'analysis/konami_v0323_report.json').write_bytes((json.dumps(r,indent=2)+'\n').encode());shutil.copyfile(ROOT/'analysis/konami_v0323_report.json',folder/'VALIDATION.json')
 shutil.copyfile(rom,ROOT/'gaw-megadrive.bin');shutil.copyfile(rom,ROOT/'gaw-title-megadrive.bin')
 print(json.dumps({k:v for k,v in r.items()if k not in ['proofs','scope']}),flush=True)
if __name__=='__main__':main()
