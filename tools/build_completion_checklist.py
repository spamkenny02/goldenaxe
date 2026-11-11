"""Build an open-world NPC/side-quest checklist, not a false 100% certificate."""
import collections
import hashlib
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE = 'https://megaforcemagazine.com/2021/06/gameplay-100-golden-axe-warrior-master-system-lord-paddle/'


def read(name):
    return json.loads((ROOT / 'analysis' / name).read_bytes())


def c_rows(file, array):
    text = (ROOT / 'megadrive/src' / file).read_text()
    body = re.search(r'\b' + re.escape(array) + r'\s*(?:\[[^\]]*\])+\s*=\s*\{(.*?)\};', text, re.S).group(1)
    return [list(map(int, row.split(','))) for row in re.findall(r'\{([\d, ]+)\}', body)]


def main():
    html = urllib.request.urlopen(GUIDE).read().decode('utf-8')
    ids = list(dict.fromkeys(re.findall(r'hcb-fetch-image-from="https://youtu.be/([\w-]{11})"', html)))
    assert len(ids) == 8
    topics = ['Labyrinthes 1 et 2', 'Bouclier magique et labyrinthe 3',
              'Montagnes et labyrinthe 4', 'Marais et labyrinthe 5',
              'Nendoria et labyrinthe 6', 'Volcans et labyrinthes 7 et 8',
              'Altorulia et labyrinthe 9', 'Death Adder et fin']
    guide = dict(page=GUIDE, author='Lord Paddle', article_date='2021-06-13',
                 html_sha256=hashlib.sha256(html.encode()).hexdigest(),
                 episodes=[dict(part=i + 1, url='https://www.youtube.com/watch?v=' + video,
                                article_topic=topics[i], viewing_status='pending',
                                npc_timestamps=[], quest_timestamps=[])
                           for i, video in enumerate(ids)],
                 limits='Article and eight embedded URLs inspected. Episode viewing and timestamps are populated only from explicit observations; no full-episode coverage is inferred.')
    observation_path = ROOT / 'analysis/lord_paddle_observations.json'
    observed_guide = json.loads(observation_path.read_bytes()) if observation_path.exists() else dict(episodes=[])
    for episode in guide['episodes']:
        observed = next((e for e in observed_guide['episodes'] if e['url'] == episode['url']), None)
        if observed:
            episode.update(viewing_status=observed['viewing_status'],
                           transcript_status=observed.get('transcript_status'),
                           duration_seconds=observed.get('duration_seconds'),
                           npc_timestamps=[o['seconds'] for o in observed['observations'] if o['kind']=='npc_dialogue'],
                           quest_timestamps=[o['seconds'] for o in observed['observations'] if o['kind']=='save_service'])
    guide['observation_ledger']='analysis/lord_paddle_observations.json'
    (ROOT / 'analysis/lord_paddle_guide_reference.json').write_text(json.dumps(guide, indent=2, ensure_ascii=False) + '\n')
    cases = []

    def add(category, identity, context, variants, evidence=None):
        cases.append(dict(id=category + ':' + identity, category=category, context=context,
                          required_variants=variants,
                          sms_status='pending', md_status='pending',
                          sms_md_comparison_status='pending',
                          guide_episode=None, guide_timestamp=None,
                          static_basis=evidence, observations=[]))

    for c in read('plain_house_dialogue_reference.json')['contexts']:
        add('plain_house', f'{c["outside"]:02x}/{c["room"]:02x}/{c["coordinate"]:04x}',
            {k: c[k] for k in ('room', 'outside', 'coordinate', 'text_pc')},
            ['Current-state text, all pages and acknowledgment',
             'Revisit after relevant story changes; identify whether the selector changes'],
            'analysis/plain_house_dialogue_reference.json')
    conditional = read('conditional_house_reference.json')
    for room, outside, coordinate, handler in conditional['nodes']:
        variants = ['Ninth-crystal flag absent', 'Ninth-crystal flag present'] if outside == 0xce else [
            'Prerequisite save[0x22] absent', 'Prerequisite present and reward save[0x47] absent: collect the reward',
            'Return after reward save[0x47] set']
        add('conditional_house', f'{outside:02x}/{room:02x}/{coordinate:04x}',
            dict(room=room, outside=outside, coordinate=coordinate, handler=handler), variants,
            'analysis/conditional_house_reference.json; megadrive/src/conditional_house.inc')
    quests = read('house_quest_reference.json')
    for entry in quests['tables']['62E9']:
        outside = entry['outside']
        for kind, coord in [('reward', 0x258), ('hint', 0x25c)]:
            add('equipment_quest', f'{outside:02x}/{kind}',
                dict(outside=outside, room=0x4f, coordinate=coord),
                ['Before required magic/item/capacity', 'Prerequisites met', 'Reward collected and return visit'],
                'analysis/house_quest_reference.json; megadrive/src/house_quest.inc')
    for outside, room in [(0x4c, 9), (0xc7, 15), (0x55, 15)]:
        add('house_item_quest', f'{outside:02x}/{room:02x}', dict(outside=outside, room=room),
            ['Before prerequisite, where applicable', 'Obtain reward with ordinary input',
             'Return with reward already owned', 'Visit connected floors and nearby hint NPCs'],
            'analysis/house_quest_reference.json; megadrive/src/house_quest.inc')
    for outside, amount in read('house_gold_reference.json')['records']:
        signed = amount if amount < 128 else amount - 256
        add('gold_house', f'{outside:02x}', dict(outside=outside, room=0x3f, coordinate=0x2dc, signed_amount=signed),
            ['First visit: text and real gold delta', 'Return after once-only flag is set',
             'Economic boundary branches if reachable; use an alternate cold-boot input branch'],
            'analysis/house_gold_reference.json; megadrive/src/house_gold.inc')
    for outside, kind in read('fairy_reference.json')['records']:
        add('fairy', f'{outside:02x}', dict(outside=outside, room=0xaf, kind=kind),
            ['Initial offer and reward/healing as applicable', 'Return after reward', 'Capacity boundary if reachable'],
            'analysis/fairy_reference.json')
    for outside, mode, parameter in c_rows('merchant_data.c', 'merchant_towns'):
        add('merchant', f'{outside:02x}', dict(outside=outside, mode=mode, parameter=parameter),
            ['Enter and leave without purchase', 'All offered goods: label and price',
             'Successful purchase and actual inventory/currency effect', 'Insufficient funds',
             'Already owned, inferior equipment, full capacity: each applicable reachable message',
             'Return after equipment and quest changes'],
            'megadrive/src/merchant_data.c; megadrive/src/merchant.inc')
    for outside, price in c_rows('healer_data.c', 'healer_prices'):
        add('healer_inn', f'{outside:02x}', dict(outside=outside, price=price),
            ['Initial offer', 'Refuse', 'Accept free night or pay actual price',
             'Insufficient funds for paid service', 'Restore health while preserving magic',
             'Night fade, wake-up dialogue and repeat visit'],
            'megadrive/src/healer_data.c; megadrive/src/healer.inc')
    for teacher, outside in enumerate([0xe6, 0xa3, 0x2c, 0xaa]):
        variants = [
            ['First introduction', 'Return without required inventory slot 8', 'Exchange slot 8 for spell level 1',
             'Level 1 with HP capacity below 72', 'Upgrade with HP capacity at least 72', 'Return at level 2'],
            ['First offer and repeat offer', 'Refuse', 'Accept with insufficient gold', 'Pay 50 for level 1',
             'Level 1 with HP capacity below 72', 'Upgrade offer: refuse, poor, pay 100', 'Return at level 2'],
            ['No spell with HP capacity below 72', 'Learn with HP capacity at least 72',
             'Level 1 before all nine crystals', 'Upgrade after all nine crystals', 'Return at level 2'],
            ['First acquisition', 'Return with spell already owned'],
        ][teacher]
        name, magic = [('Gillian','Foudre'),('Battler','Terre'),('Tyris','Feu'),('Linda','Eau')][teacher]
        add('teacher', f'{outside:02x}', dict(outside=outside, room=0xbf, teacher=teacher, name=name, magic=magic), variants,
            'megadrive/src/source_spell_teacher.c; megadrive/src/spell_teacher.inc')
    passages = read('paid_passage_reference.json')
    for outside in passages['towns']:
        add('paid_passage', f'{outside:02x}', dict(outside=outside, room=passages['room']),
            ['Offer', 'Refusal/exit', 'Insufficient funds', 'Payment and real destination', 'Return trip'],
            'analysis/paid_passage_reference.json')
    for identity, variants in [
        ('minigame', ['Enter', 'Refuse', 'Insufficient funds', 'Pay and play', 'Each reachable outcome/reward', 'Leave and return']),
        ('save_service', ['Every actual service location', 'Refuse', 'Save to each slot', 'Overwrite confirmation', 'Reload normal saved progression']),
        ('hidden_interiors', ['Audit all room/contact scripts and conditional entrances', 'Reveal every hidden NPC location', 'Visit once before and after its local quest']),
        ('optional_collectibles', ['Locate all optional equipment, HP/MP upgrades and quest items', 'Collect through normal play', 'Verify use and associated NPC follow-up']),
        ('curse_and_equipment', ['Identify curse/equipment dialogue conditions', 'Trigger and resolve each reachable condition', 'Verify equipment and later NPC replies']),
        ('reported_missing_strings', ['Find actual trigger or establish unreachable code for SMS DA58, DA7C, ED3C', 'Compare the same observed trigger on MD']),
    ]:
        add(identity, 'audit', {}, variants, 'Open audit; requires ROM reachability and/or actual guide observations')
    paired = read('paired_npc_coverage_report.json')
    known = {(r['outside'], r['room'], r['coordinate']): r for r in paired['ordinary_house_contexts']}
    for case in cases:
        if case['category'] != 'plain_house':
            continue
        c = case['context']; row = known[(c['outside'], c['room'], c['coordinate'])]
        case['sms_status'] = row['sms_status']
        case['md_status'] = row['md_status']
        if 'md_evidence' in row:
            case['sms_md_comparison_status'] = 'selected_dialogue_and_final_bitmap_verified; other checks pending'
            case['observations'].append(row['md_evidence'])
    for episode in observed_guide['episodes']:
        for observation in episode['observations']:
            for case in cases:
                if observation.get('checklist_id') == case['id']:
                    case['guide_episode'] = episode['part']
                    case['guide_timestamp'] = observation['seconds']
                    case['guide_observation'] = observation
    gillian = read('gillian_quest_campaign_report.json')
    fairies = read('npc_fairy_campaign_report.json')
    assert gillian['passed'] and fairies['passed']
    for case in cases:
        if case['id'] == 'teacher:e6':
            case['sms_status'] = 'three_variants_observed_and_replayed; remaining_variants_pending'
            case['observations'].append(dict(report='analysis/gillian_quest_campaign_report.json', variants=[d['variant'] for d in gillian['dialogues']]))
        if case['id'] == 'house_item_quest:c7/0f':
            case['sms_status'] = case['md_status'] = 'initial_golden_apple_reward_effect_and_exit_replayed; remaining_checks_pending'
            case['context'].update(reward='golden_apple', inventory_offset=8, source_label_pc=0xbbeb)
            case['observations'].append(dict(report='analysis/gillian_quest_campaign_report.json'))
        if case['id'] == 'fairy:c9':
            case['sms_status'] = case['md_status'] = 'initial_plus8_hp_reward_and_no_repeat_reward_replayed; other_checks_pending'
            case['observations'].append(dict(report='analysis/npc_fairy_campaign_report.json'))
        if case['id'] == 'gold_house:d4':
            assert read('npc_gold_campaign_report.json')['passed']
            case['sms_status'] = 'initial_plus10_gold_and_no_repeat_gift_replayed; other_checks_pending'
            case['observations'].append(dict(report='analysis/npc_gold_campaign_report.json'))
        if case['id'] in ('gold_house:f4','merchant:c7'):
            campaign_path=ROOT/'analysis/sms_npc_campaign_progress_report.json'
            if campaign_path.exists():
                assert json.loads(campaign_path.read_bytes())['passed']
                case['sms_status']=('initial_plus50_gold_replayed; return_and_other_checks_pending' if case['id']=='gold_house:f4'
                                    else 'one_key_purchase_for60_gold_and_exit_replayed; other_variants_and_checks_pending')
                case['observations'].append(dict(report='analysis/sms_npc_campaign_progress_report.json'))
        if case['id'] in ('gold_house:a1','merchant:94','healer_inn:94'):
            campaign_path=ROOT/'analysis/sms_npc_campaign_progress_report.json'
            if campaign_path.exists():
                report=json.loads(campaign_path.read_bytes());assert report['passed']
                case['sms_status']={
                    'gold_house:a1':'initial_plus30_gold_replayed; return_and_other_checks_pending',
                    'merchant:94':'one_key_purchase_for60_gold_and_exit_replayed; other_variants_pending',
                    'healer_inn:94':'free_health_refill_preserving_magic_currency_inventory_and_exit_replayed; other_variants_pending',
                }[case['id']]
                case['observations'].append(dict(report='analysis/sms_npc_campaign_progress_report.json'))
        if case['id'] in ('teacher:a3','gold_house:b4','equipment_quest:27/reward','equipment_quest:50/reward'):
            campaign_path=ROOT/'analysis/sms_npc_campaign_progress_report.json'
            if campaign_path.exists():
                report=json.loads(campaign_path.read_bytes());assert report['passed']
                case['sms_status']={
                    'teacher:a3':'first_offer_and_level1_purchase_for50_gold_observed_and_replayed; remaining_variants_pending',
                    'gold_house:b4':'initial_plus30_gold_replayed; return_and_other_checks_pending',
                    'equipment_quest:27/reward':'plate_mail_reward_and_exit_replayed; entrance_monsters_defeated; other_variants_pending',
                    'equipment_quest:50/reward':'long_sword_reward_and_exit_replayed; other_variants_pending',
                }[case['id']]
                case['observations'].append(dict(report='analysis/sms_npc_campaign_progress_report.json'))
        campaign_path=ROOT/'analysis/sms_npc_campaign_progress_report.json'
        if campaign_path.exists():
            report=json.loads(campaign_path.read_bytes())
            if report.get('sixth_crystal_reward_and_exit_verified'):
                upgrades={
                    'teacher:e6':'introduction_exchange_and_level2_upgrade_observed_and_replayed; other_variants_pending',
                    'teacher:a3':'level1_purchase_for50_and_level2_purchase_for100_observed_and_replayed; other_variants_pending',
                    'gold_house:7d':'initial_plus30_gold_replayed; return_and_other_checks_pending',
                    'gold_house:e7':'initial_plus30_gold_replayed; return_and_other_checks_pending'}
                if report.get('seventh_crystal_reward_and_exit_verified'):
                    upgrades['gold_house:ac']='initial_plus30_gold_replayed; return_and_other_checks_pending'
                if report.get('eighth_crystal_reward_and_exit_verified'):
                    upgrades.update({
                        'equipment_quest:b1/reward':'dragon_mail_reward_and_exit_replayed; other_variants_pending',
                        'equipment_quest:6a/reward':'flame_sword_reward_and_exit_replayed; other_variants_pending',
                        'paid_passage:3c':'actual10_gold_payment_and_destination1a_replayed; other_variants_pending'})
                if report.get('ninth_crystal_reward_and_exit_verified'):
                    upgrades.update({
                        'paid_passage:1a':'actual10_gold_return_payment_and_destination3c_replayed; other_variants_pending',
                        'paid_passage:3c':'actual10_gold_payment_destination1a_and_reverse_trip_replayed; other_variants_pending'})
                if case['id'] in upgrades:
                    case['sms_status']=upgrades[case['id']]
                    case['observations'].append(dict(report='analysis/sms_npc_campaign_progress_report.json',milestone='sixth_crystal'))
    coverage_path=ROOT/'analysis/sms_npc_coverage_report.json'
    if coverage_path.exists():
        coverage=json.loads(coverage_path.read_bytes())
        for visit in coverage['visits']:
            identity=f'plain_house:{visit["outside"]:02x}/{visit["room"]:02x}/{visit["coordinate"]:04x}'
            case=next(c for c in cases if c['id']==identity)
            case['sms_status']='visited_current_state_and_fixed_replayed; relevant_revisits_pending'
            evidence=dict(report='analysis/sms_npc_coverage_report.json',stage=visit['stage'],
                text_pc=visit['text_pc'],entry_frame=visit['entry_frame'],
                acknowledged_and_walked_away_frame=visit['acknowledged_and_walked_away_frame'])
            if evidence not in case['observations']:case['observations'].append(evidence)
    for branch_path in sorted((ROOT/'analysis').glob('sms-conditional-*.json')):
        branch=json.loads(branch_path.read_bytes());assert branch['passed']
        folder=ROOT/'validation'/branch['trace'];capture=json.loads((folder/'capture.json').read_bytes())
        proof=folder.with_name(folder.name+f'-assisted-fixed-replay-{capture["frames"]}')/'replay_report.json'
        assert json.loads(proof.read_bytes())['passed']
        for visit in branch['visits']:
            identity=f'conditional_house:{branch["outside"]:02x}/{branch["room"]:02x}/{visit["coordinate"]:04x}'
            case=next(c for c in cases if c['id']==identity)
            variants=case.setdefault('sms_variants_observed',[])
            if branch['variant'] not in variants:variants.append(branch['variant'])
            case['sms_status']='selected_conditional_variants_observed_and_replayed; remaining_variants_pending'
            case['observations'].append(dict(report=branch_path.relative_to(ROOT).as_posix(),
                separate_branch=True,variant=branch['variant'],**visit))
    for case in cases:
        if case['category']=='conditional_house':
            required=({'ninth_crystal_absent','ninth_crystal_present'} if case['context']['outside']==0xce else
                      {'prerequisite_absent','collect_actual_100_gold_reward','reward_already_collected'})
            case['sms_required_variants_complete']=required.issubset(set(case.get('sms_variants_observed',[])))
            if case['sms_required_variants_complete']:
                case['sms_status']='all_required_conditional_variants_observed_and_fixed_replayed'
    def receipt(trace):
        folder=ROOT/'validation'/trace
        capture=json.loads((folder/'capture.json').read_bytes())
        assert json.loads((folder/'report.json').read_bytes())['passed']
        proof=folder.with_name(folder.name+f'-assisted-fixed-replay-{capture["frames"]}')/'replay_report.json'
        assert json.loads(proof.read_bytes())['passed']
        return dict(trace=trace,frame=capture['frames'],proof=proof.relative_to(ROOT).as_posix())
    def add_observation(identity,status,trace):
        case=next(c for c in cases if c['id']==identity)
        case['observations'].append(receipt(trace));case['sms_status']=status
    for filename,key,category in [('sms_remaining_magic_campaign.json','completed_visits','teacher'),
                                  ('sms_fairy_census_campaign.json','completed_rewards','fairy'),
                                  ('sms_gold_funding_campaign.json','completed_gifts','gold_house')]:
        path=ROOT/'analysis'/filename
        if path.exists():
            for row in json.loads(path.read_bytes()).get(key,[]):
                add_observation(f'{category}:{row["outside"]:02x}',
                    'selected_acquisition_and_exit_observed_and_fixed_replayed; other_variants_pending',row['trace'])
    shield=ROOT/'analysis/sms_dragon_shield_campaign.json'
    if shield.exists():
        data=json.loads(shield.read_bytes())
        if data.get('passed'):add_observation('house_item_quest:4c/09','dragon_shield_gift_and_exit_fixed_replayed; hint_and_return_variants_pending',data['last_verified_prefix'])
    for outside in (0x27,0x50,0xb1,0x6a):
        trace=f'natural-service-route/sms-npc-quest-hint-{outside:02x}-01'
        folder=ROOT/'validation'/trace
        if (folder/'report.json').exists():
            capture=json.loads((folder/'capture.json').read_bytes())
            if folder.with_name(folder.name+f'-assisted-fixed-replay-{capture["frames"]}').exists():
                add_observation(f'equipment_quest:{outside:02x}/hint','pre_reward_hint_rendered_acknowledged_and_fixed_replayed; other_variants_pending',trace)
    service=ROOT/'analysis/sms_service_refusal_campaign.json'
    if service.exists():
        for row in json.loads(service.read_bytes()).get('completed_visits',[]):
            identity=({'merchant':'merchant','healer':'healer_inn','save':'save_service'}[row['kind']]
                      +(':'+f'{row["outside"]:02x}' if row['kind']!='save' else ':audit'))
            add_observation(identity,'selected_service_refusal_and_exit_fixed_replayed; successful_transactions_and_other_contexts_pending',row['trace'])
    result = dict(requirement='ALL NPCs and ALL side quests on SMS and MD, including relevant return visits and conditional text variants',
                  requirement_complete=False, census_proved_complete=False,
                  completion_percentage=None,
                  cases=cases, category_counts=dict(collections.Counter(c['category'] for c in cases)),
                  reference_guide='analysis/lord_paddle_guide_reference.json',
                  important_limits=[
                      'Cases are initial obligations, not a proved complete census. Hidden/scripted NPCs and optional collectibles need further inventory.',
                      'A guide advertised as 100% is a reference, not automatic proof it visits every text variant.',
                      'Every required variant needs observed reachable conditions. Alternative irreversible outcomes may require separate cold-boot controller branches.',
                      'Static extraction, selector tests and the existing ending video do not certify played exhaustive coverage.',
                      'Do not validate a row from text presence alone, a formatter return pointer, or the final bitmap alone.',
                  ],
                  acceptance=['Each NPC located and reached on both systems', 'All reachable dialogue pages and relevant quest-state variants captured',
                              'Every secondary quest completed and rewards/effects checked on both systems',
                              'Source/native text, choice, graphics restoration, animation timing and audio compared in PAL and NTSC',
                              'Independent input replay with explicit assistance provenance',
                              'Record new 100% videos from the completed in-house routes; retain the earlier MD video as a campaign-only recording'])
    (ROOT / 'analysis/full_completion_checklist.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(dict(cases=len(cases), category_counts=result['category_counts'], complete=False)))


if __name__ == '__main__':
    main()
