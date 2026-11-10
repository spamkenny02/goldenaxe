"""Append the actually completed SMS route to the existing portable test kit."""
import json,shutil
from PIL import Image
from run_core import ROOT,compile_fixed_inputs
from assisted_prefix import prefix_writes
from archive_lossless_evidence import sha


def main():
    summary=json.loads((ROOT/'analysis/sms_npc_campaign_progress_report.json').read_bytes())
    assert summary['passed'] and summary['full_campaign_complete'] and not summary['all_npcs_complete']
    source=ROOT/'validation'/summary['latest_selected_prefix']
    cap=json.loads((source/'capture.json').read_bytes());end=cap['frames']
    assert cap['rom_sha256']==sha((ROOT/'input/original.sms').read_bytes()) and cap['sram_input'] is None
    writes=prefix_writes(source,cap,True);assert all(addr==0x305 for _,addr,_ in writes)
    controls=json.loads((source/'controls.json').read_bytes());presses=list(map(tuple,cap['presses']))
    for i,row in enumerate(controls):
        stop=controls[i+1]['frame']-1 if i+1<len(controls) else end
        presses.extend((row['frame'],min(stop,end),key) for key in row['buttons'] if row['frame']<=end)
    masks=compile_fixed_inputs(presses,end);assert masks[0]==0
    guards={f:int.from_bytes(data,'big') for f,_,data in writes};rows=[];first=1;old=(masks[1],guards.get(1,-1))
    for frame in range(2,end+2):
        current=(masks[frame],guards.get(frame,-1)) if frame<=end else None
        if current!=old:rows.append((first,frame-1,*old));first=frame;old=current
    recovered=[0]*(end+1);recovered_writes=[]
    for first,last,mask,guard in rows:
        recovered[first:last+1]=[mask]*(last-first+1)
        if guard!=-1:recovered_writes.extend((f,guard) for f in range(first,last+1))
    assert recovered==masks and recovered_writes==[(f,int.from_bytes(data,'big')) for f,_,data in writes]
    kit=ROOT/'testkit';path=kit/'routes/sms_full_ntsc.csv'
    path.write_bytes(('start,end,mask,guard\n'+''.join(','.join(map(str,r))+'\n' for r in rows)).encode())
    references=kit/'references';references.mkdir(exist_ok=True)
    proof=source.with_name(source.name+f'-assisted-fixed-replay-{end}')
    for name,destination in [(f'ram_{end:05d}.bin','sms_full_ntsc_final_ram.bin'),
                             (f'frame_{end:05d}.png','sms_full_ntsc_final.png'),
                             ('replay_report.json','sms_full_ntsc_fixed_replay.json')]:
        shutil.copyfile(proof/name,references/destination)
    raw=(proof/f'ram_{end:05d}.bin').read_bytes();pr=json.loads((proof/'replay_report.json').read_bytes())
    manifest=json.loads((kit/'manifest.json').read_bytes())
    manifest['routes']['sms_full_ntsc']=dict(system='sms',region='ntsc',frames=end,csv=path.name,
        csv_sha256=sha(path.read_bytes()),rows=len(rows),approach_writes=len(writes),boss_assistance=False,
        save_imports=0,full_campaign=True,all_npcs_complete=False,bizhawk_runtime_validated=False,
        core_options=cap['core_options'],validated_core_sha256=pr['core_sha256'],
        historical_recording_rom_sha256=cap['rom_sha256'],
        source_files={n:sha((source/n).read_bytes()) for n in ('capture.json','controls.json','assistance.json')},
        expected_final=dict(game=raw[0x1d],room=int.from_bytes(raw[0xb9:0xbb],'little'),
                            health=raw[0x318],crystals=sum(bool(b&128) for b in raw[0xcf:0xd8])),
        expected_final_ram_sha256=sha(raw),expected_final_png_sha256=sha((proof/f'frame_{end:05d}.png').read_bytes()),
        expected_final_pixels_sha256=sha(Image.open(proof/f'frame_{end:05d}.png').convert('RGB').tobytes()),
        scope='Original supplied SMS ROM, nine crystals, Golden Axe, Death Adder, complete credits and return to intro. Partial NPC/side-quest coverage; NTSC libretro only.')
    (kit/'manifest.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode())
    print(json.dumps(dict(route='sms_full_ntsc',frames=end,rows=len(rows),writes=len(writes))))


if __name__=='__main__':main()
