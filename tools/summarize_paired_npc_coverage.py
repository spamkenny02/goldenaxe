"""Pair SMS/MD NPC coverage; shared data or fixture tests never imply played coverage."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    sms = json.loads((ROOT / 'analysis/sms_npc_coverage_report.json').read_bytes())
    md = ROOT / 'versions/v0321-89c58333/gaw-megadrive-v0321.bin'
    rows = []
    for context in sms['plain_house_inventory']:
        rows.append(dict(room=context['room'], outside=context['outside'],
                         coordinate=context['coordinate'], sms_text_pc=context['text_pc'],
                         sms_status=context['status'], md_status='pending_paired_campaign_visit',
                         text_comparison='pending', page_order_comparison='pending',
                         visual_restoration_comparison='pending',
                         transition_timing_comparison='pending', audio_comparison='pending'))
    report = dict(
        sms_sha256=sms['source_sha256'], md_version='v0321',
        md_sha256=hashlib.sha256(md.read_bytes()).hexdigest(),
        all_npcs_complete=False, all_variants_complete=False,
        paired_campaign_conversations_verified=0,
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
            'The SMS route is partial. Nine observed conversations have not yet been paired with new MD campaign visits.',
            'Existing MD selector, controlled-scene and full-campaign tests are separate evidence; they do not prove this exhaustive NPC coverage.',
            'Static contexts are a work list, not a census or completion-percentage denominator.',
            'ROM-resident strings without observed triggers are unresolved, not played conversations.',
        ],
    )
    path = ROOT / 'analysis/paired_npc_coverage_report.json'
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(dict(contexts=len(rows), paired_verified=0, all_npcs_complete=False)))


if __name__ == '__main__':
    main()
