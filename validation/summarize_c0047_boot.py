"""Audit c0047 opening against SMS and V318, then freeze and clean generated duplicates."""
import json,sys
from pathlib import Path
sys.path.insert(0,'tools')
from archive_lossless_evidence import freeze,sha
root=Path(__file__).resolve().parents[1];work=root/'validation/c0047-boot01'
view=json.loads((work/'inputs.json').read_bytes());assert view['read_only_input_view_not_a_build'] and view['candidate']=='c0047'
md='d3ea2a83ea24ed8a0d3c9857f9fbe70d000a4f73358452c1887f40e78966c56e'
baseline='b9e1f0a0543f191e24ffd6d2740a0d717501e0fcd986f8b8953a37a1b3c416a4'
source='852e068e331dbfb01b9c38a62eecf81ce5b9f0f1bd10fff497117bd885c716c9'
assert view['files']['rom.bin']['sha256']==md
for name,ref in view['files'].items():assert sha((root/ref['source']).read_bytes())==sha((work/'project/out/release'/name).read_bytes())==ref['sha256']
regions=[]
for region,exact,errors in [('ntsc',13636,147429),('pal',13682,124148)]:
    folder=work/(region+'-video');r=json.loads((folder/'report.json').read_bytes())
    assert r['frames']==14000 and r['region']==region and r['md_sha256']==md and r['baseline_sha256']==baseline and r['source_sha256']==source
    assert r['no_source_pixel_regression'] and not r['changed_frames'] and not r['improved_pixels'] and not r['degraded_pixels']
    assert r['totals']==dict(baseline_source_differences=errors,candidate_source_differences=errors,baseline_exact_frames=exact,candidate_exact_frames=exact)
    assert not r['ram_writes'] and not r['sram_imports']
    assert sha((root/'tools/compare_boot_to_sms.py').read_bytes())==r['driver_sha256']
    old=(folder/'baseline/normalized-frame-hashes.bin').read_bytes();new=(folder/'candidate/normalized-frame-hashes.bin').read_bytes()
    assert len(old)==len(new)==14000*32 and old==new
    for tag in ('baseline','candidate','sms'):
        c=json.loads((folder/tag/'capture.json').read_bytes());assert c['frames']==14000 and not c['presses'] and not c['test_ram_writes'] and c['sram_input'] is None
    regions.append(dict(region=region,frames=14000,identical_to_v318_frames=14000,sms_exact_frames=exact,sms_different_pixels=errors))
audio=json.loads((work/'audio/report.json').read_bytes());assert audio['passed'] and audio['md_sha256']==md and audio['baseline_sha256']==baseline and audio['frames_per_region']==6500
assert not audio['ram_writes'] and not audio['sram_imports'] and {r['region'] for r in audio['cases']}=={'ntsc','pal'}
for r in audio['cases']:
    assert not r['state_difference_frames'] and not r['psg_difference_frames']
    assert r['state_sha256']['baseline']==r['state_sha256']['candidate'] and r['psg_sha256']['baseline']==r['psg_sha256']['candidate']
result=dict(passed=True,candidate='c0047',md_sha256=md,baseline_sha256=baseline,source_sha256=source,regions=regions,
            audio_frames_per_region=6500,audio_reader_bytes_checked=402,psg_registers_checked=8,ram_writes=0,sram_imports=0,
            scope='Two no-input opening loops per region. All normalized video frames retain V318 behavior; existing partial-reveal and fade differences from SMS remain. Audio-reader and PSG state match V318, not a PCM comparison.',
            archive_manifest='analysis/c0047-boot/manifest.json')
report=root/'analysis/c0047_boot_report.json';assert not report.exists();report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
paths=[Path(__file__).resolve(),report,root/'tools/compare_boot_to_sms.py',root/'tools/compare_boot_audio_state.py']+[p for p in work.rglob('*') if p.is_file()]
freeze(root,root/'analysis/c0047-boot',paths,result,[work],cleanup=True)
print('c0047 opening audited and archived: no opening regression; source fidelity limitations retained',flush=True)
