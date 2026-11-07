"""Prepare the PAL candidate D2 continuation and the preceding reward audit."""
import ast
from pathlib import Path
root=Path(__file__).resolve().parents[2];work=Path(__file__).resolve().parent;project=work/'isolated/project'
s=(work/'audit_after_d1.py').read_text().replace('c0046','palc0046')
s=s.replace('versions/candidates/palc0046-9e747d38/gaw-megadrive-palc0046.bin','versions/candidates/c0046-9e747d38/gaw-megadrive-c0046.bin')
s=s.replace('palc0046_d1_auto_report.json','c0046_d1_pal_report.json')
s=s.replace("'md-auto-palc0046-","'md-pal-palc0046-").replace("'md-palc0046-","'md-pal-palc0046-")
s=s.replace("'md-pal-palc0046-fairy-service01'","'md-palc0046-fairy-service01'")
s=s.replace("candidate='palc0046',region='auto'","candidate='c0046',region='pal'")
s=s.replace("    assert not report.get('deaths',0)","    assert not report.get('deaths',0) and cap['core_options']['genesis_plus_gx_region_detect']=='pal'")
s=s.replace("archive=ROOT/'analysis/palc0046-after-d1'","""stream=project/'validation/palc0046-after-d1-cold-stream/completed.json';receipt=load(stream)
assert receipt['passed'] and receipt['cold_boot_count']==1 and receipt['rom_sha256']==digest and len(receipt['checkpoints'])==7
assert all(c['whole_ram_png_exact'] for c in receipt['checkpoints'])
assert receipt['checkpoints'][-1]['frames']==stages[-1]['frame']
paths.update([work/'prepare_pal_after_d1.py',work/'prepare_pal_d2.py'])
archive=ROOT/'analysis/palc0046-after-d1'""")
p=work/'audit_pal_after_d1.py';assert not p.exists();ast.parse(s);p.write_text(s,encoding='utf-8')
s=(project/'tools/continue_d2_c0046.py').read_text().replace('c0046','palc0046').replace('V317','PAL c0046')
s=s.replace("COMMON=['--assisted-prefix'","COMMON=['--pal','--retry-isolated-foes','--wake-sentinels','--assisted-prefix'")
s=s.replace("current='md-palc0046-d2-entry01'","current='md-pal-palc0046-d2-entry01'")
s=s.replace("current='md-auto-'+trial","current='md-pal-'+trial")
s=s.replace('md-auto-palc0046-d2-boss01','md-pal-palc0046-d2-boss01').replace('md-auto-palc0046-d2-exit01','md-pal-palc0046-d2-exit01')
s=s.replace("'--planning-step','32'","'--planning-step','16'")
s=s.replace("'--target-room','0x144','--frames'","'--target-room','0x144','--collect-gem','--frames'")
s=s.replace('frame(COMBAT,current)+10000','frame(COMBAT,current)+24000')
s=s.replace("names=('continue_d2_palc0046.py'","names=('campaign_stream_replay.py','cold_replay_stream.py','run_core.py','continue_d2_palc0046.py'")
s=s.replace("if __name__=='__main__':main()","""if __name__=='__main__':
    from campaign_stream_replay import streamed_replays
    with streamed_replays(helper,ROOT/'validation/palc0046-d2-cold-stream'):
        main()
""")
p=project/'tools/continue_d2_palc0046.py';assert not p.exists();ast.parse(s);p.write_text(s,encoding='utf-8')
print('PAL reward audit and D2 controller prepared; nothing launched before preceding cold proofs pass')
