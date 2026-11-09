"""Pair SMS/MD NPC coverage; shared data or fixture tests never imply played coverage."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    sms = json.loads((ROOT / 'analysis/sms_npc_coverage_report.json').read_bytes())
    md = ROOT / 'versions/v0321-89c58333/gaw-megadrive-v0321.bin'
    rows = []
    paired = {}
    md_stages = []
    for name in ['md-npc-village94-house00-01', 'md-npc-village94-house02-01', 'md-npc-villagec7-house01-01']:
        folder = ROOT / 'validation/natural-service-route' / name
        if not (folder / 'report.json').exists():
            continue
        visit_report = json.loads((folder / 'report.json').read_bytes())
        cap = json.loads((folder / 'capture.json').read_bytes())
        suffix = f'-assisted-fixed-replay-{cap["frames"]}' if visit_report['ram_injections'] else '-fixed-replay'
        proof_path = folder.with_name(name + suffix) / 'replay_report.json'
        proof = json.loads(proof_path.read_bytes())
        assert visit_report['passed'] and proof['passed']
        assert not visit_report['new_assistance_writes']
        assert proof['ram_injections'] == visit_report['ram_injections']
        assert proof['rom_sha256'] == hashlib.sha256(md.read_bytes()).hexdigest()
        for visit in visit_report['visited']:
            assert visit['bitmap_exact_bytes'] == 1040
            key = (visit_report['room'], visit_report['outside'], visit['coordinate'], visit['text_pc'])
            paired[key] = dict(**visit, trace=folder.relative_to(ROOT).as_posix())
        md_stages.append(dict(trace=folder.relative_to(ROOT).as_posix(),
                              independent_replay=proof_path.relative_to(ROOT).as_posix()))
    for context in sms['plain_house_inventory']:
        key = (context['room'], context['outside'], context['coordinate'], context['text_pc'])
        observed = paired.get(key)
        row = dict(room=context['room'], outside=context['outside'],
                         coordinate=context['coordinate'], sms_text_pc=context['text_pc'],
                         sms_status=context['status'], md_status='pending_paired_campaign_visit',
                         text_comparison='pending', page_order_comparison='pending',
                         visual_restoration_comparison='pending',
                         transition_timing_comparison='pending', audio_comparison='pending')
        if observed:
            assert context['status'] == 'visited_current_state'
            row.update(md_status='visited_current_state_and_fixed_replayed',
                       text_comparison='selected_dialogue_and_final_1040_byte_bitmap_exact',
                       acknowledgment_and_movement='verified_on_both_platforms', md_evidence=observed)
        if key == (31, 199, 360, 40244):
            row.update(md_status='v321_final_bitmap_mismatch_observed',
                       text_comparison='extra_blank_line_causes_first_sentence_to_scroll_out',
                       diagnostic='analysis/npc_c7_empty_width_report.json',
                       private_candidate_status='room31-scoped correction cold-replayed; not released')
        rows.append(row)
    report = dict(
        sms_sha256=sms['source_sha256'], md_version='v0321',
        md_sha256=hashlib.sha256(md.read_bytes()).hexdigest(),
        all_npcs_complete=False, all_variants_complete=False,
        paired_campaign_conversations_verified=len(paired),
        paired_verification_scope='Selected dialogue, final 1040-byte bitmap, acknowledgment and resumed movement, with independent cold replays. Intermediate pages, physical pixels, full restoration, timing/audio remain pending.',
        md_stages=md_stages,
        ordinary_house_contexts=rows,
        additional_categories=sms['remaining_categories'],
        required_for_each_platform=[
            'Reach the NPC through normal game progression with the required items/quest flags',
            'Trigger, capture and acknowledge every page, including choice branches',
            'Record actual text and prerequisite/reward state; revisit when those conditions change',
            'Close the exchange and verify the restored room and normal movement',
            'Keep controller trace, ROM hash and independent cold-boot replay evidence',
        ],
        pair_comparison=['Text content, missing lines and page order',
                         'Choice branches and quest/reward effects',
                         'Opening/closing animation and restored graphics',
                         'Timing and music/sound effects in PAL and NTSC'],
        unresolved_sms_offsets=sms['reported_unresolved_sms_offsets'],
        limits=[
            'Both NPC campaigns are partial. Only the individual verified rows have new paired visit evidence.',
            'Existing MD selector, controlled-scene and full-campaign tests are separate evidence; they do not prove this exhaustive NPC coverage.',
            'Static contexts are a work list, not a census or completion-percentage denominator.',
            'ROM-resident strings without observed triggers are unresolved, not played conversations.',
        ],
    )
    path = ROOT / 'analysis/paired_npc_coverage_report.json'
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(dict(contexts=len(rows), paired_verified=len(paired), all_npcs_complete=False)))


if __name__ == '__main__':
    main()
