"""Audit the private source-built audio fix; gameplay validation remains separate."""
import json,struct
from pathlib import Path
from run_core import ROOT
from archive_lossless_evidence import sha,freeze


def main():
    base=ROOT/'validation/intro-audio-v0313';project=base/'candidate11'
    refs={};paths=set()
    def read(p):
        raw=p.read_bytes();refs[p.relative_to(ROOT).as_posix()]=sha(raw);paths.add(p);return raw
    def load(p):return json.loads(read(p))
    digest=sha(read(project/'gaw-megadrive.bin'))
    assert digest=='c53381c459a1e6254a8c9f1cfad1b8cda482cc0614697ad566133b28335e07a7'
    public=sha((ROOT/'gaw-megadrive.bin').read_bytes())
    assert public=='48fb6e924a520ff579d3fb4eabe4aac365e9a37eed3dc33ff0dabfdc232e1932'
    original=read(ROOT/'input/original.sms')
    assert original[0xb48:0xb53]==bytes.fromhex('3e0c210404320bde220cde')
    cases=[];irq_count=0;pixels=0
    for region,start,complete in [('ntsc',23,5959),('pal',20,5952)]:
        source=base/'candidate05/validation'/('boot-sms-'+region)
        target=project/'validation'/('boot-md-'+region)
        a=load(source/'observations.json');b=load(target/'observations.json')
        assert a['rom_sha256']==sha(original) and b['rom_sha256']==digest
        assert a['core_sha256']==b['core_sha256']
        for r in (a,b):
            assert r['no_buttons'] and r['no_ram_mutations'] and not r['unsupported_audio_commands']
            assert r['first_active_channel_frame']==start and r['story_completion_frame']==complete
        offsets=[];variant_differences=[]
        for n in range(1,66):
            x,y=a['maps'][str(n)],b['maps'][str(n)]
            assert set(x['sha256'])&set(y['sha256']),(region,n,'no matching1536-byte map')
            offsets.append(y['first_frame']-x['first_frame'])
            if set(y['sha256'])-set(x['sha256']):variant_differences.append(n)
        assert min(offsets)>=-1 and max(offsets)<=1
        count=6500-start+1
        for filename,width in [('audio_channels.bin',192),('audio_tempo.bin',4),('audio_psg.bin',16)]:
            x=read(source/filename);y=read(target/filename)
            assert len(x)==len(y)==6500*width
            for f in range(start,6501):
                u,v=x[(f-1)*width:f*width],y[(f-1)*width:f*width]
                if width==16:
                    def audible(raw):
                        values=struct.unpack('<8H',raw)
                        return values[:6]+((values[6] if values[7] else 0),values[7])
                    u,v=audible(u),audible(v)
                assert u==v,(region,filename,f)
        suffix='-pal' if region=='pal' else ''
        title=load(project/f'validation/title_cadence{suffix}-natural-audio11_report.json')
        assert title['md_sha256']==digest and title['absolute_boot_timing_exact']
        assert title['relative_timing_exact'] and title['absolute_title_timing_exact']
        assert not any(title['map_start_offsets']+title['palette_start_offsets'])
        assert len(title['pixel_checks'])==20 and not any(p['normalized_pixel_mismatches'] for p in title['pixel_checks'])
        for sample in title['pixel_checks']:
            for tag,key in [('sms','sms_frame'),('md','md_frame')]:
                read(project/f'validation/{tag}-title-cadence{suffix}-natural-audio11'/f'frame_{sample[key]:05d}.png')
        irq_count+=count;pixels+=20
        cases.append(dict(region=region,first_music_frame=start,story_completion_frame=complete,
            exact_audio_irq_states=count,stable_story_maps_checked=65,
            text_start_offsets=[min(offsets),max(offsets)],
            additional_intermediate_map_variants=variant_differences,
            absolute_title_timing_exact=True,normalized_title_images=20))
    # Check the vendored SDK change against its actual installed source.
    sdk=ROOT.parents[1]/'work/sgdk'
    sdk_base=project/'sdk-base-sys.c'
    if sdk_base.exists():assert sdk_base.read_bytes()==(sdk/'src/sys.c').read_bytes()
    else:sdk_base.write_bytes((sdk/'src/sys.c').read_bytes())
    old=read(sdk_base);license=read(project/'SGDK-license.txt')
    assert license==(sdk/'license.txt').read_bytes()
    old_clear=b'    dst = (u16*) RAM;\r\n    len = 0x8000;\r\n    while(len--) *dst++ = 0;'
    new_clear=b'    {\r\n        vu32 *clear = (vu32*) RAM;\r\n        u16 count = 0x4000;\r\n        while(count--) *clear++ = 0;\r\n    }'
    assert old.count(old_clear)==1
    header=b'/* Derived from SGDK sys.c; only the hard-reset RAM-clear store width changes.\r\n'+license+b'\r\n*/\r\n'
    assert read(project/'megadrive/src/gaw_sgdk_sys.c')==header+old.replace(old_clear,new_clear)
    changed=[]
    for p in (ROOT/'megadrive/src').rglob('*'):
        if not p.is_file():continue
        other=project/'megadrive/src'/p.relative_to(ROOT/'megadrive/src')
        if p.read_bytes()!=other.read_bytes():changed.append(p.name);read(p);read(other)
    assert sorted(changed)==['intro.inc','main.c','sound.inc']
    for name in ['build_intro_audio_candidate11.py','compare_intro_audio_title_candidate11.py']:
        read(ROOT/'validation'/name)
    for name in ['probe_intro_audio_boot.py','summarize_intro_audio_candidate11_v0313.py','validate_title_cadence.py']:
        read(ROOT/'tools'/name)
    read(project/'megadrive/out/release/symbol.txt');read(project/'build_report.json')
    archive=ROOT/'analysis/intro-audio-deadline-v0313'
    manifest=freeze(ROOT,archive,paths,dict(candidate_md_sha256=digest,
        scope='Private source-built intro/title audio evidence; atomic audio queue and music-relative loading deadline; no public release.'),[project],cleanup=False)
    result=dict(passed=True,md_sha256=digest,public_md_sha256=public,candidate_promoted=False,
        targeted_intro_audio_title_checks_passed=True,exact_audio_irq_states=irq_count,
        normalized_title_images=pixels,stable_story_maps_checked=130,cases=cases,
        cold_gameplay_replay_passed=False,full_game_validated=False,
        archive_manifest=archive.relative_to(ROOT).as_posix()+'/manifest.json',
        archive_manifest_sha256=sha((archive/'manifest.json').read_bytes()),evidence=refs,
        limits=['Channel records,tempo and audible PSG registers compare from the first music IRQ through6500,including fade and title. Muted noise frequency is excluded; waveforms/hardware are not proved.',
                'Each story line has a matching1536-byte map. Additional transient native variants remain recorded; this is not per-frame scene/sprite equivalence.',
                'Gameplay remains unverified on this exact atomic-queue/deadline binary. Earlier prototype first-crystal evidence is not attributed to this binary; public v313 is unchanged.'])
    (ROOT/'analysis/intro_audio_candidate11_v0313_report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('Private audio/title gates:',irq_count,'exact IRQs;',pixels,'title images; gameplay remains unverified')


if __name__=='__main__':main()
