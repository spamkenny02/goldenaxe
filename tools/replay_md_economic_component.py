"""Independent native99-key currency-component replay, actual A/V and strict write audit."""
import argparse,contextlib,hashlib,io,json,shutil
from run_core import ROOT,run,FrameWrites
from assisted_prefix import prefix_writes
from validate_playable_sprite_limit import symbols
from md_stream_video import Movie,sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',required=True);p.add_argument('--trace',required=True);p.add_argument('--from-frame',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args();source=ROOT/'validation'/a.trace;r=json.loads((source/'report.json').read_bytes());cap=json.loads((source/'capture.json').read_bytes());assert r['passed'] and r['currency_assisted_component_test'] and cap['currency_assisted_component_test'] and cap['sram_input'] is None
 assert r['sms_reference']=='natural-service-route/sms-npc-key-capacity99-01' and len(r['choices'])==99 and r['choices'][-1]['expect']=='full'
 rom=ROOT/a.rom;assert sha(rom)==cap['rom_sha256'];sy=symbols(ROOT/'megadrive/out/release/symbol.txt');aid=json.loads((source/'controlled_economic_assistance.json').read_bytes());parent=ROOT/'validation'/aid['source_prefix'];pc=json.loads((parent/'capture.json').read_bytes());old=list(prefix_writes(parent,pc,True));writes=[(e['frame'],e['address'],bytes.fromhex(e['data_hex'])) for e in aid['writes']]
 assert writes[:len(old)]==old;extra=writes[len(old):];assert len(extra)==99 and all(f>pc['frames'] and at==sy['hero_gold'] and data==b'\0\xff' for f,at,data in extra)
 assert aid['inventory_actor_health_and_quest_writes']==0 and cap['test_ram_writes']==[dict(frame=f,address=at,byte_count=len(data)) for f,at,data in writes]
 end=cap['frames'];presses=list(map(tuple,cap['presses']));controls=json.loads((source/'controls.json').read_bytes())
 for n,row in enumerate(controls):
  last=controls[n+1]['frame']-1 if n+1<len(controls) else end;presses.extend((row['frame'],min(last,end),k) for k in row['buttons'])
 out=source.with_name(source.name+'-economic-fixed-replay');assert not out.exists();core=ROOT.parents[1]/'work/libretro/genesis_plus_gx_libretro.dll';core_sha=sha(core);assert core_sha=='d17f2392115b3cd54258a1fa6c4195ddadc19b0805ebcca400db5162b1793516';movie=Movie(a.trace,cap,a.from_frame,core_sha);observed=0
 def observe(frame,raw):
  nonlocal observed
  observed=frame;word=lambda n:raw[sy[n]]|raw[sy[n]+1]<<8;assert not word('sound_unhandled_command')
  if word('hero_hurt')>128:
   for n in range(16):
    at=sy['world_actor_state']+48*n;kind=raw[at^1];hp=raw[(at+24)^1];assert not hp or not (0x63<=kind<=0x6d or 0x78<=kind<=0x7c)
 with contextlib.redirect_stdout(io.StringIO()):run(rom,end,out,{end},presses,skip_intro=False,ram_writes=FrameWrites(writes),ram_observer=observe,core_options=cap['core_options'],video_observer=movie.video,audio_observer=lambda data:movie.sound(observed+1,data))
 for stem,ext in [('ram','bin'),('frame','png')]:assert (out/f'{stem}_{end:05d}.{ext}').read_bytes()==(source/f'{stem}_{end:05d}.{ext}').read_bytes()
 raw=(out/f'ram_{end:05d}.bin').read_bytes();assert (raw[sy['hero_keys']]|raw[sy['hero_keys']+1]<<8)==99
 proof=out/'replay_report.json';w=dict(passed=True,rom_sha256=cap['rom_sha256'],frames=end,whole_ram_bytes=65536,whole_ram_exact=True,final_png_exact=True,feedback_reads=False,primary_state_imports=0,sram_imports=0,inventory_actor_health_and_quest_writes=0,currency_assisted_component_test=True,currency_refills=len(extra),natural_campaign_proof=False,evidence={n:sha(source/n) for n in ('capture.json','controls.json','controlled_economic_assistance.json')},scope='Separate explicitly labelled currency-only component. All98 keys are bought through the actual native merchant and the99-key full refusal is observed. No inventory, actor, HP or quest writes.')
 proof.write_bytes((json.dumps(w,indent=2)+'\n').encode());movie.finish(proof,writes);cache=movie.folder/'report.json';video=json.loads(cache.read_bytes());dest=ROOT/'videos/md-annexes-2026-11-12'/a.name;dest.mkdir(exist_ok=False,parents=True);target=dest/(a.name+'.mp4');shutil.copyfile(movie.movie,target);assert sha(target)==video['movie_sha256'];video.update(movie=target.relative_to(ROOT).as_posix(),currency_refills=len(extra),inventory_actor_health_and_quest_writes=0);encoded=(json.dumps(video,indent=2)+'\n').encode();(dest/'report.json').write_bytes(encoded);cache.write_bytes(encoded);movie.movie.unlink();print(json.dumps(video),flush=True)

if __name__=='__main__':main()
