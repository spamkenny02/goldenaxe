"""Fresh fixed-input source replay, with actual NPC text and render observation."""
import argparse,contextlib,hashlib,io,json
from PIL import Image
from run_core import ROOT,run,FrameWrites
from assisted_prefix import prefix_writes

dialogue_events=[]


def main():
    p=argparse.ArgumentParser();p.add_argument('--sms',action='store_true',required=True)
    p.add_argument('--trace',required=True);p.add_argument('--trial',required=True);a=p.parse_args()
    source=ROOT/'validation'/a.trace;cap=json.loads((source/'capture.json').read_bytes())
    primary=json.loads((source/'report.json').read_bytes());assert primary['passed'] and cap['sram_input'] is None
    prefix=ROOT/'validation/natural-dungeon-route'/primary['source_prefix']
    start=json.loads((prefix/'capture.json').read_bytes())['frames'];end=cap['frames']
    writes=prefix_writes(source,cap,True);presses=list(map(tuple,cap['presses']))
    rows=json.loads((source/'controls.json').read_bytes())
    for i,row in enumerate(rows):
        last=rows[i+1]['frame']-1 if i+1<len(rows) else end
        presses.extend((row['frame'],min(last,end),key) for key in row['buttons'] if row['frame']<=end)
    out=ROOT/'validation/sms-guide-fixed-dialogues'/a.trial;assert not out.exists()
    out.parent.mkdir(exist_ok=True);captures={end};entries=[];completed=[];cursor=0;active=None
    def observe(frame,raw):
        nonlocal cursor,active
        while cursor<len(dialogue_events):
            event=dialogue_events[cursor];cursor+=1
            if event['frame']<=start:continue
            if event['event_pc']==0x524 and event['outside']==0xa3 and event['room']==0xbf:
                active=dict(text_pc=event['text_pc'],entry_frame=event['frame'],earth_level=raw[0xe5],
                    gold=raw[0xdd],room=event['room'],outside=event['outside'],
                    caller=event['caller'],stack_pointer=event['stack_pointer'])
                entries.append(active);captures.add(frame+1)
            elif (event['event_pc']==0x6e3 and active is not None and
                  event['caller']==active['caller'] and event['stack_pointer']==active['stack_pointer']):
                completed.append(dict(**active,render_return_frame=event['frame'],capture_frame=frame+1))
                captures.add(frame+1);active=None
    with contextlib.redirect_stdout(io.StringIO()):
        run(ROOT/'input/original.sms',end,out,captures,presses,skip_intro=False,ram_writes=FrameWrites(writes),
            ram_observer=observe,core_options=cap['core_options'])
    assert (out/f'ram_{end:05d}.bin').read_bytes()==(source/f'ram_{end:05d}.bin').read_bytes()
    pixels=lambda p:Image.open(p).convert('RGB').tobytes()
    assert pixels(out/f'frame_{end:05d}.png')==pixels(source/f'frame_{end:05d}.png')
    assert entries and len(completed)==len(entries)
    result=dict(passed=True,source_trace=a.trace,stage_start=start,frames=end,actual_entries=entries,
        completed_renderings=completed,whole_ram_bytes=8192,whole_ram_exact=True,final_pixels_exact=True,
        source_sha256=cap['rom_sha256'],new_primary_writes=0,primary_state_imports=0,
        source_evidence={name:hashlib.sha256((source/name).read_bytes()).hexdigest() for name in ('capture.json','controls.json','assistance.json')},
        scope='Original SMS cold boot, fixed ordinary recorded inputs, inherited approach protection; read-only observer. Actual Battler messages rendered; no whitelist of expected text IDs.')
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)


if __name__=='__main__':main()
