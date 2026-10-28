"""Full deterministic first burst/disappearance cycle in production loops."""
import contextlib,hashlib,io,json,re,sys
from actor_reference import ROOT
from run_core import run
from validate_actor_tick import PRESSES
def main():
 digest=hashlib.sha256((ROOT/'gaw-megadrive.bin').read_bytes()).hexdigest()
 version=next(row['version'] for row in json.loads((ROOT/'versions/index.json').read_bytes()) if row['sha256']==digest)
 label=sys.argv[sys.argv.index('--label')+1] if '--label' in sys.argv else f'v{version:04d}'
 assert label and all(c.isalnum() or c=='-' for c in label)
 baseline_version=294 if '--baseline-v0294' in sys.argv else (296 if '--baseline-v0296' in sys.argv else None)
 baseline=baseline_version is not None
 baseline_stem=f'v{baseline_version:04d}' if baseline else ''
 roms={294:'versions/v0294-508642dc/gaw-megadrive-v0294.bin',296:'versions/v0296-3446f41f/gaw-megadrive-v0296.bin'}
 symbols_by_version={294:'validation/stack-v0294-d2-all/symbol.txt',296:'validation/stack-v0296-d2-all02/symbol.txt'}
 md_rom=ROOT/(roms[baseline_version] if baseline else 'gaw-megadrive.bin')
 symbol_file=ROOT/(symbols_by_version[baseline_version] if baseline else 'megadrive/out/release/symbol.txt')
 sy={m[2].split('.lto_priv.')[0]:int(m[1],16)&65535 for l in symbol_file.read_text().splitlines() if (m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',l))}
 source=(ROOT/'input/original.sms').read_bytes();cases=[]
 for region in ['auto','pal']:
  for typ in ([0x7c] if '--type7c-only' in sys.argv else ([0x6a,0x6b,0x7c] if '--variant7c' in sys.argv else [0x6a,0x6b])):
   traces={};source_clock=[];clock_adjustments=[];clocks={}
   for tag,rom in [('sms',ROOT/'input/original.sms'),('md',md_rom)]:
    e=bytearray(768);e[0]=typ;stats=source[0x320ea+(typ-32)*4:0x320ea+(typ-31)*4];e[0x18:0x1b]=stats[:3];e[3]=stats[3]
    base=0x600 if tag=='sms' else sy['world_actor_state'];writes=[(2800,base,e)]
    if tag=='sms':writes += [(2800,0x310,(144<<8).to_bytes(2,'little')+(224<<8).to_bytes(2,'little')+bytes(4))]
    else:
     for k,v in [('hero_y',144<<8),('hero_x',224<<8),('hero_dy',0),('hero_dx',0)]:writes.append((2800,sy[k],v.to_bytes(2,'big')))
    rows={};clocks[tag]={}
    def observe(f,r):
     if f==2799:
      if tag=='sms':source_clock.append(r[0x2f])
      else:
       read32=lambda k:int.from_bytes(bytes(r[(sy[k]+i)^1] for i in range(4)),'big')
       shift=read32('world_clock_shift');clock=(read32('vtimer')-shift)&255
       adjustment=clock-source_clock[0]
       writes.append((2800,sy['world_clock_shift'],((shift+adjustment)&0xffffffff).to_bytes(4,'big')))
       clock_adjustments.append(adjustment)
     if not 2800<=f<3052:return
     clocks[tag][f]=r[0x2f] if tag=='sms' else ((int.from_bytes(bytes(r[(sy['vtimer']+i)^1] for i in range(4)),'big')-int.from_bytes(bytes(r[(sy['world_clock_shift']+i)^1] for i in range(4)),'big'))&255)
     rows[f]=bytes(r[0x600:0x900]) if tag=='sms' else bytes(r[(sy['world_actor_state']+i)^1] for i in range(768))
    with contextlib.redirect_stdout(io.StringIO()):run(rom,3052,ROOT/f'validation/{baseline_stem+"-baseline-" if baseline else (label+"-" if "--variant7c" in sys.argv else "")}burst-boss-gameplay-{typ:02x}-{region}-{tag}',{2848,2915,2945,3000},([(200,220,0)] if tag=='sms' else [])+PRESSES[:8],ram_writes=writes,ram_observer=observe,core_options={'genesis_plus_gx_region_detect':region})
    traces[tag]=rows
   (ROOT/f'validation/{baseline_stem+"-baseline" if baseline else label}-burst-clocks-{typ:02x}-{region}.json').write_text(json.dumps(dict(clocks=clocks,states={tag:{str(f):list(r[:16]) for f,r in rows.items()} for tag,rows in traces.items()}),indent=2)+'\n')
   mismatches=[dict(frame=f,differences=[(j,x,y) for j,(x,y) in enumerate(zip(traces['sms'][f],traces['md'][f])) if x!=y]) for f in traces['sms'] if traces['sms'][f]!=traces['md'][f]]
   if '--diagnose' in sys.argv:
    cases.append(dict(region=region,type=typ,frames=252,exact_frames=252-len(mismatches),first_mismatch=mismatches[0] if mismatches else None,all_768_actor_bytes_exact=not mismatches,clock_adjustments=clock_adjustments))
    print(region,hex(typ),'exact frames',252-len(mismatches),'first mismatch',mismatches[0]['frame'] if mismatches else None,flush=True)
    continue
   for f in traces['sms']:
    a,b=traces['sms'][f],traces['md'][f];assert a==b,(region,typ,f,[(j,x,y) for j,(x,y) in enumerate(zip(a,b)) if x!=y][:24])
   r=traces['md'];assert all(r[2908][n*48]==0x74 for n in range(8,16))
   assert r[2988][1]==14 and all(not r[3051][n*48] for n in range(8,16))
   if typ==0x6a:assert any(r[2944][n*48+1]==8 for n in range(8,16))
   else:assert any(r[2944][n*48+1]==6 for n in range(8,16))
   cases.append(dict(region=region,type=typ,frames=252,all_768_actor_bytes_exact=True,clock_adjustments=clock_adjustments,first_eight_shot_burst_and_variant_branch_and_clear_verified=True))
   print(region,hex(typ),'252 frames: first burst, variant and disappearance exact',flush=True)
 report=dict(md_sha256=hashlib.sha256(md_rom.read_bytes()).hexdigest(),source_sha256=hashlib.sha256(source).hexdigest(),cases=cases,full_game_ported=False,limits=['Controlled boss/hero records injected in exterior, initial stats from original; MD world clock explicitly aligned to source at fixture start. Production actor loop, animation-period-zero behavior, eight allocations, projectile flight/pause/variant branch, flash/cull and boss disappearance execute unchanged.','The initial world clock is explicitly aligned. Historical unaligned-clock diagnostics from older ROMs do not establish the current global phase; this controlled check does not prove natural dungeon boot-to-combat timing.','Stops before relocation random choices; natural dungeon fight, global clock/RNG, complete sprite/framebuffer/audio and hardware timing remain unproved.'])
 report.update(diagnostic='--diagnose' in sys.argv,all_cases_exact=all(case['all_768_actor_bytes_exact'] for case in cases),baseline_v0294=baseline_version==294,baseline_version=baseline_version)
 output=(f'analysis/burst_variant_7c_{baseline_stem+"_baseline" if baseline else label}_diagnostic.json' if '--diagnose' in sys.argv else (f'analysis/burst_variant_7c_{label}_gameplay_report.json' if '--variant7c' in sys.argv else 'validation/burst_boss_gameplay_report.json'))
 (ROOT/output).write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
