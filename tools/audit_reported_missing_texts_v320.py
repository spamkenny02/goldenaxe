"""Reproduce the three reported text omissions without assuming SMS reachability.

File offsets in bank 3 are not Z80 addresses: DA58 maps to 9A58 only
while bank 3 occupies the 8000-BFFF window. The same address in bank 2
can name an actor routine. This audit deliberately makes no gameplay change.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SMS_SHA = '852e068e331dbfb01b9c38a62eecf81ce5b9f0f1bd10fff497117bd885c716c9'
MD_SHA = '9e5b0abed80678ce864a0bb796c17e97047d1d34e5227a5275bf9336129ceaff'


def occurrences(data, needle):
    return [n for n in range(len(data) - len(needle) + 1)
            if data.startswith(needle, n)]


def main():
    sms = (ROOT / 'input/original.sms').read_bytes()
    md = (ROOT / 'versions/v0320-9e5b0abe/gaw-megadrive-v0320.bin').read_bytes()
    assert hashlib.sha256(sms).hexdigest() == SMS_SHA
    assert hashlib.sha256(md).hexdigest() == MD_SHA
    contexts = json.loads((ROOT / 'analysis/plain_house_dialogue_reference.json').read_text())['contexts']
    rows = []
    for address in (0xDA58, 0xDA7C, 0xED3C):
        text = sms[address:sms.index(0, address) + 1]
        pc = 0x8000 + (address & 0x3FFF)
        references = occurrences(sms, pc.to_bytes(2, 'little'))
        assert not occurrences(md, text)
        rows.append(dict(
            sms_file_offset=f'{address:04X}', sms_text_bank=3,
            z80_address_when_bank3_selected=f'{pc:04X}',
            text_bytes_hex=text.hex(),
            text_preview=text[:-1].decode('latin-1'),
            present_verbatim_in_v320=False,
            raw_little_endian_pointer_occurrences=[f'{n:05X}' for n in references],
            exported_plain_house_contexts=[c for c in contexts if c['text_pc'] == pc],
            sms_reachable=None,
            classification='absent MD asset; SMS dialogue trigger not established',
        ))
    # The sole raw 589A match belongs to the bank-2 actor state dispatch.
    assert rows[0]['raw_little_endian_pointer_occurrences'] == ['09A1F']
    assert not rows[1]['raw_little_endian_pointer_occurrences']
    assert not rows[2]['raw_little_endian_pointer_occurrences']
    assert sms[0x4F44:0x4F47] == bytes.fromhex('211b9a')  # LD HL,9A1B
    table = [int.from_bytes(sms[n:n+2], 'little') for n in range(0x9A1B, 0x9A2B, 2)]
    assert table[2] == 0x9A58
    assert sms[0x9A58:0x9A5C] == bytes.fromhex('cdb74ad8')  # CALL 4AB7; RET C
    assert all(not row['exported_plain_house_contexts'] for row in rows)
    report = dict(
        source_sha256=SMS_SHA, published_v320_sha256=MD_SHA,
        asset_absence_confirmed=True, gameplay_omission_confirmed=False,
        unused_in_sms_proven=False, rom_modified=False,
        findings=rows,
        rejected_pointer_match=dict(
            file_offset='09A1F', bank=2, table='09A1B',
            table_targets=[f'{n:04X}' for n in table],
            table_selected_at='04F44: LD HL,9A1B',
            target_bytes='09A58: CALL 4AB7; RET C',
            native_counterpart='megadrive/src/actors.c (4F44 ->9A1B)',
            reason='Actor-state code pointer in bank 2, not text in bank 3.',
        ),
        plain_house_contexts_examined=len(contexts),
        limits=[
            'A byte search cannot rule out a computed pointer or another encoding.',
            'Existing house-dialogue exports are not a complete reachability proof.',
            'No new SMS NPC walkthrough or runtime text-pointer trace was performed by this audit.',
            'Do not add a quest condition or classify these strings as unused solely from these results.',
        ],
        next_evidence_needed='Observe an original SMS text frontend receiving 9A58, 9A7C or AD3C with bank 3 selected, and record the NPC/quest state; alternatively establish a complete source call/data-flow proof.',
    )
    output = ROOT / 'analysis/reported_missing_texts_v0320_report.json'
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('Three absent strings confirmed; SMS reachability remains unproved. ROM unchanged.')


if __name__ == '__main__':
    main()
