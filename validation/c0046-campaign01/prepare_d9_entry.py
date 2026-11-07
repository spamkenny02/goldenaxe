"""Adapt D9 entry to the actual paid southern return, retaining its approach episode."""
from pathlib import Path
root=Path(__file__).resolve().parents[2]
project=root/'validation/c0046-campaign01/isolated/project'
text=(root/'tools/continue_d9_entry_v0317.py').read_text().replace('v0317','c0046')
text=text.replace("analysis/d9_recovery_c0046_report.json","analysis/d9_south_c0046_report.json")
text=text.replace("recovered='md-c0046-d9-healer94-service01'","recovered='md-c0046-d9-south-paid01'")
text=text.replace('c0046-d9-sources03','c0046-d9-sources04')
text=text.replace("assert recovery['current_campaign_trace']=='validation/'+SERVICE+'/'+recovered", "assert recovery['current_campaign_trace'].split('/')[-1]==recovered")
text=text.replace("[*world,'--new-assistance-episode','--completed-exit-proof',COMBAT+'/'+source,'--prefix-service',recovered", "[*world,'--prefix-service',recovered")
target=project/'tools/continue_d9_entry_c0046.py';assert not target.exists();target.write_text(text)

for name in ['summarize_d9_entry','summarize_d9_midboss']:
    text=(root/'tools'/f'{name}_v0317.py').read_text().replace('v0317','c0046').replace('version=317',"candidate='c0046'")
    text=text.replace('c0046-d9-sources03','c0046-d9-sources04')
    text=text.replace('versions/c0046-7694654e/gaw-megadrive-c0046.bin','gaw-megadrive.bin')
    if name.endswith('entry'):
        text=text.replace('analysis/d9_recovery_c0046_report.json','analysis/d9_south_c0046_report.json')
        text=text.replace("and prior['normal_death_continue'] and not prior['currency_or_inventory_fixtures']", "and prior['paid_south_return'] and prior['real_price']==10")
        text=text.replace("previous=prior['current_campaign_trace']", "previous='validation/natural-service-route/'+prior['current_campaign_trace'].split('/')[-1]")
        before="  for before,after in zip(pa['episodes'],a['episodes'][:-1]):assert all(before[k]==after[k] for k in EPISODE_KEYS)"
        after="  assert pa['episodes'][:-1]==a['episodes'][:-1] and pa['boss_room']==a['boss_room']==0x1ac\n  assert a['activation_after_frame']==pa['activation_after_frame']"
        assert text.count(before)==1;text=text.replace(before,after)
        text=text.replace("assert a['activation_after_frame']==pc['frames'] and r['recorded_service_prefix']==previous.split('/')[-1]", "assert r['recorded_service_prefix']==previous.split('/')[-1]")
        text=text.replace("word('hero_keys')==prior['stages'][-1]['keys']","word('hero_keys')==1")
        text=text.replace('return_to_southern_region_via_normal_continue=True','return_to_southern_region_via_normal_continue=False,paid_south_return=True')
        text=text.replace('This current branch returns to the southern region by actual death/Continue, then opensCB with ordinary Bell input. No second northern transport or funds fixture is used; the earlier D8 paid passage is separately retained.',
            'This candidate pays the actual reverse passage1A to3C, then opensCB with ordinary Bell input. The approach episode began after D8 and continues here; no death/Continue or funds fixture is used.')
        text=text.replace(' refs={}',' refs={};origins={};global_root=ROOT.parents[3]')
        before='  raw=evidence(ROOT/name);refs[name]=sha(raw);return raw'
        after="  raw=evidence(ROOT/name);refs[name]=sha(raw);origins[name]=(ROOT/name).resolve().relative_to(global_root).as_posix();return raw"
        marker=" (ROOT/'analysis/d9_entry_c0046_report.json').write_bytes"
        normalize=" prefix=ROOT.relative_to(global_root).as_posix()+'/'\n for stage in result['stages']:stage['trace']=prefix+stage['trace']\n result['current_campaign_trace']=prefix+result['current_campaign_trace']\n result['evidence']={origins[name]:h for name,h in refs.items()}\n"
    else:
        text=text.replace("previous = prior['current_campaign_trace']", "previous = 'validation/natural-dungeon-route/'+prior['current_campaign_trace'].split('/')[-1]")
        text=text.replace('    refs = {}','    refs = {};origins={};global_root=ROOT.parents[3]')
        before='        raw = evidence(ROOT/name); refs[name] = sha(raw); return raw'
        after="        raw=evidence(ROOT/name);refs[name]=sha(raw);origins[name]=(ROOT/name).resolve().relative_to(global_root).as_posix();return raw"
        marker="    (ROOT/'analysis/d9_midboss_c0046_report.json').write_bytes"
        # Inspect the report variable name before binding output normalization.
        assert marker in text
        normalize="    prefix=ROOT.relative_to(global_root).as_posix()+'/'\n    for stage in result['stages']:stage['trace']=prefix+stage['trace']\n    result['current_campaign_trace']=prefix+result['current_campaign_trace']\n    result['evidence']={origins[name]:h for name,h in refs.items()}\n"
    assert text.count(before)==1;text=text.replace(before,after)
    assert text.count(marker)==1;text=text.replace(marker,normalize+marker)
    target=project/'tools'/f'{name}_c0046.py';assert not target.exists();target.write_text(text)
print('D9 Bell entry and first guardian adapted to real paid southern return; not executed')
