"""Bind the controlled v310 frontend comparison to captures and actual seed work."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from validate_playable_sprite_limit import symbols

def main():
    base=ROOT/'validation/minigame-rng-v0310-01';refs={}
    def read(path):
        data=path.read_bytes();refs[path.relative_to(ROOT).as_posix()]=sha(data);return data
    report=json.loads(read(ROOT/'analysis/minigame_rng_v0310_report.json'))
    digest=sha((ROOT/'gaw-megadrive.bin').read_bytes());assert report['passed'] and report['md_sha256']==digest
    assert report['production_rng_seed_controlled'] and report['production_refresh_provider_controlled']
    assert len(report['cases'])==12 and {(r['region'],r['scenario'])for r in report['cases']}=={(region,name)for region in ['auto','pal']for name in ['ordinary','lucky','inverse','replay','poor','entry-no']}
    sy=symbols(ROOT/'megadrive/out/release/symbol.txt');seed_samples=[]
    fixture=read(base/'controlled-source.sms');original=(ROOT/'input/original.sms').read_bytes()
    assert fixture[0x3a20:0x3a3d]==original[0x4e1:0x4fe]
    assert all(fixture[n]==original[n]for n in range(len(original))if not(0x4e1<=n<0x4e4 or 0x3a00<=n<0x3a0d or 0x3a20<=n<0x3a3d))
    for row in report['cases']:
        for tag in ['sms','md']:
            folder=base/f'{row["scenario"]}-{row["region"]}-{tag}'
            capture=json.loads(read(folder/'capture.json'));assert capture['frames']==6600 and capture['sram_input']is None
            assert capture['rom_sha256']==(sha(fixture)if tag=='sms'else digest)
            assert capture['test_ram_writes'],'Controlled fixture must disclose its setup'
            for f in [3480,3600,3900,4100,4500,4900,5300,5700,6000,6600]:
                for stem,ext in [('ram','bin'),('frame','png')]:read(folder/f'{stem}_{f:05d}.{ext}')
            if tag=='md':
                seeds=[w for w in capture['test_ram_writes']if w['address']==sy['game_rng_seed']]
                assert len(seeds)==len(row['roll_inputs']) and all(w['byte_count']==2 for w in seeds)
                for n,roll in enumerate(row['roll_inputs']):
                    f=4100+n*400;raw=read(folder/f'ram_{f:05d}.bin');at=sy['game_rng_seed']
                    seed=int.from_bytes(bytes(raw[(at+i)^1]for i in range(2)),'big');assert seed==0x733c,(row,f,seed)
                    seed_samples.append(dict(region=row['region'],scenario=row['scenario'],frame=f,controlled_low5_roll=roll,seed_after_draw=seed))
        assert row['all_observed_unit_gold_changes_exact'] and row['dialogue_bitmap_bytes_exact']==1040 and row['confirmation_font_tiles_exact']==4 and row['confirmation_frame_bytes_exact']==48
    assert len(seed_samples)==28
    sources=['tools/validate_minigame_rng_v0310.py','tools/audit_minigame_rng_v0310.py','megadrive/src/main.c','megadrive/src/minigame.inc','megadrive/src/minigame_core.inc','megadrive/src/source_rng.c','megadrive/src/source_rng_runtime.c','megadrive/out/release/symbol.txt']
    frozen=ROOT/'validation/v0310-minigame-rng-sources';assert not frozen.exists();frozen.mkdir()
    index={}
    for name in sources:
        data=read(ROOT/name);index[name]=sha(data);(frozen/(name.replace('/','__'))).write_bytes(data)
    (frozen/'source_index.json').write_bytes((json.dumps(index,indent=2)+'\n').encode())
    result=dict(passed=True,md_sha256=digest,source_sha256=sha(original),controlled_sms_fixture_sha256=sha(fixture),cases=12,regions=['NTSC','PAL'],controlled_seeded_draw_samples=seed_samples,trace_frames_each=6600,trace_count=24,evidence=refs,source_snapshot=frozen.relative_to(ROOT).as_posix(),full_game_validated=False,limits=report['limits']+['Seed733C after each of28 deliberately reset draws confirms production adapter execution; it does not prove the natural global random stream.'])
    (ROOT/'analysis/minigame_rng_v0310_audit_report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
    print('12 SMS/MD frontend cases audited;28 production seeded draws verified')

if __name__=='__main__':main()
