"""Summarize played C9 fairy rewards/returns without claiming equal progression."""
import json
from run_core import ROOT
from summarize_gillian_campaign import verified


def main():
    stages = []
    for platform, first, capacity in [('sms', '01', 32), ('md', '02', 24)]:
        for name, route in [
            (f'natural-dungeon-route/{platform}-{platform}-npc-life-fairy-entry01', True),
            (f'natural-service-route/{platform}-npc-life-fairy{first}', False),
            (f'natural-dungeon-route/{platform}-{platform}-npc-life-fairy-return-entry01', True),
            (f'natural-service-route/{platform}-npc-life-fairy-return01', False),
        ]:
            path, cap, report, raw, evidence = verified(name, route)
            if not route:
                before = report['initial_state']; after = report['last_state']
                repeat = name.endswith('return01')
                assert report['new_assistance_writes'] == 0
                assert after['outside_flags'] & 2 and after['room'] == 0xc9
                assert after['max_health'] == after['health'] == capacity + 8
                if repeat:
                    assert report['revisit'] and report['contact_end'] - report['contact_start'] == 80
                    assert before['max_health'] == after['max_health']
                    assert before['health'] == after['health']
                    assert before['outside_flags'] == after['outside_flags']
                else:
                    assert before['max_health'] == capacity and not before['outside_flags'] & 2
                evidence.update(variant='return_after_reward' if repeat else 'initial_reward',
                                initial_state=before, final_state=after)
                if platform == 'sms':
                    obs = json.loads((path / 'dialogue_observations.json').read_bytes())['events']
                    entries = [e for e in obs if e['frame'] >= report['prefix_end']
                               and e['event_pc'] in (0x50c, 0x524)]
                    if repeat:
                        assert not entries, 'Return unexpectedly started a dialogue'
                    else:
                        assert any(e['text_pc'] == 0x9021 for e in entries)
                    evidence['observed_text_entries'] = [dict(frame=e['frame'], text_pc=e['text_pc']) for e in entries]
                evidence['platform'] = platform
            stages.append(evidence)
    report = dict(passed=True, outside=0xc9, stages=stages,
                  initial_reward_effect_both_platforms_verified=True,
                  return_no_second_reward_both_platforms_verified=True,
                  latest_selected_sms_prefix='natural-service-route/sms-npc-life-fairy-return01',
                  latest_selected_md_prefix='natural-service-route/md-npc-life-fairy-return01',
                  all_npcs_complete=False,
                  limits=['SMS has the first crystal; this MD branch does not. Compare the +8 reward and once-only effect, not absolute HP or timing.',
                          'Both branches use recorded approach protection; none is added during these service visits. No quest/save imports.',
                          'SMS entry observation establishes the initial 9021 text and no new formatter entry on return. MD text/pages/pixels/audio/timing remain to compare.',
                          'Only the C9 life fairy initial/repeat variants are covered here; other fairies and capacity-boundary variants remain open.'])
    (ROOT / 'analysis/npc_fairy_campaign_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(dict(passed=True, replayed_stages=len(stages), initial_and_return_both_platforms=True)))


if __name__ == '__main__':
    main()
