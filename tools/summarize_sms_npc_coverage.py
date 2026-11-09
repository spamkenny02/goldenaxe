"""Inventory current SMS NPC visits without counting static strings as played text."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGES = [
    'sms-npc-village94-house00-01',
    'sms-npc-village94-house02-01',
    'sms-npc-villagec7-house01-01',
    'sms-npc-villagec7-house1f-01',
]


def read(path):
    return json.loads(path.read_bytes())


def main():
    rom_sha = hashlib.sha256((ROOT / 'input/original.sms').read_bytes()).hexdigest()
    visits = []
    stages = []
    for name in STAGES:
        folder = ROOT / 'validation/natural-service-route' / name
        report = read(folder / 'report.json')
        capture = read(folder / 'capture.json')
        observations = read(folder / 'dialogue_observations.json')
        assert report['passed'] and report['source_sha256'] == rom_sha
        assisted = bool(report['primary_ram_writes'])
        suffix = f'-assisted-fixed-replay-{capture["frames"]}' if assisted else '-fixed-replay'
        replay_path = folder.with_name(name + suffix) / 'replay_report.json'
        replay = read(replay_path)
        assert replay['passed'], replay_path
        for visit in report['visited']:
            entry = next(e for e in observations['events']
                         if e['event_pc'] == 0x050c and e['frame'] == visit['entry_frame']
                         and e['text_pc'] == visit['text_pc'])
            assert visit['render_completed']
            assert any(e['event_pc'] == 0x627a
                       and visit['entry_frame'] <= e['frame'] < visit['acknowledged_and_walked_away_frame']
                       for e in observations['events'])
            visits.append(dict(stage=name, room=report['room'], outside=report['outside'],
                               **visit, x=entry['x'], y=entry['y'],
                               save_bytes_hex=entry['save_bytes_hex'],
                               text_bytes_hex=entry['text_bytes_hex'],
                               sms_file_offset=entry['sms_file_offset']))
        stages.append(dict(stage=name, end_frame=capture['frames'],
                           replay=str(replay_path.relative_to(ROOT)).replace('\\', '/'),
                           assisted_approach=assisted,
                           new_assistance_writes=report.get('new_assistance_writes', 0)))
    contexts = read(ROOT / 'analysis/plain_house_dialogue_reference.json')['contexts']
    verified = {(v['room'], v['outside'], v['coordinate'], v['text_pc']) for v in visits}
    inventory = [dict(c, status='visited_current_state' if
                     (c['room'], c['outside'], c['coordinate'], c['text_pc']) in verified
                     else 'pending') for c in contexts]
    result = dict(source_sha256=rom_sha, full_campaign_complete=False,
                  all_npcs_complete=False, all_text_variants_complete=False,
                  observed_acknowledged_conversations=len(visits),
                  static_plain_house_context_count=len(contexts),
                  denominator_warning='Static plain-house contexts are not a census of all NPCs or all dialogue variants. No global completion percentage is derived.',
                  visits=visits, stages=stages, plain_house_inventory=inventory,
                  remaining_categories=[
                      'Remaining plain-house NPCs and return visits after quest changes',
                      'Conditional house dialogues before and after their prerequisite/reward flags',
                      'Quest givers, hint givers and gift NPCs, including connected house floors',
                      'Merchants, teachers, fairies, paid passages and minigames: offers, refusals and results',
                      'Story, dungeon and ending text outside house conversations',
                  ],
                  reported_unresolved_sms_offsets=['0xDA58', '0xDA7C', '0xED3C'],
                  unresolved_scope='Presence in ROM is established; gameplay triggers remain unproved. These strings are not counted as visited.',
                  method='Continuous cold-boot SMS controller route. Read-only original text-entry/completion observation, dismissal followed by movement, and independent fixed-input official-core replay. Approach hurt-byte protection is recorded where used; no quest or save imports.')
    out = ROOT / 'analysis/sms_npc_coverage_report.json'
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('observed_acknowledged_conversations', 'static_plain_house_context_count', 'all_npcs_complete')}))


if __name__ == '__main__':
    main()
