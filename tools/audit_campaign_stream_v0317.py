"""Bind shared cold replay results and count the avoided repeated prefixes."""
import argparse,json,re
from pathlib import Path
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--report',default='campaign_stream_v0317_report.json')
    parser.add_argument('--stream',action='append')
    args=parser.parse_args()
    assert re.fullmatch(r'[a-zA-Z0-9_-]+\.json',args.report)
    target=ROOT/'analysis'/args.report;assert not target.exists()
    refs={}
    def read(p):
        raw=evidence(p);refs[p.relative_to(ROOT).as_posix()]=sha(raw);return raw
    def load(p):return json.loads(read(p))
    digest=sha(read(ROOT/'gaw-megadrive.bin'));streams=[]
    for label in (args.stream or ['v0317-earth-cold-stream','v0317-d4-cold-stream']):
        folder=(ROOT/'validation'/label).resolve();assert folder.is_relative_to(ROOT/'validation')
        done=load(folder/'completed.json')
        assert done['passed'] and done['rom_sha256']==digest
        assert done['cold_boot_count']==1 and not done['primary_state_imports']
        assert done['checkpoints']==load(folder/'checkpoints.json')['checkpoints']
        previous=0;total=0;endpoints=[]
        for index,row in enumerate(done['checkpoints'],1):
            trace=(ROOT/'validation'/row['trace']).resolve();assert trace.is_relative_to(ROOT/'validation')
            c=load(trace/'capture.json');end=c['frames']
            proof=trace.with_name(trace.name+f'-assisted-fixed-replay-{end}')
            q=load(proof/'replay_report.json')
            assert q['passed'] and q['rom_sha256']==c['rom_sha256']==digest
            assert end==row['frames'] and end>previous and row['whole_ram_png_exact']
            assert q['cold_boot_count']==1 and q['primary_state_imports']==0
            assert q['shared_cold_stream']==folder.relative_to(ROOT).as_posix()
            assert q['shared_stream_checkpoint']==index and q['new_emulated_frames']==end-previous
            assert q['whole_ram_bytes']==65536 and q['final_png_exact'] and not q['feedback_reads']
            assert q['live_boss_guard_check'] and not q['boss_assistance']
            assert c['sram_input'] is None
            for name,h in q['evidence'].items():assert sha(read(trace/name))==h
            for stem,extension in [('ram','bin'),('frame','png')]:
                name=f'{stem}_{end:05d}.{extension}'
                assert read(trace/name)==read(proof/name)
            assert q['driver_sha256']==sha(read(ROOT/'tools/cold_replay_stream.py'))
            endpoints.append(dict(trace=row['trace'],frames=end,new_emulated_frames=end-previous))
            total+=end;previous=end
        assert previous==done['emulated_frames']
        streams.append(dict(name=label,checkpoints=endpoints,cold_boot_count=1,
            emulated_frames=previous,independent_restarts_would_emulate=total,
            avoided_repeated_prefix_frames=total-previous))
    result=dict(passed=True,version=317,md_sha256=digest,streams=streams,
        total_checkpoints=sum(len(r['checkpoints']) for r in streams),
        total_cold_boots=len(streams),
        total_emulated_frames=sum(r['emulated_frames'] for r in streams),
        total_independent_restart_frames=sum(r['independent_restarts_would_emulate'] for r in streams),
        avoided_repeated_prefix_frames=sum(r['avoided_repeated_prefix_frames'] for r in streams),
        whole_ram_and_final_png_exact=True,primary_state_imports=0,feedback_reads=False,
        evidence=refs,driver_sha256=sha(Path(__file__).read_bytes()),
        limits=['Only the independent fixed-input proof reader is shared across increasing checkpoints. The planning/game runs are separate and still compared against complete RAM and PNG.',
                'Emulated-frame savings count the proof reader, not all development or wall-clock time. No game timing, guard rules, boss damage or comparison scope is shortened.'])
    target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('Shared cold proof:',result['total_checkpoints'],'checkpoints;',
          result['avoided_repeated_prefix_frames'],'repeated prefix frames avoided')


if __name__=='__main__':main()
