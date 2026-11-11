"""Evidence-bound status of the user's six open SMS completion tasks."""
import json,hashlib
from run_core import ROOT


def read(name):
    path=ROOT/'analysis'/name
    return json.loads(path.read_bytes()) if path.exists() else None


def verified(trace):
    folder=ROOT/'validation'/trace
    report=json.loads((folder/'report.json').read_bytes())
    cap=json.loads((folder/'capture.json').read_bytes())
    proof=folder.with_name(folder.name+f'-assisted-fixed-replay-{cap["frames"]}')/'replay_report.json'
    assert report['passed'] and not report['failure'] and json.loads(proof.read_bytes())['passed']
    raw=(folder/f'ram_{cap["frames"]:05d}.bin').read_bytes()
    return dict(trace=trace,frame=cap['frames'],proof=proof.relative_to(ROOT).as_posix(),
        ram_sha256=hashlib.sha256(raw).hexdigest(),health_capacity=raw[0xda],magic_capacity=raw[0xdc],
        magic_levels=list(raw[0xe4:0xe8]))


def main():
    census=read('sms_plain_house_census_campaign.json')
    o3=next((h for h in census['completed_houses'] if h['outside']==0x3e and h['room']==0x8f),None)
    point1=dict(status='complete' if o3 else 'pending',scope='O3 ordinary context, not all NPC/service branches')
    if o3:point1['evidence']=verified(o3['trace'])
    magic=read('sms_remaining_magic_campaign.json');fairies=read('sms_fairy_census_campaign.json')
    point2=dict(status='in_progress',teachers=None,fairies=None)
    if magic and magic.get('completed_visits'):
        point2['teachers']=verified(magic['completed_visits'][-1]['trace'])
    if fairies and fairies.get('completed_rewards'):
        point2['fairies']=verified(fairies['completed_rewards'][-1]['trace'])
        end=point2['fairies']
        if fairies['status']=='all_eight_fairy_rewards_present_and_selected_new_rewards_replayed' and end['health_capacity']==end['magic_capacity']==128 and end['magic_levels']==[2,2,2,1]:point2['status']='complete_acquisitions_revisits_separate'
    service=read('sms_service_refusal_campaign.json')
    point3=dict(status='in_progress',refusal_tour=service,
        save_slots=read('sms_actual_save_slots_report.json'),
        limits='Refusal entries do not close successful purchases, paid nights, saves, passages, gambling or return variants.')
    shield=read('sms_dragon_shield_campaign.json')
    point4=dict(status='in_progress',complete=False,equipment_hint_branches=read('sms_equipment_hint_branches.json'))
    if shield and shield.get('passed'):point4['dragon_shield']=verified(shield['last_verified_prefix'])
    points={
        '1_o3':point1,'2_teachers_and_capacity':point2,'3_services':point3,
        '4_equipment_hints_hidden_rooms_curse':point4,
        '5_reported_strings':dict(status='unresolved',offsets=['0xDA58','0xDA7C','0xED3C'],unused_proven=False),
        '6_final_replay_and_video':dict(status='pending_final_route',complete_100_percent_video=False)}
    report=dict(date='2026-11-11',source_sha256=hashlib.sha256((ROOT/'input/original.sms').read_bytes()).hexdigest(),
        all_npcs_complete=False,all_side_quests_complete=False,points=points)
    (ROOT/'analysis/sms_six_points_progress.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v['status'] for k,v in points.items()}))


if __name__=='__main__':main()
