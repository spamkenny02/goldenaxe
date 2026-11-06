"""Bind the first-world correction to natural source observations and regressions."""
import json
from pathlib import Path

from PIL import Image

from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from run_core import ROOT
from validate_playable_sprite_limit import symbols


def indexed_pixels(path, system):
    image=Image.open(path).convert('RGB')
    if system=='md':image=image.crop((0,16,256,208))
    else:image=image.crop((0,0,256,192))
    levels=([0,98,172,238],[0,102,170,238],[0,98,172,238]) if system=='md' else ([0,82,172,255],[0,85,170,255],[0,82,172,255])
    tables=[bytes(min(range(4),key=lambda n:abs(value-channel[n]))for value in range(256))for channel in levels]
    return bytes(tables[n%3][value]for n,value in enumerate(image.tobytes()))


def main():
    base=ROOT/'validation/opening-return-v0315'
    project=base/'candidate06'
    digest=sha((project/'out/release/rom.bin').read_bytes())
    sy=symbols(project/'out/release/symbol.txt')
    cases=[]
    for region in ('pal','ntsc'):
      for late in (False,True):
        folder=base/('candidate06-'+region+('-late' if late else ''))
        probe=json.loads((folder/'report.json').read_bytes())
        assert probe['natural_input_only'] and probe['results']['md']['rom_sha256']==digest
        ready=probe['results']['sms']['first_hero_ready']
        assert ready==probe['results']['md']['first_hero_ready']
        rows={tag:{r['frame']:r for r in json.loads((folder/tag/'observations.json').read_bytes())}for tag in ('sms','md')}
        for frame in range(ready-31,ready+1):
            assert rows['sms'][frame]['occupancy_hex']==rows['md'][frame]['occupancy_hex'],(region,late,frame)
        changes=[dict(frame=f,cells=rows['sms'][f]['nonblank_cells'])for f in range(ready-31,ready)if f==ready-31 or rows['sms'][f]['occupancy_hex']!=rows['sms'][f-1]['occupancy_hex']]
        assert len(changes)==16 and changes[-1]['cells']==768
        for tag in ('sms','md'):
            empty=(folder/tag/f'vram_{ready:05d}.bin').read_bytes()
            visible=(folder/tag/f'vram_{ready+1:05d}.bin').read_bytes()
            if tag=='sms':assert empty[0x3f00]==208 and visible[0x3f00]!=208
            else:assert int.from_bytes(empty[0xf400:0xf402],'little')==128 and int.from_bytes(visible[0xf400:0xf402],'little')>128
        ack=2480 if late else 2400
        for frame in range(ack,ack+19):
            assert indexed_pixels(folder/'sms'/f'frame_{frame:05d}.png','sms')==indexed_pixels(folder/'md'/f'frame_{frame:05d}.png','md'),(region,late,'closing',frame)
        # Music phase remains a separately quantified limitation; never label
        # a subset of matching frames as complete source audio equivalence.
        start=ready-52
        channels=[];tempo=[]
        for frame in range(start,ready+33):
            src=(folder/'sms'/f'ram_{frame:05d}.bin').read_bytes()[0x1e00:0x1f00]
            raw=(folder/'md'/f'ram_{frame:05d}.bin').read_bytes()
            dst=bytes(raw[(sy['sound_ram']+i)^1]for i in range(256))
            if src[64:256]!=dst[64:256]:channels.append(frame)
            if src[1:5]!=dst[1:5]:tempo.append(frame)
        cases.append(dict(region=region,last_ack=ack,hero_ready_frame=ready,first_hardware_hero_frame=ready+1,
                          contours=changes,occupancy_frames_exact=32,closing_normalized_frames_exact=19,
                          audio_compared_frames=85,audio_channel_mismatch_frames=channels,audio_tempo_mismatch_frames=tempo,
                          observations_sha256=sha((folder/'report.json').read_bytes())))
    regressions=[]
    for region in ('pal','ntsc'):
        boot=base/'candidate06-tests/validation'/('boot-md-'+region)
        prior=ROOT/'validation/merchant-panel-v0314/candidate03-services/validation'/('boot-md-'+region)
        for name in ('audio_channels.bin','audio_tempo.bin','audio_psg.bin'):
            assert (boot/name).read_bytes()==evidence(prior/name),(region,name)
        now=json.loads((boot/'observations.json').read_bytes());old=json.loads(evidence(prior/'observations.json'))
        assert now['rom_sha256']==digest and now['maps']==old['maps']
        frames=([20,62,5952,6031]if region=='pal'else[23,69,5959,6045])
        for frame in frames:assert (boot/f'frame_{frame:05d}.png').read_bytes()==evidence(prior/f'frame_{frame:05d}.png')
        save=base/'candidate06-tests/validation/save-compatibility'/('opening06-settled-'+region)/'report.json'
        saved=json.loads(save.read_bytes());assert saved['passed'] and saved['md_sha256']==digest
        assert saved['source_crystal_markers_exact']==9 and saved['movement_frame']>saved['ready_frame']
        regressions.append(dict(region=region,boot_frames=6500,boot_audio_streams_exact=3,boot_title_pngs_exact=4,
                                save_report_sha256=sha(save.read_bytes()),save_ready=saved['ready_frame'],save_movement=saved['movement_frame']))
    inventory=base/'candidate06-tests/validation/inventory_restore_report.json'
    inv=json.loads(inventory.read_bytes());assert inv['md_sha256']==digest and len(inv['cases'])==6
    for case in inv['cases']:
        assert case['inventory_open_and_closed']
        assert all(not values for values in case['static_background_pattern_difference_indices'].values())
    diagnosis=base/'input-diagnosis06';a=json.loads((diagnosis/'candidate06-original/observations.json').read_bytes());b=json.loads((diagnosis/'sms-original/observations.json').read_bytes())
    fields=('room','game','hero','x','y')
    compared=[(x,y)for x,y in zip(a,b)if x['frame']>=2507]
    assert len(compared)==894 and all(all(x[k]==y[k]for k in fields)for x,y in compared)
    campaign=base/'campaign-comparison06/report.json';bad=json.loads(campaign.read_bytes());assert not bad['passed']
    result=dict(passed=True,md_sha256=digest,public_md_sha256=sha((ROOT/'versions/v0315-004b593b/gaw-megadrive-v0315.bin').read_bytes()),
                candidate_promoted=False,changed_native_sources=['main.c'],main_source_sha256=sha((project/'src/main.c').read_bytes()),
                natural_cases=cases,regressions=regressions,inventory_cases=6,inventory_report_sha256=sha(inventory.read_bytes()),
                natural_first_route_source_frames_exact=len(compared),natural_route_fields=list(fields),
                old_campaign_replay_passed=False,old_campaign_report_sha256=sha(campaign.read_bytes()),
                complete_campaign_on_this_binary=False,driver_sha256=sha(Path(__file__).read_bytes()),
                limits=['Restores omitted 11B7->0B48 story closing and 1FA7/2003 first-room reveal.',
                        'The former campaign input begins at2501 before source/candidate readiness2507 in NTSC; its divergence does not validate or invalidate later bosses. A fresh complete campaign remains required.',
                        'NTSC music tempo already has a two-tick phase difference before the story; the new theme starts during the reveal, but complete audio equality is not claimed.',
                        'Partial raster publication differs during some contour frames. Occupancy, closing images and hero appearance are distinct measured checks.',
                        'Source refresh/RNG stream, global IRQ clock, other scenes and physical hardware are not proved by these checks.'])
    target=ROOT/'analysis/initial_world_candidate06_v0315_report.json'
    assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n')
    print('Initial room: four natural cases, 16 contours each, eight boot captures, six inventories, two real-save continuations; remaining limits recorded.',flush=True)


if __name__=='__main__':main()
