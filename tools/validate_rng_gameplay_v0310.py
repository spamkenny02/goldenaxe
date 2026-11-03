"""Cold opening/gameplay smoke, plus fixed full-RAM/image replay of v310."""
import contextlib, io, json, subprocess, sys
from run_core import ROOT, run
from validate_actor_tick import PRESSES
from validate_playable_sprite_limit import symbols
from archive_lossless_evidence import sha

def main():
    rom=ROOT/'gaw-megadrive.bin';sy=symbols(ROOT/'megadrive/out/release/symbol.txt');rows=[]
    for region in ['auto','pal']:
        folder=ROOT/('validation/rng-gameplay-v0310-02/'+region);assert len(sys.argv)>1 or not folder.exists()
        states=[];seed_changes=[];previous=None
        def observe(f,raw):
            nonlocal previous
            def word(n):return int.from_bytes(bytes(raw[(sy[n]+i)^1]for i in range(2)),'big')
            assert not word('sound_unhandled_command'),f
            if f>=2500 and word('game_state')==12 and word('hero_state')==1:
                states.append(dict(frame=f,room=word('room_id'),x=word('hero_x')>>8,y=word('hero_y')>>8,health=word('hero_health')))
            seed=word('game_rng_seed')
            if previous is not None and seed!=previous:seed_changes.append(dict(frame=f,before=previous,after=seed))
            previous=seed
        captures={60,300,800,1000,1500,2300,2700,3000,3140}
        if len(sys.argv)>1:
            if sys.argv[1]!=region:continue
            target=ROOT/sys.argv[2]
            with contextlib.redirect_stdout(io.StringIO()):run(rom,3140,target,captures,PRESSES,ram_observer=observe,core_options={'genesis_plus_gx_region_detect':region})
            (target/'observations.json').write_bytes((json.dumps(dict(states=states,seed_changes=seed_changes))+'\n').encode())
            return
        subprocess.run([sys.executable,__file__,region,folder.relative_to(ROOT).as_posix()],check=True)
        observations=json.loads((folder/'observations.json').read_bytes());states=observations['states'];seed_changes=observations['seed_changes']
        assert states and all(s['health']>0 for s in states)
        assert len({(s['room'],s['x'],s['y'])for s in states})>1
        assert seed_changes,'Production seeded stream did not execute'
        fixed=folder.with_name(region+'-fixed');assert not fixed.exists()
        subprocess.run([sys.executable,__file__,region,fixed.relative_to(ROOT).as_posix()],check=True)
        for f in captures:
            for stem,ext in [('ram','bin'),('frame','png')]:assert(folder/f'{stem}_{f:05d}.{ext}').read_bytes()==(fixed/f'{stem}_{f:05d}.{ext}').read_bytes()
        for p in [folder,fixed]:
            capture=json.loads((p/'capture.json').read_bytes());assert not capture['test_ram_writes'] and not capture['sram_input']
        rows.append(dict(region=region,trace=folder.relative_to(ROOT).as_posix(),whole_ram_png_exact_frames=sorted(captures),controllable_samples=len(states),first=states[0],last=states[-1],seed_changes=seed_changes,audio_errors=0,ram_writes=0,sram_imports=0))
        print(region,'Cold boot, movement, production seed updates and exact replay passed',flush=True)
    report=dict(passed=True,md_sha256=sha(rom.read_bytes()),cases=rows,limits=['3140-frame opening/initial-gameplay smoke in PAL/NTSC. Fixed replay proves reproducibility only, not SMS RNG phase equivalence.','No full campaign, optional-content or physical-hardware claim.'])
    (ROOT/'analysis/rng_gameplay_v0310_report.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())

if __name__=='__main__':main()
