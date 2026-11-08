"""Reuse the PAL-vector kernel after the terminal GCC temporary-path failure was corrected."""
import contextlib,io,json,re,sys,types
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'tools'))
from run_core import run
from archive_lossless_evidence import sha
work=root/'validation/v319-native-intro-poll-callback01'
project=work/'kernel2'
a=types.SimpleNamespace(source_region='pal')
source_regions=('pal',)
cases=json.loads((work/'pal/native-cases.json').read_bytes())
expected_reads=sum(case['expected'][12] for case in cases)
assert all(not (work/('compiled-pal-'+region)).exists() for region in ('ntsc','pal'))
sy = {m[2].split('.lto_priv.')[0]: int(m[1], 16) & 65535 for line in (project / 'out/release/symbol.txt').read_text().splitlines()
      if (m := re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)', line))}
results = []
for region in ('ntsc', 'pal'):
    stats = {}
    def observe(frame, raw):
        for name, size in [('intro_poll_done',2), ('intro_poll_cases',4), ('intro_poll_errors',4),
                           ('intro_poll_reads',4), ('intro_poll_first_failure',2)]:
            stats[name] = int.from_bytes(bytes(raw[(sy[name] + i) ^ 1] for i in range(size)), 'big')
        stats['frame'] = frame
    with contextlib.redirect_stdout(io.StringIO()):
        run(project / 'out/release/rom.bin', 5000, work / ('compiled-' + a.source_region + '-' + region), set(), [], skip_intro=False,
            ram_observer=observe, stop_when=lambda: bool(stats.get('intro_poll_done')),
            core_options={'genesis_plus_gx_region_detect': 'pal' if region == 'pal' else 'auto'})
    assert stats['intro_poll_done'] == 1 and stats['intro_poll_errors'] == 0, stats
    assert stats['intro_poll_cases'] == len(cases) and stats['intro_poll_reads'] == expected_reads
    results.append(dict(region=region, **stats)); print(region, stats, flush=True)
report = dict(passed=True, diagnostic_only=True, source_vector_cases=len(cases), source_regions=source_regions, results=results,
    kernel_sha256=sha((project / 'out/release/rom.bin').read_bytes()),
    scope='Compiled68000 source semantic helper checked against the selected natural original source vectors '
          'on each target region. No physical publication scheduler or PCM claim.')
name = 'compiled-report.json' if a.source_region == 'both' else 'compiled-' + a.source_region + '-report.json'
(work / name).write_text(json.dumps(report, indent=2) + '\n')
