"""Archive natural c0047 inventory restoration checks in exteriors and village houses."""
import json,sys
from pathlib import Path
sys.path.insert(0,'tools')
from archive_lossless_evidence import freeze,sha
root=Path(__file__).resolve().parents[1];work=root/'validation/c0047-inventory01'
r=json.loads((work/'inventory_restore_report.json').read_bytes())
md='d3ea2a83ea24ed8a0d3c9857f9fbe70d000a4f73358452c1887f40e78966c56e';sms='852e068e331dbfb01b9c38a62eecf81ce5b9f0f1bd10fff497117bd885c716c9'
assert r['md_sha256']==md and r['source_sha256']==sms and not r['diagnostic_only']
assert len(r['cases'])==6 and {(c['name'],c['region']) for c in r['cases']}=={(n,t) for n in ('exterior','first_house','second_house') for t in ('auto','pal')}
for c in r['cases']:
    assert c['normal_controller_route'] and c['inventory_open_and_closed'] and c['settled_background_tiles_compared']==124
    assert all(not v for v in c['static_background_pattern_difference_indices'].values()) and not c['early_native_static_pattern_changes_from_before_menu']
    for tag,digest in [('sms',sms),('md',md)]:
        p=work/f"inventory-restore-{c['name']}-{c['region']}-{tag}";cap=json.loads((p/'capture.json').read_bytes())
        assert cap['rom_sha256']==digest and cap['frames']==3470 and cap['sram_input'] is None and not cap['test_ram_writes']
report=root/'analysis/c0047_inventory_report.json';assert not report.exists()
result=dict(passed=True,candidate='c0047',md_sha256=md,source_sha256=sms,cases=r['cases'],normal_controller_routes=6,static_patterns_per_capture=124,
            ram_writes=0,sram_imports=0,archive_manifest='analysis/c0047-inventory/manifest.json',
            limits=r['limits'],driver_sha256=sha((root/'tools/validate_inventory_restore.py').read_bytes()))
report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
paths=[Path(__file__).resolve(),report,root/'tools/validate_inventory_restore.py']+[p for p in work.rglob('*') if p.is_file()]
freeze(root,root/'analysis/c0047-inventory',paths,result,[work],cleanup=True)
print('Six natural inventory returns verified and archived; animated house phase remains explicitly separate',flush=True)
