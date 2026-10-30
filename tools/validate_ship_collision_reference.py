"""Compare controller ship-cache predictions with executed original Z80 2D41.

Controlled isolated fixture, never a campaign checkpoint. The production SMS
and MD ROMs are read only; only a separate test cartridge is patched.
"""
import contextlib
import io
import json
from run_core import ROOT, run
from archive_lossless_evidence import sha
from movement_reference import Hero, collision_cache


def main():
    original = (ROOT/'input/original.sms').read_bytes()
    folder = ROOT/'validation/ship-controller-v0304-01'
    assert not folder.exists()
    folder.mkdir()
    rows, expected = [], []
    for ship in [0, 1]:
        for foot5 in [0, 0x40, 0x80, 0xc0]:
            for foot6 in [0, 0x40, 0x80, 0xc0]:
                for pattern in range(256):
                    cache = bytearray(24)
                    for i in range(12):
                        cache[i*2] = (pattern+13*i)&255
                        cache[i*2+1] = (pattern+29*i)&255
                    cache[11] = foot5 | (pattern&63)
                    cache[13] = foot6 | ((pattern^0x25)&63)
                    tilemap = bytearray(1536)
                    for i in range(12):
                        off = 668+(i//4)*64+(i%4)*2
                        tilemap[off:off+2] = cache[i*2:i*2+2]
                    values = collision_cache(tilemap, Hero(x=128<<8, y=96<<8), canoe=True, ship=bool(ship))
                    result = bytearray(cache)
                    result[1::2] = bytes(values)
                    rows.append(bytes([ship])+cache+bytes(7))
                    expected.append(bytes(result))
    assert len(rows) == 8192
    image = bytearray(original)
    code, labels, fixes = bytearray(), {}, []
    def emit(value):
        code.extend(bytes.fromhex(value))
    def label(name):
        labels[name] = 0x3000+len(code)
    def jump(opcode, name):
        emit(opcode)
        fixes.append((len(code), name))
        emit('0000')
    emit('f331f0df2100c01101c001ff1f3600edb0af32fcff32fdff3e0132feff')
    emit('3e04d3bf3e80d3bfafd3bf3e81d3bf2100802206c03e0a3208c0')
    label('case')
    emit('af3202c03a08c032ffffdd2a06c0dd7e0032f0c0')
    for i in range(24):
        emit(f'dd7e{i+1:02x}32{0x48+i:02x}c0')
    emit('cd412d2148c01100c1011800edb03e013202c00603')
    label('hold')
    emit('dbbfe680')
    jump('ca', 'hold')
    emit('05')
    jump('c2', 'hold')
    emit('af3202c02a06c011200019cb74')
    jump('ca', 'pointer')
    emit('2100803a08c03c3208c0')
    label('pointer')
    emit('2206c02a00c0232200c0010020b7ed42')
    jump('c2', 'case')
    emit('3e013204c0')
    label('done')
    jump('c3', 'done')
    for offset, name in fixes:
        code[offset:offset+2] = labels[name].to_bytes(2, 'little')
    assert len(code) < 0xa00
    image[:3] = bytes.fromhex('c30030')
    image[0x3000:0x3000+len(code)] = code
    image[0x28000:0x28000+len(rows)*32] = b''.join(rows)
    image[0x2d7b] = 0xc9  # Stop at the common exit; original2D41..2D7A stays intact.
    assert image[0x2d41:0x2d7b] == original[0x2d41:0x2d7b]
    fixture = folder/'source.sms'
    fixture.write_bytes(image)
    outputs, done = {}, []
    captures = {1}
    def observe(frame, ram):
        if ram[4]:
            if not done:
                done.append(frame)
                captures.add(frame+1)
        if not ram[2]:
            return
        index = int.from_bytes(ram[:2], 'little')
        actual = ram[0x100:0x118]
        assert index < len(rows) and actual == expected[index], (frame, index, actual.hex(), expected[index].hex())
        if index in outputs:
            assert outputs[index] == actual
        outputs[index] = actual
    with contextlib.redirect_stdout(io.StringIO()):
        run(fixture, len(rows)*6+100, folder/'sms', captures, [], skip_intro=False,
            ram_observer=observe, stop_when=lambda: bool(done) and len(outputs) == len(rows) and
            (folder/'sms'/f'ram_{done[0]+1:05d}.bin').exists())
    assert done and len(outputs) == len(rows)
    raw = b''.join(outputs[i] for i in range(len(rows)))
    (folder/'source_outputs.bin').write_bytes(raw)
    digest = sha((ROOT/'gaw-megadrive.bin').read_bytes())
    assert digest == sha((ROOT/'versions/v0304-b7b4e150/gaw-megadrive-v0304.bin').read_bytes())
    report = dict(passed=True, version=304, md_sha256=digest, source_sha256=sha(original),
                  source_fixture_sha256=sha(image), source_routine_sha256=sha(original[0x2d41:0x2d7b]),
                  cases=len(rows), both_foot_upper_flag_pairs=16, byte_patterns=256, ship_states=[0, 1],
                  compared_cache_bytes=len(raw), source_outputs_sha256=sha(raw), source_completed_frame=done[0],
                  reference_sha256=sha((ROOT/'tools/movement_reference.py').read_bytes()),
                  validator_sha256=sha((ROOT/'tools/validate_ship_collision_reference.py').read_bytes()),
                  production_rom_unchanged=True, campaign_proof=False,
                  limits=['Isolated original2D41..2D7A execution with common exit replaced by RET in a separate fixture.',
                          'Input cache has canoe processing already applied. Tests ship transformation and low-byte preservation,not movement cadence,global phase or complete campaign.'])
    (folder/'report.json').write_bytes((json.dumps(report, indent=2)+'\n').encode())
    print('Original Z80 ship cache:', len(rows), 'cases and', len(raw), 'cache bytes exact;production ROM unchanged')


if __name__ == '__main__':
    main()
