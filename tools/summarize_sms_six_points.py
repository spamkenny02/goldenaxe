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
    point2['fully_learned_teacher_returns']=read('sms_teacher_returns_campaign.json')
    point3['gambling_branches']=[read(f'sms_minigame_{n}_{v}_campaign.json') for n,v in
        [('13','play'),('5c','play'),('5c','poor'),('5c','refuse'),('a7','play'),('de','play')]]
    point3['money_house_tour']=read('sms_gold_house_census_campaign.json')
    point3['inn_acceptances']=read('sms_inn_locations_campaign.json')
    point3['save_locations']=read('sms_save_locations_campaign.json')
    point3['paid_passages']=read('sms_passage_census_campaign.json')
    shield=read('sms_dragon_shield_campaign.json')
    point4=dict(status='in_progress',complete=False,equipment_hint_branches=read('sms_equipment_hint_branches.json'))
    if shield and shield.get('passed'):point4['dragon_shield']=verified(shield['last_verified_prefix'])
    point4['hidden_rewards']=read('sms_hidden_rewards_campaign.json')
    point4['curse_and_oil_remedy']=verified('natural-dungeon-combat/sms-auto-sms-npc-palace-extended-curse-remedy01')
    point4['curse_and_oil_remedy']['actual_contact_and_oil_consumption_verified']=True
    points={
        '1_o3':point1,'2_teachers_and_capacity':point2,'3_services':point3,
        '4_equipment_hints_hidden_rooms_curse':point4,
        '5_reported_strings':dict(status='adjacent_npc_dispatch_reconciled_global_reachability_open',offsets=['0xDA58','0xDA7C','0xED3C'],unused_proven=False,
            reconciliation=read('reported_text_dispatch_reconciliation.json')),
        '6_final_replay_and_video':dict(status='main_campaign_video_ready_annexes_pending',complete_100_percent_video=False,
            main_campaign_video=read('sms_extended_campaign_video_report.json'))}
    report=dict(date='2026-11-11',source_sha256=hashlib.sha256((ROOT/'input/original.sms').read_bytes()).hexdigest(),
        all_npcs_complete=False,all_side_quests_complete=False,points=points)
    (ROOT/'analysis/sms_six_points_progress.json').write_text(json.dumps(report,indent=2)+'\n')
    def count(data,key):return len((data or {}).get(key,[]))
    text=f'''# État des six points SMS — 11 novembre 2026

1. **O3 terminé.** Accès réel, conversation, acquittement et sortie rejoués indépendamment.
2. **Acquisitions terminées.** Enseignements 2/2/2/1, huit récompenses de fées présentes, capacités vie/magie 128/128. Retours chez les quatre maîtres vérifiés dans une branche distincte ; cela ne clôt pas toutes leurs variantes précoces.
3. **Services en cours.** {count(service,'completed_visits')}/48 contextes marchand/soigneur/sauvegarde avec refus et sortie rejoués ; {count(point3['inn_acceptances'],'completed_locations')}/11 auberges acceptées ; {count(point3['save_locations'],'completed_locations')}/14 lieux avec sauvegarde effective puis Continuer normal ; {count(point3['paid_passages'],'completed_passages')}/6 directions de passage payant. Quatre lieux de jeu parcourus, pertes/gains/rejouer/refus et manque d'argent sélectionnés. Trois slots de sauvegarde vérifiés à Eren. {count(point3['money_house_tour'],'completed_houses')}/31 maisons d'argent à entrée directe et retours vérifiés ; deux autres lignes de table restent à clarifier. Les transactions et variantes économiques restantes ne sont pas réputées couvertes.
4. **Équipements et annexes en cours.** Récompenses principales, cinq indices avant récompense, pomme de J9, huile cachée à Kari-Kari, corrosion réelle et consommation de l'huile vérifiées. Des variantes et retours restent ouverts.
5. **Trois textes non résolus globalement.** Les dialogues voisins de DA58/DA7C/ED3C et les retours du formateur ne sont pas leurs déclencheurs. Leur inaccessibilité dans toute la ROM n'est pas prouvée.
6. **Campagne vidéo prête, preuve exhaustive en cours.** Parcours continu étendu de 564131 images jusqu'à la fin, 2 h 36 min 54 s, audio/vidéo décodés et RAM/pixels finaux exacts. Des annexes séparées sont enregistrées ; elles ne sont pas présentées comme une seule partie continue.

Deux points sont clos dans le périmètre demandé (1 et 2). Les points 3, 4 et 5 restent ouverts ; le point 6 est partiel. Aucun pourcentage global ni certificat tous PNJ/toutes quêtes n'est déduit du nombre de lignes de cette liste. La couverture correspondante sur Mega Drive et les comparaisons PAL/NTSC restent distinctes.

Les traces et preuves figurent dans [le relevé JSON](sms_six_points_progress.json) ; les vidéos sont indexées [ici](../videos/sms/README.md).
'''
    (ROOT/'analysis/ETAT_SIX_POINTS_SMS.md').write_text(text,encoding='utf-8')
    print(json.dumps({k:v['status'] for k,v in points.items()}))


if __name__=='__main__':main()
