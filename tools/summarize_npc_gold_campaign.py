"""Verify the selected SMS D4 gift and subsequent once-only return."""
import json
from run_core import ROOT
from summarize_gillian_campaign import verified


def main():
    stages = []
    for relative, route in [
        ('natural-dungeon-route/sms-sms-npc-gold-d4-entry01', True),
        ('natural-service-route/sms-npc-gold-d4-gift01', False),
        ('natural-dungeon-route/sms-sms-npc-gold-d4-return-entry01', True),
        ('natural-service-route/sms-npc-gold-d4-return02', False),
    ]:
        path, cap, result, raw, evidence = verified(relative, route)
        if not route:
            repeat = relative.endswith('return02')
            before = result['first_state']; after = result['last_state']
            assert after['room'] == 0xd4 and after['game'] == 12 and after['health'] > 0
            assert after['gold'] - before['gold'] == (0 if repeat else 10)
            assert after['outside_flags'] & 2 and result['new_assistance_writes'] == 0
            events = json.loads((path / 'dialogue_observations.json').read_bytes())['events']
            entries = [e for e in events if e['frame'] >= cap['frames'] - 5000
                       and e['event_pc'] in (0x50c, 0x524)]
            # Limit to this service, excluding all cold-prefix conversations.
            prefix = ROOT / 'validation/natural-dungeon-route' / result['source_prefix']
            start = json.loads((prefix / 'capture.json').read_bytes())['frames']
            entries = [e for e in entries if e['frame'] >= start]
            if repeat:
                assert result['contact_end'] - result['contact_start'] == 80 and not entries
                assert before['outside_flags'] == after['outside_flags']
            else:
                assert not before['outside_flags'] & 2
                assert any(e['text_pc'] == 0x8e30 for e in entries)
            evidence.update(variant='return_after_reward' if repeat else 'initial_gift',
                            initial_state=before, final_state=after,
                            text_entries=[dict(frame=e['frame'], text_pc=e['text_pc']) for e in entries])
        stages.append(evidence)
    report = dict(passed=True, outside=0xd4, stages=stages,
                  latest_selected_sms_prefix=relative,
                  current_sms_state=dict(frame=cap['frames'], **result['last_state'], max_health=raw[0xda], keys=raw[0xde],
                                         crystals=sum(bool(b&128) for b in raw[0xcf:0xd8])),
                  all_npcs_complete=False, md_status='pending',
                  limits=['Only the SMS initial +10 gold gift and return without a second gift are verified.',
                          'MD approach did not enter this house; that attempt is not an accepted stage.',
                          'Capacity/currency boundaries, graphic restoration, timing, audio and the paired MD service remain open.',
                          'Ordinary controller input with inherited recorded approach protection; no new service assistance or progression imports.'])
    (ROOT / 'analysis/npc_gold_campaign_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(dict(passed=True, replayed_stages=len(stages))))


if __name__ == '__main__':
    main()
