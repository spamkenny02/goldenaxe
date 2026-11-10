"""Verify the selected cold-boot NPC campaign beyond the second crystal."""
import hashlib
import json
from run_core import ROOT


def read(path):return json.loads(path.read_bytes())


def main():
    chain=[
        ('natural-dungeon-route/sms-sms-npc-d2-fairy-entry01','entry'),
        ('natural-dungeon-combat/sms-auto-sms-npc-d2-fairy-boss07','partial_combat'),
        ('natural-dungeon-combat/sms-auto-sms-npc-d2-fairy-boss08','boss_defeated_reward_pending'),
        ('natural-dungeon-combat/sms-auto-sms-npc-d2-reward01','crystal_reward_finished'),
        ('natural-dungeon-combat/sms-auto-sms-npc-d2-exit02','partial_exit'),
        ('natural-dungeon-combat/sms-auto-sms-npc-d2-exit03','dungeon_exit'),
        ('natural-dungeon-route/sms-sms-npc-gold-f4-entry01','entry'),
        ('natural-service-route/sms-npc-gold-f4-gift01','gold_gift'),
        ('natural-dungeon-route/sms-sms-npc-key-shop-c7-entry01','entry'),
        ('natural-service-route/sms-npc-key-c7-buy01','key_purchase'),
        ('natural-dungeon-route/sms-sms-npc-d3-entry02','entry'),
        ('natural-dungeon-combat/sms-auto-sms-npc-d3-rope02','rope'),
        ('natural-dungeon-combat/sms-auto-sms-npc-d3-switch01','mechanism'),
        ('natural-dungeon-combat/sms-auto-sms-npc-d3-key01','dungeon_key'),
        ('natural-dungeon-combat/sms-auto-sms-npc-d3-pre-boss01','entry_combat'),
        ('natural-dungeon-combat/sms-auto-sms-npc-d3-boss01','third_crystal'),
        ('natural-dungeon-combat/sms-auto-sms-npc-d3-exit01','partial_exit'),
        ('natural-dungeon-combat/sms-auto-sms-npc-d3-exit02','third_dungeon_exit'),
        ('natural-dungeon-route/sms-sms-npc-gold-b4-entry01','entry'),
        ('natural-service-route/sms-npc-gold-b4-gift01','gold_gift'),
        ('natural-dungeon-route/sms-sms-npc-earth-entry01','entry'),
        ('natural-service-route/sms-npc-earth-learn01','earth_teacher'),
        ('natural-dungeon-route/sms-sms-npc-d4-entry01','entry'),
        ('natural-dungeon-combat/sms-auto-sms-npc-d4-key01','dungeon_key'),
        ('natural-dungeon-combat/sms-auto-sms-npc-d4-earth01','earth_passage'),
        ('natural-dungeon-combat/sms-auto-sms-npc-d4-a1-key02','dungeon_key'),
        ('natural-dungeon-combat/sms-auto-sms-npc-d4-canoe01','canoe'),
        ('natural-dungeon-combat/sms-auto-sms-npc-d4-warp01','earth_passage'),
        ('natural-dungeon-combat/sms-auto-sms-npc-d4-boss-key01','dungeon_key'),
        ('natural-dungeon-combat/sms-auto-sms-npc-d4-pre-boss01','reach_room'),
        ('natural-dungeon-combat/sms-auto-sms-npc-d4-boss01','partial_combat'),
        ('natural-dungeon-combat/sms-auto-sms-npc-d4-boss02','fourth_crystal'),
        ('natural-dungeon-combat/sms-auto-sms-npc-d4-exit03','fourth_dungeon_exit'),
        ('natural-dungeon-route/sms-sms-npc-equipment-27-entry03','entry'),
        ('natural-service-route/sms-npc-equipment-27-gift01','armor2'),
        ('natural-dungeon-route/sms-sms-npc-equipment-50-entry01','entry'),
        ('natural-service-route/sms-npc-equipment-50-gift01','long_sword'),
        ('natural-dungeon-route/sms-sms-npc-d5-entry01','entry'),
        ('natural-dungeon-combat/sms-auto-sms-npc-d5-key01','dungeon_key'),
        ('natural-dungeon-combat/sms-auto-sms-npc-d5-earth01','earth_passage'),
        ('natural-dungeon-combat/sms-auto-sms-npc-d5-boots01','boots'),
        ('natural-dungeon-combat/sms-auto-sms-npc-d5-supply-exit01','supply_exit'),
        ('natural-dungeon-route/sms-sms-npc-d5-golda1-entry01','entry'),
        ('natural-service-route/sms-npc-gold-a1-gift01','gold_gift'),
        ('natural-dungeon-route/sms-sms-npc-d5-merchant94-entry01','entry'),
        ('natural-service-route/sms-npc-key94-buy01','key_purchase'),
        ('natural-dungeon-route/sms-sms-npc-d5-healer94-entry01','entry'),
        ('natural-service-route/sms-npc-healer94-rest01','free_rest'),
        ('natural-dungeon-route/sms-sms-npc-d5-return-entry02','entry'),
        ('natural-dungeon-combat/sms-auto-sms-npc-d5-warp02','earth_passage'),
        ('natural-dungeon-combat/sms-auto-sms-npc-d5-contact02','contact_passage'),
        ('natural-dungeon-combat/sms-auto-sms-npc-d5-approach01','entry_combat'),
        ('natural-dungeon-combat/sms-auto-sms-npc-d5-boss01','fifth_crystal'),
        ('natural-dungeon-combat/sms-auto-sms-npc-d5-return-contact01','contact_passage'),
        ('natural-dungeon-combat/sms-auto-sms-npc-d5-exit01','fifth_dungeon_exit'),
        ('natural-service-route/sms-npc-d6-equipaxe01','weapon_selection'),
        ('natural-dungeon-route/sms-sms-npc-d6-gold7d-entry02','entry'),
        ('natural-service-route/sms-npc-d6-gold7d-gift01','gold_gift'),
        ('natural-dungeon-route/sms-sms-npc-d6-golde7-entry01','entry'),
        ('natural-service-route/sms-npc-d6-golde7-gift01','gold_gift'),
        ('natural-dungeon-route/sms-sms-npc-d6-gillian2-entry01','entry'),
        ('natural-service-route/sms-npc-d6-gillian2-learn01','gillian_upgrade'),
        ('natural-dungeon-route/sms-sms-npc-d6-battler2-entry01','entry'),
        ('natural-service-route/sms-npc-d6-battler2-learn01','battler_upgrade'),
        ('natural-dungeon-route/sms-sms-npc-d6-entry01','entry'),
    ]
    kinds=['entry_combat','dungeon_key','earth_passage','dungeon_key','contact_passage',
           'dungeon_key','contact_passage','dungeon_key','earth_passage','earth_passage',
           'earth_passage','earth_passage','dungeon_key','ice_bell','earth_passage']
    chain.extend((f'natural-dungeon-combat/sms-auto-sms-npc-d6-stage{i:02d}-01',kind)
                 for i,kind in enumerate(kinds,1))
    chain.extend([('natural-dungeon-combat/sms-auto-sms-npc-d6-boss02','sixth_crystal'),
                  ('natural-dungeon-combat/sms-auto-sms-npc-d6-exit02','sixth_dungeon_exit')])
    chain.extend([
        ('natural-dungeon-route/sms-sms-npc-d7-goldac-entry01','entry'),
        ('natural-service-route/sms-npc-d7-goldac-gift01','gold_gift'),
        ('natural-dungeon-route/sms-sms-npc-d7-key94-entry01','entry'),
        ('natural-service-route/sms-npc-d7-key94-buy01','key_purchase'),
        ('natural-dungeon-route/sms-sms-npc-d7-healer94-entry01','entry'),
        ('natural-service-route/sms-npc-d7-healer94-rest01','free_rest'),
        ('natural-dungeon-route/sms-sms-npc-d7-entry01','entry'),
    ])
    d7=[('key01','dungeon_key'),('key03','dungeon_key'),('earth01','earth_passage'),
        ('earth02','earth_passage'),('contact01','contact_passage'),('midboss01','intermediate_victory'),
        ('resume02','intermediate_resume'),('south01','entry_combat'),('remote01','contact_passage'),
        ('ship01','ship'),('north01','entry_combat'),('warp01','earth_passage'),
        ('approach01','entry_combat'),('boss01','seventh_crystal'),('return-earth01','earth_passage'),
        ('exit01','seventh_dungeon_exit')]
    chain.extend(('natural-dungeon-combat/sms-auto-sms-npc-d7-'+suffix,kind) for suffix,kind in d7)
    chain.extend([
        ('natural-dungeon-route/sms-sms-npc-d8-dragonmail-entry01','entry'),
        ('natural-service-route/sms-npc-d8-dragonmail-gift01','armor3'),
        ('natural-dungeon-route/sms-sms-npc-d8-flamesword-entry01','entry'),
        ('natural-service-route/sms-npc-d8-flamesword-gift01','flame_sword'),
        ('natural-dungeon-route/sms-sms-npc-d8-healer94-entry01','entry'),
        ('natural-service-route/sms-npc-d8-healer94-rest01','free_rest'),
        ('natural-dungeon-route/sms-sms-npc-d8-paid3c-entry01','entry'),
        ('natural-service-route/sms-npc-d8-paid3c-service02','paid_passage'),
        ('natural-dungeon-route/sms-sms-npc-d8-entry01','entry'),
        ('natural-dungeon-combat/sms-auto-sms-npc-d8-mini-ready01','entry_combat'),
        ('natural-dungeon-combat/sms-auto-sms-npc-d8-midboss01','intermediate_victory'),
        ('natural-dungeon-combat/sms-auto-sms-npc-d8-resume01','intermediate_resume'),
    ])
    d8=['entry_combat','contact_passage','contact_passage','earth_passage','thief_key','contact_passage','entry_combat']
    chain.extend((f'natural-dungeon-combat/sms-auto-sms-npc-d8-stage{i:02d}-'+('02' if i==6 else '01'),kind)
                 for i,kind in enumerate(d8,1))
    chain.extend([('natural-dungeon-combat/sms-auto-sms-npc-d8-boss01','eighth_crystal'),
                  ('natural-dungeon-combat/sms-auto-sms-npc-d8-exit01','eighth_dungeon_exit')])
    stages=[]
    expected=hashlib.sha256((ROOT/'input/original.sms').read_bytes()).hexdigest()
    for relative,kind in chain:
        folder=ROOT/'validation'/relative
        cap=read(folder/'capture.json')
        report=read(folder/('route_report.json' if kind=='entry' else 'report.json'))
        proof_path=folder.with_name(folder.name+f'-assisted-fixed-replay-{cap["frames"]}')/'replay_report.json'
        proof=read(proof_path)
        assert cap['rom_sha256']==proof['rom_sha256']==expected and cap['sram_input'] is None
        assert proof['passed'] and proof['whole_ram_bytes']==8192 and proof['final_png_exact']
        hashes={name:hashlib.sha256((folder/name).read_bytes()).hexdigest()
                for name in ('capture.json','controls.json','assistance.json')}
        assert hashes==proof['evidence']
        assert report['failure'] in (None,'frame_limit')
        raw=(folder/f'ram_{cap["frames"]:05d}.bin').read_bytes()
        assert raw[0x1d]==12 and raw[0x318]>0
        if kind.startswith('partial_'):
            assert not report['room_cleared']
        elif kind=='entry':assert report['reached_entrance']
        elif kind=='boss_defeated_reward_pending':
            assert report['room_cleared'] and not report['last_actors'] and raw[0xd0]&128
            assert raw[0xda]==40,'This checkpoint is before the real capacity reward'
        elif kind=='crystal_reward_finished':assert raw[0xd0]&128 and raw[0xda]==raw[0x318]==48
        elif kind=='dungeon_exit':assert report['full_dungeon_cleared'] and raw[0xba]==raw[0x37]==0
        elif kind=='gold_gift':assert report['passed'] and report['last_state']['gold']-report['first_state']['gold']==(50 if relative.endswith('sms-npc-gold-f4-gift01') else 30)
        elif kind=='key_purchase':
            assert report['passed'] and report['last_state']['keys']-report['first_state']['keys']==1
            assert report['first_state']['gold']-report['last_state']['gold']==60
        elif kind=='rope':assert report['item_acquisition_passed'] and raw[0xed]==1
        elif kind=='mechanism':assert report['contact_route_passed'] and report['contact_opened']['flags']&4
        elif kind=='dungeon_key':assert report['new_key_verified'] and raw[0xde]>0
        elif kind=='entry_combat':assert report['room_cleared']
        elif kind=='third_crystal':assert report['room_cleared'] and raw[0xd1]&128 and raw[0xda]==raw[0x318]==56
        elif kind=='third_dungeon_exit':assert report['full_dungeon_cleared'] and raw[0xba]==raw[0x37]==0
        elif kind=='earth_teacher':
            assert report['passed'] and report['first_state']['level']==0 and report['last_state']['level']==1
            assert report['first_state']['gold']-report['last_state']['gold']==50 and raw[0xe5]==1
            texts=read(folder/'dialogue_observations.json')['events']
            pcs={e['text_pc'] for e in texts if e['event_pc']==0x524 and e['outside']==0xa3 and e['room']==0xbf}
            assert {0xb06f,0xb35d}<=pcs
        elif kind=='earth_passage':assert report['earth_route_passed']
        elif kind=='canoe':assert report['item_acquisition_passed'] and raw[0xec]==1
        elif kind=='reach_room':assert report['target_room_reached']
        elif kind=='fourth_crystal':assert report['room_cleared'] and raw[0xd2]&128 and raw[0xda]==raw[0x318]==64
        elif kind=='fourth_dungeon_exit':assert report['full_dungeon_cleared'] and raw[0xba]==raw[0x37]==0
        elif kind=='fifth_crystal':assert report['room_cleared'] and raw[0xd3]&128 and raw[0xda]==raw[0x318]==72
        elif kind=='fifth_dungeon_exit':assert report['full_dungeon_cleared'] and raw[0xba]==raw[0x37]==0
        elif kind=='weapon_selection':assert report['passed'] and report['seen_menu'] and raw[0xdf]==report['selected_slot']
        elif kind in ('gillian_upgrade','battler_upgrade'):
            assert report['passed'] and report['first_state']['level']==1 and report['last_state']['level']==2
            assert report['first_state']['gold']-report['last_state']['gold']==(100 if kind=='battler_upgrade' else 0)
            assert raw[0xe4 if kind=='gillian_upgrade' else 0xe5]==2
        elif kind=='ice_bell':assert report['item_acquisition_passed'] and raw[0xea]==1
        elif kind=='sixth_crystal':assert report['room_cleared'] and raw[0xd4]&128 and raw[0xda]==raw[0x318]==80
        elif kind=='sixth_dungeon_exit':assert report['full_dungeon_cleared'] and raw[0xba]==raw[0x37]==0
        elif kind=='intermediate_victory':assert report['room_cleared'] and raw[0xce+raw[0x37]]&128==0
        elif kind=='intermediate_resume':assert report['resumed_after_verified_intermediate'] and report['new_assistance_writes']==1 and raw[0x305]==129
        elif kind=='ship':assert report['item_acquisition_passed'] and raw[0xf0]==1
        elif kind=='seventh_crystal':assert report['room_cleared'] and raw[0xd5]&128 and raw[0xda]==raw[0x318]==88
        elif kind=='seventh_dungeon_exit':assert report['full_dungeon_cleared'] and raw[0xba]==raw[0x37]==0
        elif kind=='armor3':assert report['passed'] and report['first_state']['armor']==2 and raw[0xf1]==3
        elif kind=='flame_sword':assert report['passed'] and report['first_state']['basic']==2 and raw[0xe0]==3
        elif kind=='paid_passage':assert report['passed'] and report['price']==10 and report['first_state']['gold']-report['last_state']['gold']==10
        elif kind=='thief_key':assert report['item_acquisition_passed'] and raw[0xef]==1
        elif kind=='eighth_crystal':assert report['room_cleared'] and raw[0xd6]&128 and raw[0xda]==raw[0x318]==96
        elif kind=='eighth_dungeon_exit':assert report['full_dungeon_cleared'] and raw[0xba]==raw[0x37]==0
        elif kind=='armor2':assert report['passed'] and report['first_state']['armor']==1 and raw[0xf1]==2
        elif kind=='long_sword':assert report['passed'] and report['first_state']['basic']==1 and raw[0xe0]==2
        elif kind=='boots':assert report['item_acquisition_passed'] and raw[0xee]==1
        elif kind=='supply_exit':assert report['dungeon_exit_verified'] and report['exit_before_crystal_requested'] and raw[0xba]==raw[0x37]==0
        elif kind=='contact_passage':assert report['contact_route_passed'] and report['contact_opened'] is not None
        elif kind=='free_rest':
            assert report['passed'] and report['normal_health_refill'] and raw[0x318]==raw[0xda]
            assert report['first_state']['gold']==report['last_state']['gold']
            assert report['first_state']['magic']==report['last_state']['magic']
        stages.append(dict(trace=relative,kind=kind,frame=cap['frames'],
                           fixed_replay=proof_path.relative_to(ROOT).as_posix(),evidence_sha256=hashes))
    state=dict(frame=cap['frames'],room=int.from_bytes(raw[0xb9:0xbb],'little'),health=raw[0x318],
               max_health=raw[0xda],gold=raw[0xdd],keys=raw[0xde],rope=raw[0xed],
               crystals=sum(bool(b&128) for b in raw[0xcf:0xd8]),second_boss_defeated=True)
    report=dict(passed=True,source_sha256=expected,stages=stages,
                second_crystal_reward_and_exit_verified=True,
                third_crystal_reward_and_exit_verified=True,
                fourth_crystal_reward_and_exit_verified=True,plate_mail_acquired=True,long_sword_acquired=True,
                fifth_crystal_reward_and_exit_verified=True,
                sixth_crystal_reward_and_exit_verified=True,ice_bell_acquired=True,
                seventh_crystal_reward_and_exit_verified=True,ship_acquired=True,
                eighth_crystal_reward_and_exit_verified=True,dragon_mail_acquired=True,flame_sword_acquired=True,
                thief_key_acquired=True,paid3c_passage_price=10,
                gillian_level=2,battler_level=2,battler_upgrade_price=100,
                running_boots_acquired=True,a1_gold_gift=30,key94_purchase_price=60,free_healer94_refill_verified=True,
                b4_gold_gift=30,earth_purchase_price=50,battler_dialogue_pcs=[0xb06f,0xb35d],canoe_acquired=True,
                f4_gold_gift=50,c7_key_purchase_price=60,
                rope_acquired=True,d3_mechanism_activated=True,
                latest_selected_prefix=chain[-1][0],current_sms_state=state,
                full_campaign_complete=False,all_npcs_complete=False,completion_percentage=None,
                limits=['The successful type63 fight uses recorded approach protection, removed before combat. Its reward acknowledgment is a separate verified stage.',
                        'Partial live fight/exit checkpoints are included only as replayed continuations, never as completed objectives.',
                        'Failed controller experiments and the earlier D3 attempt without a key are not selected.',
                        'Source reward flags can precede modal completion. The second crystal is accepted only after real capacity48 and HP refill, followed by movement and exterior return.',
                        'F4/B4 returns, teacher upgrade/refusals, equipment hints/returns, all merchant choices/pages, remaining NPCs/quests and paired MD checks remain open.',
                        'Guide observations are sampled screenshots. Neither episode has been watched in full.'])
    (ROOT/'analysis/sms_npc_campaign_progress_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,stages=len(stages),current=state)))


if __name__=='__main__':main()
