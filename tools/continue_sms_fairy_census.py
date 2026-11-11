"""Collect the remaining life/magic fairy rewards on the current SMS branch."""
import argparse,json
from run_core import ROOT
from sms_campaign_runner import Campaign
from continue_sms_plain_house_census import census_world
from continue_sms_npc_d4 import ROUTE
from extract_title import rle_planes


def main():
    p=argparse.ArgumentParser();p.add_argument('--prefix',required=True);a=p.parse_args()
    output=ROOT/'analysis/sms_fairy_census_campaign.json'
    saved=json.loads(output.read_bytes()) if output.exists() else {}
    completed=saved.get('completed_rewards',[])
    prefix=completed[-1]['trace'] if completed else a.prefix
    c=Campaign(prefix,0x15e,'npc-fairies')
    cases=json.loads((ROOT/'analysis/full_completion_checklist.json').read_bytes())['cases']
    targets=[x['context'] for x in cases if x['category']=='fairy']
    pending=[];prior=[]
    def save(status):
        output.write_text(json.dumps(dict(status=status,all_npcs_complete=False,all_side_quests_complete=False,
            initial_prefix=a.prefix,last_verified_prefix=c.family+'/'+c.current,
            completed_rewards=completed,previously_collected=prior,pending=pending),indent=2)+'\n')
    try:
        c.verify(lambda r:r['passed']);initial=c.raw()
        assert all(initial[i] for i in (0xe4,0xe5,0xe6,0xe7)), 'Learn all four magics before the remaining magic fairies; the original capacity rule depends on acquisition order'
        for target in targets:
            if initial[0x100+target['outside']]&2:prior.append(target)
            else:pending.append(target)
        while pending:
            raw=c.raw();start=(int.from_bytes(raw[0xb9:0xbb],'little'),raw[0x313],raw[0x311])
            ordered=sorted(pending,key=lambda t:(0 if raw[0xdb]<16 and t['kind']==255 else 1,
                abs((t['outside']&15)-(start[0]&15))+abs((t['outside']>>4)-(start[0]>>4))))
            chosen=None
            for target in ordered:
                w=None
                for direction in range(4):
                    candidate=census_world(raw,target['outside'],0xaf,direction);path,_=candidate.route(start)
                    if path is not None:w=candidate;break
                if w is None:continue
                m=w.arrays['world_room_metadata'];node=next((m[i:i+4] for i in range(0,len(m)-3,4) if m[i]==target['outside']),None)
                earth=None
                if node and not raw[0x100+target['outside']]&1:
                    cells=bytearray(160);pointer=int.from_bytes(w.arrays['world_room_index'][target['outside']*2:target['outside']*2+2],'little')
                    rle_planes(w.arrays['world_room_streams'],pointer,cells,0,1)
                    if cells[node[1]] in (0x13,0x38,0x3d,0x85,0x86):earth=node[1]
                if earth is not None and raw[0xdb]<8:continue
                chosen=target,earth,direction;break
            if chosen is None:save('needs_transport_or_magic_replenishment');return
            target,earth,direction=chosen;outside=target['outside'];attempt=1
            while (ROOT/'validation'/ROUTE/f'sms-sms-npc-fairies-{outside:02x}-entry{attempt:02d}').exists():attempt+=1
            extra=['--house-outside',hex(outside),'--house-target','0xaf','--persisted-only']
            extra+=['--door-entry-direction',str(direction)]
            if earth is not None:extra+=['--earth-world-cell',hex(earth)]
            c.route(f'{outside:02x}-entry{attempt:02d}',extra,tool='natural_earth_world_route.py' if earth is not None else 'natural_bell_world_route.py')
            kind='life' if target['kind']==1 else 'magic';before=c.raw();capacity=before[0xda if kind=='life' else 0xdc]
            c.service(f'{outside:02x}-reward{attempt:02d}','natural_fairy_service',
                ['--outside',hex(outside),'--kind',kind,'--expected-initial-capacity',str(capacity)])
            after=c.raw();assert after[0x100+outside]&2 and after[0xda if kind=='life' else 0xdc]==min(128,capacity+8)
            completed.append(dict(outside=outside,kind=kind,capacity_before=capacity,
                capacity_after=after[0xda if kind=='life' else 0xdc],trace=c.family+'/'+c.current,frame=c.cap()['frames']))
            pending.remove(target);save('running');print('FAIRY REWARD VERIFIED',hex(outside),kind,flush=True)
        final=c.raw();assert all(final[0x100+t['outside']]&2 for t in targets)
        assert final[0xda]==128 and final[0xdc]==128
        save('all_eight_fairy_rewards_present_and_selected_new_rewards_replayed')
    finally:c.close()


if __name__=='__main__':main()
