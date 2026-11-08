"""Run the same compiled source-vector assertions on an existing actor kernel; never rebuild it."""
import argparse,contextlib,io,json,re,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'tools'))
from run_core import run
from archive_lossless_evidence import sha
p=argparse.ArgumentParser();p.add_argument('--work',required=True);p.add_argument('--kernel-name',required=True)
p.add_argument('--source-region',choices=['ntsc','pal'],required=True);p.add_argument('--case-start',type=int,required=True);p.add_argument('--case-count',type=int,default=500);a=p.parse_args()
work=root/'validation'/a.work;project=work/a.kernel_name
assert project.resolve().is_relative_to(root/'validation') and (project/'out/release/rom.bin').is_file()
source_regions=(a.source_region,)
cases=json.loads((work/a.source_region/'native-cases.json').read_bytes())[a.case_start:a.case_start+a.case_count]
assert cases
expected_reads=sum(c['expected'][12] for c in cases);ram_bytes=len(cases[0]['input_ram'])
profile=json.loads((work/'report.json').read_bytes());fire=profile.get('fire',False);actors=profile.get('actors');irq_status=profile.get('irq_status',False)
sy = {m[2].split('.lto_priv.')[0]: int(m[1], 16) & 65535 for line in (project / 'out/release/symbol.txt').read_text().splitlines()
      if (m := re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)', line))}
results = []
partitioned=a.case_start>0 or a.case_count is not None
run_prefix='compiled-'+a.source_region+('-'+a.kernel_name if partitioned else '')
for region in ('ntsc', 'pal'):
    stats = {}
    def observe(frame, raw):
        for name, size in [('intro_poll_done',2), ('intro_poll_cases',4), ('intro_poll_errors',4),
                           ('intro_poll_reads',4), ('intro_poll_first_failure',2)]:
            stats[name] = int.from_bytes(bytes(raw[(sy[name] + i) ^ 1] for i in range(size)), 'big')
        stats['frame'] = frame
    with contextlib.redirect_stdout(io.StringIO()):
        run(project / 'out/release/rom.bin', 5000, work / (run_prefix + '-' + region), set(), [], skip_intro=False,
            ram_observer=observe, stop_when=lambda: bool(stats.get('intro_poll_done')),
            core_options={'genesis_plus_gx_region_detect': 'pal' if region == 'pal' else 'auto'})
    assert stats['intro_poll_done'] == 1 and stats['intro_poll_errors'] == 0, stats
    assert stats['intro_poll_cases'] == len(cases) and stats['intro_poll_reads'] == expected_reads
    results.append(dict(region=region, **stats)); print(region, stats, flush=True)
report = dict(passed=True, diagnostic_only=True, source_vector_cases=len(cases), source_regions=source_regions,
    case_start=a.case_start,ram_bytes=ram_bytes,fire=fire,actors=actors,irq_status=irq_status,results=results,
    kernel_sha256=sha((project / 'out/release/rom.bin').read_bytes()),
    scope='Compiled68000 source semantic helper checked against the selected natural original source vectors '
          'on each target region. No physical publication scheduler or PCM claim.')
name = 'compiled-report.json' if a.source_region == 'both' else 'compiled-' + a.source_region + '-report.json'
if partitioned:name=run_prefix+'-report.json'
(work / name).write_text(json.dumps(report, indent=2) + '\n')
