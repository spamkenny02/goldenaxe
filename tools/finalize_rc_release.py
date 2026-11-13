"""Collect actual release evidence; fail closed if a required gate is absent."""
import hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SHA='1421abe47de95ac104a03e2fb1be7001f70aeca1fbb6a9b35669aa6e98b7d9a4'
def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    coverage=json.loads((ROOT/'analysis/md_annex_replay_coverage.json').read_bytes())
    #409 retained recordings include controller checkpoints and aliases; keep
    # their exact-reference ledger honest. Publication instead requires every
    # selected gameplay goal plus explicit known-context cohorts, and a movie
    # collection proving that none of those selected goals lost its footage.
    goals=json.loads((ROOT/'analysis/md_selected_gameplay_goal_closure.json').read_bytes())
    assert goals['passed'] and goals['verified_selected_gameplay_goals']==goals['required_selected_gameplay_goals']==145
    assert all(c['verified'] for c in goals['cases']) and len(goals['supplemental_known_context_cohorts'])==5
    movies=json.loads((ROOT/'analysis/md_selected_proof_video_collection.json').read_bytes())
    assert movies['passed'] and not movies['missing_selected_goal_movies']
    included={r['trace'] for r in movies['completed_clips']}
    assert all(e['trace'] in included for cohort in goals['supplemental_known_context_cohorts'] for e in cohort['evidence'])
    out=ROOT/'reports/gaw-v0322-rc1-2026-11-13';out.mkdir(exist_ok=True,parents=True)
    files={
      'clean-build':'validation/rc1-clean-build03/source-build-report.json',
      'standalone-build':'validation/rc1-portable/gaw-v0322-rc1/dist/source-build-report.json',
      'campaign-ntsc':'validation/rc1-campaign-ntsc01/report.json',
      'campaign-pal':'validation/rc1-campaign-pal01/report.json',
      'continue-ntsc':'validation/rc1-runtime/validation/save-compatibility/rc1-ntsc/report.json',
      'continue-pal':'validation/rc1-runtime/validation/save-compatibility/rc1-pal/report.json',
      'saylun-ntsc':'validation/natural-service-route/md-ntsc-rc1-c7-dialogue01/report.json',
      'saylun-pal':'validation/natural-service-route/md-pal-rc1-c7-dialogue01/report.json',
      'saylun-ntsc-fixed':'validation/natural-service-route/md-ntsc-rc1-c7-dialogue01-assisted-fixed-replay-6857/replay_report.json',
      'saylun-pal-fixed':'validation/natural-service-route/md-pal-rc1-c7-dialogue01-fixed-replay/replay_report.json',
      'selected-md-goals':'analysis/md_selected_gameplay_goal_closure.json',
      'selected-md-movies':'analysis/md_selected_proof_video_collection.json',
      'video-md-montage':'analysis/md_proof_montage_report.json',
      'video-md-boundaries':'analysis/md_montage_boundary_pixels_report.json',
      'video-md':'videos/v0322-rc1/report.json',
      'video-sms':'analysis/sms_proof_montage_report.json',
      'video-sms-boundaries':'analysis/sms_montage_boundary_pixels_report.json'}
    reports={}
    for name,path in files.items():
        source=ROOT/path;r=json.loads(source.read_bytes());assert r['passed'],path
        recorded_sha=r.get('md_sha256',r.get('rom_sha256'))
        if recorded_sha:assert recorded_sha==SHA,path
        reports[name]=r;shutil.copyfile(source,out/(name+'.json'))
    for region in ('ntsc','pal'):
        r=reports['campaign-'+region];assert r['ending_seen'] and r['final']['crystals']==9 and not r['normal_deaths'] and not r['live_boss_guard_overlap_frames'] and not r['boss_assistance'] and not r['sram_imports']
        r=reports['continue-'+region];assert r['normal_continue'] and r['ram_writes']==0 and r['items_and_crystals_restored']
    video=reports['video-md'];assert video['campaign_completed'] and video['full_video_decoded'] and video['full_audio_decoded'] and not video['boss_assistance']
    assert sha(Path(video['movie']))==video['sha256']
    sms=reports['video-sms'];assert sms['full_audio_video_decoded'] and sha(Path(sms['movie']))==sms['movie_sha256']
    assert reports['video-sms-boundaries']['movie_sha256']==sms['movie_sha256']
    md=reports['video-md-montage'];assert md['full_audio_video_decoded'] and md['selected_receipts_covered']==145 and sha(Path(md['movie']))==md['movie_sha256']
    assert reports['video-md-boundaries']['movie_sha256']==md['movie_sha256']
    assert {r['trace'] for r in md['sources']}==included
    collection=json.loads((ROOT/'analysis/sms_selected_proof_video_collection.json').read_bytes())
    assert collection['all_selected_receipts_video_covered'] and collection['covered_selected_receipts']==collection['required_selected_receipts']==145
    persistence=json.loads((ROOT/'analysis/sms_persistence_video_collection.json').read_bytes());assert persistence['complete'] and len(persistence['completed_branches'])==17
    rom=ROOT/'validation/dialogue-empty-width03/candidate.bin';raw=rom.read_bytes();assert sha(rom)==SHA and len(raw)==2097152
    import sys
    sys.path.insert(0,str(ROOT/'tools'))
    from finalize_md_rom import md_checksum
    assert md_checksum(raw)==int.from_bytes(raw[0x18e:0x190],'big') and int.from_bytes(raw[0x1a4:0x1a8],'big')==len(raw)-1
    overlay=json.loads((ROOT/'validation/dialogue-empty-width03/build-report.json').read_bytes());assert overlay['all_other_bytes_identical'] and overlay['title_and_credits_overlays_unchanged']
    limits=[
      'No global 100% certificate for all NPCs, side-quest permutations or paired SMS/MD physical pixels.',
      'SMS strings DA58/DA7C/ED3C remain present in source data and without a demonstrated legitimate trigger; not declared globally unused. They are not added to MD through invented triggers.',
      'Saylun owned-apple complete text matches at the SMS formatter return; the later source SMS wait duplicates a suffix and is not pixel-identical. Two source money-table rows lack demonstrated access. Known residual title raster/reveal/fade fidelity differences remain; title and credits overlays from V321 are retained unchanged.',
      'Logic/PSG checks do not certify identical PCM waveforms; no actual-console or BizHawk campaign validation.',
      'PAL and NTSC complete-campaign evidence is MD. The selected extended SMS video is NTSC.',
      'Recorded approach protection is disclosed and excluded from live boss combat. Two separately labelled SMS component branches and one MD99-key component use money assistance; no live boss protection.']
    result=dict(passed=True,date='2026-11-13',version=322,release_candidate='rc1',md_sha256=SHA,bytes=len(raw),checksum=f'{md_checksum(raw):04X}',
      status='release_candidate_for_external_testing',point6='complete_for_selected_route_and_identified_annexes',
      scope='Source-reproducible candidate; actual PAL/NTSC ending campaigns, genuine save Continue, scoped Saylun fix and delivered video evidence. Not global final fidelity certification.',
      evidence={k:dict(file=str((out/(k+'.json')).relative_to(ROOT)).replace('\\','/'),sha256=sha(out/(k+'.json'))) for k in files},
      md_selected_gameplay_goals_verified=145,md_annex_videos=len(movies['completed_clips']),md_exact_reference_recordings_verified=coverage['md_ntsc_played_replayed_and_filmed_cases'],md_retained_diagnostic_recordings=coverage['retained_sms_recording_cases'],
      sms_selected_receipts_video_covered=145,sms_annex_videos=70,sms_continue_branches=17,
      known_reproduced_blockers_in_executed_release_gates=[],all_npcs_complete=False,hardware_validated=False,limits=limits)
    (ROOT/'analysis/rc1_release_report.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    shutil.copyfile(ROOT/'analysis/rc1_release_report.json',out/'RELEASE.json')
    p=ROOT/'analysis/sms_six_points_progress.json';progress=json.loads(p.read_bytes());progress['points']['6_final_replay_and_video'].update(status='complete_selected_route_and_identified_annexes_global_100_percent_open',closure_report='analysis/rc1_release_report.json');p.write_text(json.dumps(progress,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('evidence','limits')},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
