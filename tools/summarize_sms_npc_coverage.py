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
    census_path=ROOT/'analysis/sms_plain_house_census_campaign.json'
    census=read(census_path) if census_path.exists() else None
    names=STAGES[:]
    if census:
        for house in census['completed_houses']:
            family,name=house['trace'].split('/')
            assert family=='natural-service-route'
            if name not in names:names.append(name)
    for name in names:
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
    # Reward windows use a different source path. Keep their evidence separate
    # from the nine formatter-entry/completion-verified plain conversations.
    reward = ROOT / 'validation/natural-service-route/sms-sms-npc-villagec7-oil02'
    if (reward / 'report.json').exists():
        rr = read(reward / 'report.json')
        rc = read(reward / 'capture.json')
        proof = reward.with_name(reward.name + f'-assisted-fixed-replay-{rc["frames"]}') / 'replay_report.json'
        assert rr['passed'] and read(proof)['passed']
        assert rr['first_state']['oil'] == 0 and rr['last_state']['oil'] == 1
        assert rr['visited'] == [0x1f, 0x0f, 0xc7]
        result['verified_reward_visits'] = [dict(
            trace=reward.relative_to(ROOT).as_posix(), outside=0xc7,
            rooms=rr['visited'], reward='golden_apple', end_frame=rc['frames'],
            inventory_offset=8,source_label_pc=0xbbeb,
            legacy_trace_naming_warning='The historical oil filename/state key actually tracks the golden apple. Magic oil is inventory slot2, not slot8.',
            independent_fixed_replay=proof.relative_to(ROOT).as_posix(),
            new_assistance_writes=rr['new_assistance_writes'],
            text_content_comparison='pending',
            scope='Real NPC reward, acknowledgment, both stairs and exterior return. Not counted as a standard 050C/627A plain conversation.')]
        result['latest_selected_prefix'] = reward.relative_to(ROOT).as_posix()
    continuation = ROOT / 'validation/natural-dungeon-combat/sms-auto-sms-npc-d2-key03'
    if (continuation / 'report.json').exists():
        cr = read(continuation / 'report.json')
        cc = read(continuation / 'capture.json')
        cp = continuation.with_name(continuation.name + f'-assisted-fixed-replay-{cc["frames"]}') / 'replay_report.json'
        assert cr['room_cleared'] and cr['failure'] is None and read(cp)['passed']
        result['latest_selected_prefix'] = continuation.relative_to(ROOT).as_posix()
        result['current_campaign_checkpoint'] = dict(
            frame=cc['frames'], room=cr['last_state']['room'],
            health=cr['last_state']['health'], keys=cr['last_state']['keys'],
            crystals=1, second_boss_defeated=False,
            scope='Three key rooms completed in dungeon two. The later exploratory boss attempt is not a selected campaign stage.')
    gillian_path = ROOT / 'analysis/gillian_quest_campaign_report.json'
    if gillian_path.exists():
        gr = read(gillian_path)
        assert gr['passed']
        result['verified_teacher_visits'] = dict(npc=gr['npc'], magic=gr['magic'],
            source=gillian_path.relative_to(ROOT).as_posix(), dialogues=gr['dialogues'],
            golden_apple_consumed=True, spell_level=1, all_variants_complete=False)
        result['latest_selected_prefix'] = 'validation/' + gr['latest_selected_prefix']
        result['current_campaign_checkpoint'] = gr['current_sms_state']
    fairy_path = ROOT / 'analysis/npc_fairy_campaign_report.json'
    if fairy_path.exists():
        fr = read(fairy_path)
        assert fr['passed']
        result['verified_fairy_visits'] = dict(source=fairy_path.relative_to(ROOT).as_posix(),
            outside=0xc9, initial_reward=True, return_without_second_reward=True,
            all_variants_complete=False)
        latest = ROOT / 'validation' / fr['latest_selected_sms_prefix']
        report = read(latest / 'report.json'); cap = read(latest / 'capture.json')
        assert report['passed']
        result['latest_selected_prefix'] = latest.relative_to(ROOT).as_posix()
        result['current_campaign_checkpoint'] = dict(frame=cap['frames'], **report['last_state'],
            crystals=1, second_boss_defeated=False,
            scope='Axe acquired, Gillian apple exchange and C9 life-fairy reward/return replayed. Failed exploratory dungeon-two boss branches are not selected.')
    gold_path = ROOT / 'analysis/npc_gold_campaign_report.json'
    if gold_path.exists():
        gold = read(gold_path)
        assert gold['passed']
        result['verified_gold_house_visits'] = dict(source=gold_path.relative_to(ROOT).as_posix(),
            outside=0xd4, gift=10, return_without_second_gift=True, all_variants_complete=False)
        result['latest_selected_prefix'] = 'validation/' + gold['latest_selected_sms_prefix']
        result['current_campaign_checkpoint'] = dict(**gold['current_sms_state'], second_boss_defeated=False)
    campaign_path = ROOT / 'analysis/sms_npc_campaign_progress_report.json'
    if campaign_path.exists():
        campaign = read(campaign_path)
        assert campaign['passed']
        result['played_campaign_continuation'] = campaign_path.relative_to(ROOT).as_posix()
        result['latest_selected_prefix'] = 'validation/' + campaign['latest_selected_prefix']
        result['current_campaign_checkpoint'] = campaign['current_sms_state']
        result['full_campaign_complete'] = campaign['full_campaign_complete']
    if census:
        result['ordinary_house_census_branch']=census_path.relative_to(ROOT).as_posix()
        result['current_npc_census_prefix']=census['last_verified_prefix']
        result['known_ordinary_houses_pending']=len(census['remaining_houses'])
    out = ROOT / 'analysis/sms_npc_coverage_report.json'
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('observed_acknowledged_conversations', 'static_plain_house_context_count', 'all_npcs_complete')}))


if __name__ == '__main__':
    main()
