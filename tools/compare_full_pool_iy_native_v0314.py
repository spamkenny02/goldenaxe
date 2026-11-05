"""Compare unchanged compiled production bodies with the original full-pool cases."""
import contextlib,io,json
from run_core import ROOT,run
from archive_lossless_evidence import sha
from validate_playable_sprite_limit import symbols
from build_full_pool_iy_native_probe import function

def main():
    base=ROOT/'validation/full-pool-iy-v0314-native01';project=base/'megadrive';index=json.loads((base/'source_index.json').read_bytes())
    assert index['production_rom_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes())
    text=(ROOT/'megadrive/src/actors.c').read_bytes().decode();assert sha(text.encode())==index['actors_sha256']
    assert sha((project/'src/main.c').read_bytes())==index['fixture_source_sha256']
    for name,token in [('allocator','static u8 *create_projectile_type('),('boss','void first_boss_behavior(')]:assert sha(function(text,token).encode())==index['unchanged_body_sha256'][name]
    out=base/'capture';sy=symbols(project/'out/release/symbol.txt');rom=project/'out/release/rom.bin'
    with contextlib.redirect_stdout(io.StringIO()):run(rom,120,out,{120},[],skip_intro=False)
    raw=(out/'ram_00120.bin').read_bytes();word=lambda n:int.from_bytes(bytes(raw[(sy[n]+i)^1] for i in range(2)),'big')
    assert word('probe_ready')==0xa531
    result=bytes(raw[(sy['probe_results']+i)^1] for i in range(768));after=word('probe_after_pool');assert after==0x5a
    source=ROOT/'validation/full-pool-iy-v0314-source02';baseline=(source/'iy-8000/ram_00020.bin').read_bytes();assert result==baseline[0x600:0x900]
    cases=[]
    for iy,address in ((0xc6f0,0xc6fa),(0xc8d0,0xc8da),(0xc900,0xc90a)):
        sms=(source/f'iy-{iy:04x}/ram_00020.bin').read_bytes()
        differences=[dict(source_address=0xc600+i,native_value=x,sms_value=y) for i,(x,y) in enumerate(zip(result,sms[0x600:0x900])) if x!=y]
        if address<0xc900:assert differences==[dict(source_address=address,native_value=0xa7,sms_value=0)]
        else:assert not differences and sms[0x90a]==0 and after==0x5a
        cases.append(dict(incoming_iy=iy,actor_differences=differences,native_after_pool=after,sms_after_pool=sms[0x90a]))
    report=dict(probe_passed=True,native_equivalence_passed=False,md_sha256=index['production_rom_sha256'],native_fixture_sha256=sha(rom.read_bytes()),native_matches_rom_iy_actor_bytes=768,source_cases=cases,unchanged_production_bodies=index,production_fix_applied=False,natural_reachability_proven=False,natural_gameplay_proof=False,scope='Controlled native M68K routine comparison. The full-pool allocator and boss bodies are copied unchanged from production. They match the original ROM-IY case, but do not reproduce the supplied inherited RAM-IY side effect. Actual caller register provenance remains to inspect before a production fix.')
    (ROOT/'analysis/full_pool_iy_native_comparison_v0314_report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
