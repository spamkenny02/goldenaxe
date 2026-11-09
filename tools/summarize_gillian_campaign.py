"""Verify the in-house SMS apple/axe/Gillian chain and the MD apple effect."""
import hashlib
import json
from pathlib import Path
from run_core import ROOT


def read(path):
    return json.loads(path.read_bytes())


def verified(relative, route=False):
    path = ROOT / 'validation' / relative
    cap = read(path / 'capture.json')
    result = read(path / ('route_report.json' if route else 'report.json'))
    proof_path = path.with_name(path.name + f'-assisted-fixed-replay-{cap["frames"]}') / 'replay_report.json'
    proof = read(proof_path)
    assert proof['passed'] and proof['rom_sha256'] == cap['rom_sha256']
    assert cap['sram_input'] is None and result['failure'] is None
    assert result['reached_entrance'] if route else result.get('passed', result.get('room_cleared'))
    raw = (path / f'ram_{cap["frames"]:05d}.bin').read_bytes()
    entry = dict(trace=relative, end_frame=cap['frames'],
                 rom_sha256=cap['rom_sha256'], fixed_replay=proof_path.relative_to(ROOT).as_posix(),
                 evidence_sha256={name: hashlib.sha256((path/name).read_bytes()).hexdigest()
                                  for name in ('capture.json','controls.json','assistance.json')})
    return path, cap, result, raw, entry


def main():
    stages = []
    chain = [
        ('natural-dungeon-combat/sms-auto-sms-npc-d2-supply-exit02', False),
        ('natural-dungeon-route/sms-sms-npc-axe-return-entry01', True),
        ('natural-dungeon-combat/sms-auto-sms-npc-axe-item01', False),
        ('natural-dungeon-combat/sms-auto-sms-npc-axe-exit01', False),
        ('natural-dungeon-route/sms-sms-npc-fire-teacher-entry02', True),
        ('natural-service-route/sms-npc-fire-teacher-intro01', False),
        ('natural-dungeon-route/sms-sms-npc-fire-teacher-entry03', True),
        ('natural-service-route/sms-npc-fire-teacher-learn01', False),
        ('natural-dungeon-route/sms-sms-npc-fire-teacher-entry04', True),
        ('natural-service-route/sms-npc-fire-teacher-return02', False),
    ]
    for relative, route in chain:
        path, cap, result, raw, entry = verified(relative, route)
        assert cap['rom_sha256'] == '852e068e331dbfb01b9c38a62eecf81ce5b9f0f1bd10fff497117bd885c716c9'
        stages.append(entry)
        if 'axe-item' in relative:
            assert raw[0xe1] == 1
        if 'axe-exit' in relative:
            assert raw[0xe1] == raw[0xdf] == 1 and raw[0xba] == 0
        if 'entry02' in relative:
            assert result['required_chop_verified'] and result['required_chop'] == [0xe6,0x7b]
    events = read(path / 'dialogue_observations.json')['events']
    dialogs = []
    for pc, variant in [(0xad89,'first_introduction'), (0xae39,'golden_apple_exchange'), (0xaf95,'return_below_72_hp_capacity')]:
        begin = next(e for e in events if e['event_pc'] == 0x524 and e['text_pc'] == pc and e['room'] == 0xbf and e['outside'] == 0xe6)
        finish = next(e for e in events if e['event_pc'] == 0x6e3 and e['frame'] >= begin['frame']
                      and e['caller'] == begin['caller'] and e['stack_pointer'] == begin['stack_pointer'])
        dialogs.append(dict(text_pc=pc, variant=variant, entry_frame=begin['frame'], render_return_frame=finish['frame'],
                            caller=begin['caller'], stack_pointer=begin['stack_pointer'],
                            text_bytes_hex=begin['text_bytes_hex'], quest_state_hex=begin['save_bytes_hex']))
    assert raw[0xe8] == 0 and raw[0xe4] == 1 and raw[0xdb] == raw[0xdc] == 48 and raw[0xda] == 32
    md = verified('natural-service-route/md-npc-golden-apple01')
    sms = verified('natural-service-route/sms-sms-npc-villagec7-oil02')
    for data in (md, sms):
        report = data[2]
        assert report['first_state']['oil'] == 0 and report['last_state']['oil'] == 1
        assert report['last_state']['flags'] & 2 and report['visited'] == [31,15,199]
        assert report['new_assistance_writes'] == 0
    result = dict(passed=True, sms_stages=stages, npc='Gillian', magic='Foudre',
                  dialogues=dialogs, sms_golden_apple_consumed=True, sms_spell_level=1,
                  sms_max_magic_before=24, sms_max_magic_after=48,
                  sms_axe_acquired_and_equipped=True, hidden_tree_cut_verified=True,
                  latest_selected_prefix=chain[-1][0],
                  golden_apple_initial_gift_both_platforms_verified=True,
                  golden_apple_evidence=[sms[4],md[4]],
                  current_sms_state=dict(frame=cap['frames'], room=int.from_bytes(raw[0xb9:0xbb],'little'),
                                         hp=raw[0x318], hp_capacity=raw[0xda], gold=raw[0xdd],
                                         crystals=sum(bool(x&128)for x in raw[0xcf:0xd8]),
                                         golden_apple=raw[0xe8], axe=raw[0xe1], spell=raw[0xe4], magic=raw[0xdb]),
                  historical_naming_warning='oil/oil_stairs follows inventory slot8 (golden apple); fire-teacher follows Gillian/Foudre. Preserve historical trace paths but use source item/text labels for interpretation.',
                  all_quests_complete=False, all_npcs_complete=False,
                  limits=['Three observed SMS Gillian variants, not all six prerequisite/upgrade states.',
                          'No MD Gillian exchange/comparison yet. Only the initial C7 apple reward effect is verified on both.',
                          'Source 0524 formatter entry and06E3 return are paired by stack pointer and caller. Page graphics/timing/audio comparison remains pending.',
                          'Inherited approach protection is fully recorded. No assistance writes are added during the service visits; no progression or save imports.'])
    target = ROOT / 'analysis/gillian_quest_campaign_report.json'
    target.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(dict(passed=True,dialogues=len(dialogs),state=result['current_sms_state'])))


if __name__ == '__main__': main()
