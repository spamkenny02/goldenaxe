"""Fresh normal Continue from an independently reproduced game-written SMS SRAM.

Separate persistence test: this is not appended to the uninterrupted campaign.
"""
import argparse,contextlib,io,json,hashlib
from run_core import ROOT,run


def main():
    p=argparse.ArgumentParser();p.add_argument('--trace',required=True);p.add_argument('--trial',required=True);a=p.parse_args()
    source=(ROOT/'validation'/a.trace).resolve();assert source.is_relative_to(ROOT/'validation')
    report=json.loads((source/'report.json').read_bytes());cap=json.loads((source/'capture.json').read_bytes())
    proof=source.with_name(source.name+f'-assisted-fixed-replay-{cap["frames"]}')/'replay_report.json'
    re=json.loads(proof.read_bytes());assert report['passed'] and report['game_written_save'] and re['passed'] and re['game_written_sram_exact']
    sram=source/'game-written.srm';block=sram.read_bytes();assert hashlib.sha256(block).hexdigest()==report['sram_sha256']
    slot=report['slot'];payload=block[0x400+slot*0x400:0x650+slot*0x400]
    out=ROOT/'validation/sms-save-continue'/a.trial;assert not out.exists()
    controls=[(200,220,0),(920,935,0),(1000,1005,5),(1050,1065,8),(1300,1310,8)]
    with contextlib.redirect_stdout(io.StringIO()):
        run(ROOT/'input/original.sms',1920,out,{1920},controls,skip_intro=False,sram_in=sram)
    raw=(out/'ram_01920.bin').read_bytes()
    checks=dict(normal_game=raw[0x1d]==12,
        resume_room=int.from_bytes(raw[0xb9:0xbb],'little')==int.from_bytes(payload[0x12:0x14],'little'),
        health=raw[0x318]==payload[0x29],health_capacity=raw[0xda]==payload[0x2a],
        magic=raw[0xdb]==payload[0x2b],magic_capacity=raw[0xdc]==payload[0x2c],
        gold=raw[0xdd]==payload[0x2d],keys=raw[0xde]==payload[0x2e],
        inventory=raw[0xe0:0xf3]==payload[0x30:0x43],crystals=raw[0xcf:0xd8]==payload[0x1f:0x28])
    result=dict(passed=all(checks.values()),checks=checks,slot=slot,source_recording=a.trace,
        source_sram_sha256=report['sram_sha256'],game_written_sram_input=True,synthetic_sram_fixture=False,
        source_save_fixed_replayed=True,ram_writes=0,continuous_campaign=False,
        final_room=int.from_bytes(raw[0xb9:0xbb],'little'),
        scope='Fresh boot, normal Continue and actually written SRAM. Separate persistence branch; no synthetic SRAM, RAM edits or savestate.')
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
    if not result['passed']:raise SystemExit(1)


if __name__=='__main__':main()
