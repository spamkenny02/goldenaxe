"""Verify a Continue recording's actual game-written SRAM provenance."""
import json,hashlib
from pathlib import Path
from run_core import ROOT
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verified_sram(folder,capture):
    assert folder.is_relative_to(ROOT/'validation/game-written-save-load')
    r=json.loads((folder/'report.json').read_bytes())
    assert r['passed'] and r['game_written_save'] and not r['synthetic_sram_fixture'] and r['raw_sram_fixed_replay_exact'] and r['save_whole_ram_png_exact'] and r['reload_ram_writes']==0
    source=ROOT/'validation'/r['source_trace'];s=json.loads((source/'report.json').read_bytes());assert s['passed'] and s['game_written_save'] and s['payload_source_ram_exact'] and s['primary_state_imports']==0
    sram=Path(capture['sram_input']).resolve();assert sram.is_relative_to(source) and sha(sram)==r['source_sram_sha256']==s['sram_sha256']
    fixed=ROOT/r['fixed_replay_trace'];proof=json.loads((fixed/'replay_report.json').read_bytes());assert proof['passed'] and proof['raw_sram_exact'] and proof['sram_sha256']==sha(sram)
    assert (fixed/'replayed.srm').read_bytes()==sram.read_bytes()
    assert capture['rom_sha256']==r['rom_sha256']==s['rom_sha256'] and not capture['test_ram_writes']
    return sram
