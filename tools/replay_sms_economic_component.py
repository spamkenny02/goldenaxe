"""Independent fixed replay of an explicitly isolated currency-assisted test."""
import argparse,hashlib,json
from PIL import Image
from run_core import ROOT,run,FrameWrites
from assisted_prefix import prefix_writes


def main():
    p=argparse.ArgumentParser();p.add_argument('--trace',required=True);a=p.parse_args()
    folder=(ROOT/'validation'/a.trace).resolve();assert folder.is_relative_to(ROOT/'validation')
    report=json.loads((folder/'report.json').read_bytes());assert report['passed'] and report['currency_assisted_component_test']
    cap=json.loads((folder/'capture.json').read_bytes());assert cap['sram_input'] is None
    aid=json.loads((folder/'controlled_economic_assistance.json').read_bytes())
    source=ROOT/'validation'/aid['source_prefix'];initial=json.loads((source/'capture.json').read_bytes())
    old=list(prefix_writes(source,initial,True));writes=[(r['frame'],r['address'],bytes.fromhex(r['data_hex'])) for r in aid['writes']]
    assert writes[:len(old)]==old
    extra=writes[len(old):];assert extra and all(f>initial['frames'] and
        (addr==0xdd and data==b'\xff' or addr==0x305 and data==b'\x81') for f,addr,data in extra)
    assert cap['test_ram_writes']==[dict(frame=f,address=addr,byte_count=len(data)) for f,addr,data in writes]
    end=cap['frames'];presses=list(map(tuple,cap['presses']));controls=json.loads((folder/'controls.json').read_bytes())
    for i,row in enumerate(controls):
        last=controls[i+1]['frame']-1 if i+1<len(controls) else end
        presses.extend((row['frame'],min(last,end),k) for k in row['buttons'] if row['frame']<=end)
    out=folder.with_name(folder.name+'-economic-fixed-replay');assert not out.exists()
    def observe(frame,raw):
        if raw[0x305]>128:
            assert not any(raw[0x618+n*48] and (0x63<=raw[0x600+n*48]<=0x6d or 0x78<=raw[0x600+n*48]<=0x7c) for n in range(16)), 'Approach aid overlaps a live boss'
    run(ROOT/'input/original.sms',end,out,{end},presses,skip_intro=False,ram_writes=FrameWrites(writes),core_options=cap['core_options'],ram_observer=observe)
    raw=(out/f'ram_{end:05d}.bin').read_bytes();expected=(folder/f'ram_{end:05d}.bin').read_bytes();assert raw==expected
    pixels=lambda p:Image.open(p).convert('RGB').tobytes()
    assert pixels(out/f'frame_{end:05d}.png')==pixels(folder/f'frame_{end:05d}.png')
    proof=dict(passed=True,trace=a.trace,frames=end,whole_ram_bytes=len(raw),whole_ram_exact=True,final_pixels_exact=True,
        final_keys=raw[0xde],currency_refills=sum(addr==0xdd for _,addr,_ in extra),inventory_actor_health_and_quest_writes=0,
        currency_assisted_component_test=True,natural_campaign_proof=False,sram_imports=0,
        final_ram_sha256=hashlib.sha256(raw).hexdigest(),
        evidence={n:hashlib.sha256((folder/n).read_bytes()).hexdigest() for n in ('capture.json','controls.json','controlled_economic_assistance.json')})
    (out/'replay_report.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof),flush=True)


if __name__=='__main__':main()
