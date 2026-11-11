"""Check reported missing text against selected, fixed-replayed SMS observations.

Negative observations are not a proof that the original strings are unused.
"""
import hashlib,json
from run_core import ROOT


def main():
    rom=(ROOT/'input/original.sms').read_bytes();traces=set()
    census=json.loads((ROOT/'analysis/sms_plain_house_census_campaign.json').read_bytes())
    traces.add(census['completed_houses'][-1]['trace'])
    for name,key in [('sms_remaining_magic_campaign.json','completed_visits'),
                     ('sms_fairy_census_campaign.json','completed_rewards'),
                     ('sms_service_refusal_campaign.json','completed_visits'),
                     ('sms_gold_house_census_campaign.json','completed_houses'),
                     ('sms_hidden_rewards_campaign.json','completed_rewards'),
                     ('sms_teacher_returns_campaign.json','completed_visits'),
                     ('sms_passage_census_campaign.json','completed_passages')]:
        path=ROOT/'analysis'/name
        if path.exists():
            rows=json.loads(path.read_bytes()).get(key,[])
            if rows:traces.add(rows[-1]['trace'])
    for filename in ('sms_inn_locations_campaign.json','sms_save_locations_campaign.json'):
        path=ROOT/'analysis'/filename
        if path.exists():
            for row in json.loads(path.read_bytes()).get('completed_locations',[]):
                traces.add(row.get('trace',row.get('save_trace')))
    for path in (ROOT/'analysis').glob('sms_minigame_*_campaign.json'):
        data=json.loads(path.read_bytes())
        if data.get('passed'):traces.add(data['last_verified_prefix'])
    for path in (ROOT/'analysis').glob('sms-conditional-*.json'):
        report=json.loads(path.read_bytes())
        if report.get('passed'):
            # Conditional reports identify their selected service recordings.
            for value in report.values():
                if isinstance(value,str) and value.startswith('natural-service-route/'):
                    traces.add(value)
    selected=[];entries=[];returns=[]
    for trace in sorted(traces):
        folder=ROOT/'validation'/trace
        observation=folder/'dialogue_observations.json'
        if not observation.exists():continue
        cap=json.loads((folder/'capture.json').read_bytes())
        proof=folder.with_name(folder.name+f'-assisted-fixed-replay-{cap["frames"]}')/'replay_report.json'
        assert json.loads(proof.read_bytes())['passed']
        source=json.loads(observation.read_bytes());assert source['read_only'] and source['source_sha256']==hashlib.sha256(rom).hexdigest()
        selected.append(dict(trace=trace,frames=cap['frames'],proof=proof.relative_to(ROOT).as_posix(),
            observations_sha256=hashlib.sha256(observation.read_bytes()).hexdigest()))
        for e in source['events']:
            item=dict(trace=trace,frame=e['frame'],event_pc=e['event_pc'],text_pc=e['text_pc'],
                outside=e['outside'],room=e['room'],caller=e['caller'])
            if e['event_pc'] in (0x50c,0x524):entries.append(item)
            else:returns.append(item)
    findings=[]
    for target in (0xda58,0xda7c,0xed3c):
        hits=[]
        for e in entries:
            pc=e['text_pc']
            if not 0x8000<=pc<0xc000:continue
            begin=0xc000+(pc&0x3fff);end=rom.index(0,begin)
            if begin<=target<=end:hits.append(e)
        findings.append(dict(sms_offset=f'0x{target:04X}',entry_or_displayed_string_range_hits=hits,
            unused_in_sms_proven=False,classification='observed_source_trigger' if hits else 'still_unresolved_after_selected_runtime_observations',
            return_pointer_matches_not_display_proof=[e for e in returns if e['text_pc']==0x8000+(target&0x3fff)]))
    result=dict(source_sha256=hashlib.sha256(rom).hexdigest(),selected_recordings=selected,
        entry_event_count=len(entries),unique_text_entry_pcs=len({e['text_pc'] for e in entries}),findings=findings,
        complete_call_data_flow_proof=False,all_npcs_and_side_quests_complete=False,
        limits=['Only selected recordings with an independent fixed replay are admitted.',
                'Formatter/wrapper return pointers do not identify displayed strings.',
                'Not observing a string cannot prove it unreachable. No quest trigger or ROM change is invented.'])
    (ROOT/'analysis/selected_sms_missing_texts_runtime_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(recordings=len(selected),entries=len(entries),findings=[(x['sms_offset'],len(x['entry_or_displayed_string_range_hits'])) for x in findings])))


if __name__=='__main__':main()
