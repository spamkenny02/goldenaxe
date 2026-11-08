"""Write real c0047 SRAM using recorded ordinary input, then Continue from that exact SRAM."""
import contextlib,io,json,sys
from pathlib import Path
sys.path.insert(0,'tools')
from run_core import ROOT,FrameWrites,run
from assisted_prefix import recording
from archive_lossless_evidence import freeze,sha
from validate_playable_sprite_limit import symbols
from validate_reward_hud_restore import translated
project=ROOT/'validation/c0046-campaign01/isolated/project';work=ROOT/'validation/c0047-pal-real-save01';assert not work.exists()
reference=ROOT/'analysis/game_written_save_pal_c0046_nine_crystals_report.json';r=json.loads(reference.read_bytes())
assert r['passed'] and r['candidate']=='c0046' and r['md_sha256']=='9e747d38e0c6fb2d69b7c1aa8c2b296a61e8b6af41171d14e543ed9a6cb49cf5'
assert r['game_written_save'] and not r['synthetic_sram_fixture'] and r['raw_sram_fixed_replay_exact'] and r['save_whole_ram_png_exact'] and r['source_crystal_markers_exact']==9
source=(project/'validation'/r['source_trace']).resolve();assert source.is_relative_to(project/'validation')
cap=json.loads((source/'capture.json').read_bytes());service=json.loads((source/'report.json').read_bytes());assist,writes=recording(source,cap)
assert cap['core_options']['genesis_plus_gx_region_detect']=='pal' and cap['sram_input'] is None and service['passed'] and service['game_written_save'] and service['payload_source_ram_exact'] and not service['primary_state_imports'] and not service['new_assistance_writes']
expected_sram=(project/service['sram_file']).resolve();assert expected_sram.is_relative_to(source) and sha(expected_sram.read_bytes())==r['source_sram_sha256']
def presses(c,folder):
    controls=json.loads((folder/'controls.json').read_bytes());result=[tuple(p) for p in c['presses']];end=c['frames']
    for i,row in enumerate(controls):
        stop=controls[i+1]['frame']-1 if i+1<len(controls) else end
        result.extend((row['frame'],min(stop,end),b) for b in row['buttons'] if row['frame']<=end)
    return result
rom=ROOT/'versions/candidates/c0047-d3ea2a83/gaw-megadrive-c0047.bin';assert sha(rom.read_bytes())=='d3ea2a83ea24ed8a0d3c9857f9fbe70d000a4f73358452c1887f40e78966c56e'
writer=work/'write';sram=writer/'game-written.srm';end=cap['frames']
with contextlib.redirect_stdout(io.StringIO()):run(rom,end,writer,{end},presses(cap,source),skip_intro=False,ram_writes=FrameWrites(writes),sram_out=sram,core_options=cap['core_options'])
assert sram.read_bytes()==expected_sram.read_bytes()
for stem,ext in [('ram','bin'),('frame','png')]:assert (writer/f'{stem}_{end:05d}.{ext}').read_bytes()==(source/f'{stem}_{end:05d}.{ext}').read_bytes()
print('Actual c0047 game-written SRAM, writer whole RAM and image match the verified c0046 branch',flush=True)
reload_source=(project/r['reload_trace']).resolve();assert reload_source.is_relative_to(project/'validation')
rc=json.loads((reload_source/'capture.json').read_bytes());assert not rc['test_ram_writes'] and rc['sram_input'] and rc['core_options']==cap['core_options']
loader=work/'continue';last=rc['frames']
with contextlib.redirect_stdout(io.StringIO()):run(rom,last,loader,{last},presses(rc,reload_source),skip_intro=False,sram_in=sram,core_options=rc['core_options'])
for stem,ext in [('ram','bin'),('frame','png')]:assert (loader/f'{stem}_{last:05d}.{ext}').read_bytes()==(reload_source/f'{stem}_{last:05d}.{ext}').read_bytes()
lc=json.loads((loader/'capture.json').read_bytes());assert not lc['test_ram_writes'] and Path(lc['sram_input']).resolve()==sram.resolve()
sy=symbols(rom.with_name('symbol.txt'));raw=(loader/f'ram_{last:05d}.bin').read_bytes();data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
assert word('game_state')==12 and word('room_id')==r['checkpoint_room'] and word('hero_health')==r['last_state']['health'] and word('hero_max_health')==104 and word('hero_hurt')<=128 and not word('sound_unhandled_command')
payload=(source/'serialized-payload.bin').read_bytes();assert len(payload)==592
for name,offset in r['restored_source_fields'].items():assert word(name)==payload[offset]
assert data('hero_items',17)==payload[0x30:0x41] and data('game_save_state',592)[0x1f:0x28]==bytes([128]*9)
sms=data('sms_vram',16384);vram=(loader/f'vram_{last:05d}.bin').read_bytes();regs=(loader/f'vdp_regs_{last:05d}.bin').read_bytes();base=(regs[2]&56)<<10;width=[32,64,32,128][regs[16]&3]
for n in range(128):
    at=base+((n//32+22)*width+n%32)*2;assert int.from_bytes(vram[at:at+2],'little')==translated(int.from_bytes(sms[0x3d00+n*2:0x3d02+n*2],'little'))
result=dict(passed=True,candidate='c0047',region='pal',rom_sha256=sha(rom.read_bytes()),game_written_save=True,synthetic_sram_fixture=False,
            writer_initial_sram=False,writer_primary_state_imports=0,writer_whole_ram_bytes_exact=65536,writer_final_png_exact=True,writer_frames=end,
            raw_sram_exact_to_c0046=True,sram_sha256=sha(sram.read_bytes()),reload_from_own_game_written_sram=True,reload_primary_sram_imports=1,reload_ram_writes=0,
            reload_frames=last,reload_whole_ram_bytes_exact=65536,reload_final_png_exact=True,source_crystal_markers_exact=9,physical_hud_words_exact=128,
            source_reference=reference.relative_to(ROOT).as_posix(),archive_manifest='analysis/c0047-pal-real-save/manifest.json',
            scope='Actual PAL c0047 slot0 SRAM write from a separate cold nine-crystal controller branch, then normal Continue and movement from that exact c0047-generated SRAM. Both complete RAM and final image match the verified c0046 branch, no stack normalization. Reload is a normal SRAM import, not a cold New Game campaign; not all slots/refusals or source/hardware fidelity.')
paths=[Path(__file__).resolve(),reference,expected_sram,source/'capture.json',source/'report.json',source/'controls.json',source/'assistance.json',source/'serialized-payload.bin',reload_source/'capture.json',reload_source/'controls.json',reload_source/'report.json']
paths += [source/f'{stem}_{end:05d}.{ext}' for stem,ext in [('ram','bin'),('frame','png')]]+[reload_source/f'{stem}_{last:05d}.{ext}' for stem,ext in [('ram','bin'),('frame','png')]]
paths += [p for p in work.rglob('*') if p.is_file()]
freeze(ROOT,ROOT/'analysis/c0047-pal-real-save',paths,result,[work],cleanup=True)
(ROOT/'analysis/c0047_pal_real_save_report.json').write_text(json.dumps(result,indent=2)+'\n')
print('c0047 real SRAM write and normal Continue verified on complete RAM/image',flush=True)
