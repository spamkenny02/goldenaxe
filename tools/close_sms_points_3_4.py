"""Close the user's SMS service/equipment obligations from bound played evidence.

This does not certify the separate MD comparison, global NPC census, unresolved
strings, or the final exhaustive video. Currency-assisted tests stay distinct.
"""
import hashlib,json
from functools import lru_cache
from PIL import Image
from run_core import ROOT


def read(name):return json.loads((ROOT/'analysis'/name).read_bytes())
def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        while data:=f.read(1024*1024):h.update(data)
    return h.hexdigest()


@lru_cache(None)
def receipt(trace,component=False):
    folder=ROOT/'validation'/trace;c=json.loads((folder/'capture.json').read_bytes())
    r=json.loads((folder/('report.json' if (folder/'report.json').exists() else 'route_report.json')).read_bytes())
    assert not r.get('failure') and (r.get('passed') or r.get('room_cleared') or r.get('reached_entrance'))
    assert c['rom_sha256']==ROM_SHA and c['sram_input'] is None
    end=c['frames'];proof=folder.with_name(folder.name+('-economic-fixed-replay' if component else f'-assisted-fixed-replay-{end}'))
    p=json.loads((proof/'replay_report.json').read_bytes());assert p['passed'] and p['whole_ram_bytes']==8192
    assert p.get('final_pixels_exact',p.get('final_png_exact',False))
    assert (folder/f'ram_{end:05d}.bin').read_bytes()==(proof/f'ram_{end:05d}.bin').read_bytes()
    assert Image.open(folder/f'frame_{end:05d}.png').convert('RGB').tobytes()==Image.open(proof/f'frame_{end:05d}.png').convert('RGB').tobytes()
    for name,value in p['evidence'].items():assert digest(folder/name)==value,(trace,name)
    if component:assert p['currency_assisted_component_test'] and p['inventory_actor_health_and_quest_writes']==0
    else:assert p.get('boss_assistance') is False and not p.get('feedback_reads',False)
    selected[trace]=dict(frame=end,proof=(proof/'replay_report.json').relative_to(ROOT).as_posix(),
        proof_sha256=digest(proof/'replay_report.json'),report_sha256=digest(folder/('report.json' if (folder/'report.json').exists() else 'route_report.json')),
        final_ram_sha256=digest(folder/f'ram_{end:05d}.bin'),currency_assisted_component_test=component,
        input_evidence=p['evidence'])
    return r


def main():
    global ROM_SHA,selected
    ROM_SHA=digest(ROOT/'input/original.sms');selected={};rom=(ROOT/'input/original.sms').read_bytes()
    merchant=read('merchant_assets.json')
    towns=[[rom[p],0,rom[p+1]] for p in range(0x796a,0x7986,2)]
    towns += [[rom[0x752e+n],1,rom[0x7533+n]] for n in range(5)]
    towns += [[rom[0x75a8+n],2,0] for n in range(4)]
    assert towns==merchant['towns'] and len(towns)==23
    for group in range(6):
        for option in range(3):
            off=0x7986+group*14+option*4
            assert merchant['goods'][group][option][:2]==list(rom[off+2:off+4])
    assert list(rom[0x75ac:0x75b2])==[2,4,8,20,30,50]
    tour=read('sms_service_refusal_campaign.json');assert len(tour['completed_visits'])==48 and not tour['pending']
    for v in tour['completed_visits']:assert receipt(v['trace'])['resources_unchanged']
    variants=['g0','g1','g2','g3','g4','g5','g2oil','shield-owned','shield-better','apple-only','apple-poor',
        'magic64','magic32-poor','magic-clamp','magic-poor']
    purchased=set();outcomes=set();variant_rows=[]
    for key in variants:
        v=read(f'sms_merchant_variant_{key}.json');assert v['passed'];r=receipt(v['trace'])
        for action in r['completed']:
            outcomes.add(action['expect'])
            if action['expect']=='buy':purchased.add((action['item'],action['price']))
        variant_rows.append(dict(case=key,trace=v['trace']))
    shield_purchase=read('sms_knight_shield_campaign.json');assert shield_purchase['passed']
    receipt(shield_purchase['last_verified_prefix']);purchased.add((25,250))
    expected={(item,price) for g in merchant['goods'] for item,price,_ in g}|{(12,40),(0x110,20),(0x120,30),(0x140,50)}
    assert expected<=purchased and outcomes=={'buy','poor','owned','better','full'}
    capacity=read('sms_keys_capacity_component_report.json');assert capacity['passed']
    receipt(capacity['trace'],True);assert capacity['final_keys']==99 and capacity['ordinary_key_purchases']>0
    inns=read('sms_inn_locations_campaign.json');assert len(inns['completed_locations'])==11
    for v in inns['completed_locations']:receipt(v['trace'])
    repeat=read('sms_inn_repeat_report.json');assert repeat['passed'] and repeat['health_already_full'];receipt(repeat['second_night_trace'])
    save=read('sms_save_locations_campaign.json');assert len(save['completed_locations'])==14
    for v in save['completed_locations']:
        written=receipt(v['save_trace']);loaded=json.loads((ROOT/v['continue_report']).read_bytes())
        assert loaded['passed'] and all(loaded['checks'].values()) and not loaded['synthetic_sram_fixture']
        assert written['sram_sha256']==loaded['source_sram_sha256']
    slots=read('sms_actual_save_slots_report.json');assert slots['passed'] and len(slots['slots'])==3
    for v in slots['slots']:receipt(v['source_recording']);assert all(v['checks'].values())
    overwrite=read('sms_save_overwrite_report.json');assert overwrite['passed']
    receipt(overwrite['second_save_trace']);assert overwrite['original_payload_sha256']!=overwrite['replacement_payload_sha256']
    assert json.loads((ROOT/overwrite['continue_report']).read_bytes())['passed']
    passages=read('sms_passage_census_campaign.json');assert len(passages['completed_passages'])==6 and not passages['pending']
    for v in passages['completed_passages']:
        r=receipt(v['trace']);assert r['target']==v['destination'] and r['price']==10
    alternatives=['inn20-poor','inn40-poor','passage-poor']+[f'passage-refuse-{o:02x}' for o in (0x1a,0x3c,0x36,0x87,0x6d,0x96)]
    for key in alternatives:
        v=read(f'sms_service_alternative_{key}.json');assert v['passed'];r=receipt(v['trace'])
        assert r['confirmation_frame'] and (r['poor_text_frame'] if r['variant']=='poor' else True)
    games=[];specials={};wins=losses=False
    for outside,variant in [('13','play'),('5c','play'),('a7','play'),('de','play'),('5c','poor'),('5c','refuse')]:
        v=read(f'sms_minigame_{outside}_{variant}_campaign.json');assert v['passed'];trace=v['last_verified_prefix'];r=receipt(trace)
        games.append(trace)
        for outcome in r.get('outcomes') or ([r['outcome']] if r.get('outcome') else []):
            wins|=outcome['amount']>0;losses|=outcome['amount']<0
            for frame in range(outcome['frame'],outcome['frame']+6):
                snapshot=ROOT/'validation'/trace/f'ram_{frame:05d}.bin'
                if snapshot.exists():
                    card=snapshot.read_bytes()[0x1c0c]
                    if card in (0x38,0x39):specials[card]=dict(trace=trace,frame=frame,snapshot_sha256=digest(snapshot))
                    break
    lucky=read('sms_minigame_lucky_campaign.json');assert lucky['passed'] and not lucky['source_rng_writes']
    r=receipt(lucky['trace']);assert r['lucky_card_observed']
    specials[0x38]=dict(trace=lucky['trace'],outcomes=[o for o in r['outcomes'] if o['special_card']==0x38])
    assert set(specials)=={0x38,0x39} and wins and losses
    point3=dict(status='complete',known_service_contexts=dict(merchants=23,inns=11,saves=14,passages=6,gambling_hosts=4),
        merchant_tables_checked_against_rom=True,merchant_transactions_by_shared_goods_group=True,
        successful_distinct_item_price_offers=len(expected),merchant_variants=variant_rows,
        all_shared_merchant_result_classes=sorted(outcomes),all_inns_accepted=True,all_save_locations_written_and_normally_loaded=True,
        save_slots=[0,1,2],real_save_overwrite=overwrite,all_six_passage_directions_paid_and_refused=True,
        poor_service_cases=['inn20-poor','inn40-poor','passage-poor'],gambling_traces=games,
        gambling_special_cards={f'0x{k:02X}':v for k,v in specials.items()},
        limits=['Every known location is visited. Equivalent transaction handlers are covered by their identical ROM goods group, not every cross-product of place and inventory.',
                'The keys-at-99 test uses explicitly authorized money assistance, with ordinary purchases and no key/item/quest writes.',
                'The two unmatched money-table rows AD/F3 are a separate open reachability audit, not additional merchant/inn/save/passage/game locations.'])
    gifts=[(0x27,'natural-service-route/sms-npc-equipment-27-gift01',0xf1,2),
        (0x50,'natural-service-route/sms-npc-equipment-50-gift01',0xe0,2),
        (0xb1,'natural-service-route/sms-npc-d8-dragonmail-gift01',0xf1,3),
        (0x6a,'natural-service-route/sms-npc-d8-flamesword-gift01',0xe0,3),
        (0xc7,'natural-service-route/sms-sms-npc-villagec7-oil02',0xe8,1)]
    d=read('sms_dragon_shield_campaign.json');gifts.append((0x4c,d['last_verified_prefix'],0xf2,3))
    hidden=read('sms_hidden_rewards_campaign.json')
    for v in hidden['completed_rewards']:gifts.append((v['outside'],v['trace'],0xe0+v['inventory_slot'],1))
    assert len(gifts)==8
    gift_rows=[]
    for outside,trace,offset,value in gifts:
        receipt(trace);p=ROOT/'validation'/trace;c=json.loads((p/'capture.json').read_bytes());raw=(p/f'ram_{c["frames"]:05d}.bin').read_bytes()
        assert raw[offset]==value and raw[0x100+outside]&2
        gift_rows.append(dict(outside=outside,trace=trace,inventory_address=offset,value=value))
    returns=read('sms_equipment_returns_campaign.json');assert len(returns['completed_visits'])==8
    for v in returns['completed_visits']:assert receipt(v['trace'])['resources_and_flags_unchanged']
    texts={};quest_traces=[]
    for v in read('sms_equipment_hint_branches.json')['contexts']:quest_traces.append((v['trace'],False))
    for key in ('no-lightning','low-health-capacity','shield-before-crystal','shield-after-crystal-hint'):
        v=read(f'sms_equipment_prerequisite_{key}.json');assert v['passed'];quest_traces.append((v['trace'],False))
    for key in ('j9-owned-apple','kari-owned-oil','saylun-owned-apple'):
        v=read(f'sms_owned_quest_item_{key}.json');assert v['passed'];quest_traces.append((v['trace'],bool(v.get('currency_assisted_component_test'))))
    for trace,component in quest_traces:
        r=receipt(trace,component)
        for event in r.get('visited',[])+r.get('text_entries',[]):texts.setdefault(event['text_pc'],[]).append(trace)
    required={r['cpu'] for r in read('house_quest_reference.json')['strings']}
    assert required<=set(texts),(required-set(texts))
    cure_trace='natural-dungeon-combat/sms-auto-sms-npc-palace-extended-curse-remedy01';cure=receipt(cure_trace)
    assert cure['curse_remedy_passed'] and cure['first_curse']['frame']<cure['first_cure']['frame']
    assert cure['last_state']['curse']==cure['last_state']['oil']==0 and cure['resource_or_actor_writes']==0
    point4=dict(status='complete',reward_contexts=gift_rows,post_reward_returns=returns['completed_visits'],
        original_quest_dialogue_count=len(required),observed_quest_dialogues={f'0x{pc:04X}':sorted(set(texts[pc])) for pc in sorted(required)},
        all_nine_original_quest_dialogues_displayed_and_acknowledged=True,
        both_hidden_stair_interiors_entered_and_exited_before_and_after_reward=True,
        prerequisites_checked=['No Lightning','Health capacity below 56 with rope obtained before third crystal','Sixth crystal absent and present','Already carrying genuinely obtained apple/oil'],
        real_corrosion_and_oil_cure_trace=cure_trace,
        limits=['The Saylun already-owned-apple branch uses one explicitly declared money refill for a real purchase, plus declared approach protection. No item or quest flag is injected.',
                'These receipts close the requested SMS equipment/hint/chimney/corrosion checks. They do not certify every possible inventory permutation or the paired MD graphics/audio behavior.'])
    report=dict(date='2026-11-11',source_sha256=ROM_SHA,passed=True,point3=point3,point4=point4,
        selected_receipts=selected,all_npcs_complete=False,all_side_quests_complete=False,
        point5_and_point6_complete=False,currency_assisted_tests=[capacity,read('sms_owned_quest_item_saylun-owned-apple.json')])
    (ROOT/'analysis/sms_points_3_4_closure.json').write_text(json.dumps(report,indent=2)+'\n')
    folder=ROOT/'reports/gaw-sms-points-3-4-2026-11-11';folder.mkdir(parents=True,exist_ok=True)
    copies=[]
    for trace,entry in sorted(selected.items()):
        source=ROOT/'validation'/trace
        report_file=source/('report.json' if (source/'report.json').exists() else 'route_report.json')
        copies.append(dict(trace=trace,receipt=entry,interaction_report=json.loads(report_file.read_bytes()),
            replay_report=json.loads((ROOT/entry['proof']).read_bytes())))
    (folder/'PREUVES.json').write_text(json.dumps(dict(source_sha256=ROM_SHA,selected_reports=copies,
        scope='Copies of actual interaction/replay reports. Raw input recordings and captures remain local under validation.'),indent=2)+'\n')
    text=f'''# Points 3 et 4 SMS — clôture du 11 novembre 2026

Les deux points sont validés sur la ROM SMS fournie, SHA-256 `{ROM_SHA}`.
Le relevé conserve **{len(selected)} enregistrements sélectionnés**, leurs preuves de relecture, les hashes des entrées et les états finaux. Chaque relecture reproduit les 8192 octets de RAM et les pixels finaux, depuis le démarrage, sans import d'état d'émulateur.

Les rapports d'exécution et de relecture sont conservés dans [PREUVES.json](PREUVES.json). Les commandes brutes et captures restent dans le répertoire local `validation` ; elles ne sont pas incluses dans ce fichier de rapports.

## Point 3 — services

| Obligation | Résultat |
| --- | --- |
| Marchands | 23 contextes visités ; les six groupes de marchandises et les deux commerces spécialisés sont exercés. |
| Achats | Les 18 offres distinctes objet/prix sont effectivement achetées ; monnaie et effet vérifiés. Les tables partagées sont recoupées octet par octet avec la ROM. |
| Refus marchands | Argent insuffisant, objet déjà possédé, équipement inférieur et capacité pleine observés. Vie pleine, magie pleine et 99 clés sont distingués. |
| Auberges | 11 lieux : refus et nuit acceptée ; manque d'argent aux tarifs 20 et 40 ; revisite payée avec vie déjà pleine, magie conservée. |
| Sauvegardes | 14 lieux : écriture réelle puis redémarrage avec Continuer ; trois slots vérifiés à Eren ; écrasement d'un vrai slot après un vrai gain d'argent, puis rechargement du nouvel état. |
| Passages | Six directions : paiement, destination réelle et refus ; insuffisance de fonds vérifiée pour le tarif commun de 10. |
| Jeux | Quatre hôtes ; premier refus, manque d'argent, pertes, gains, seconde partie payée et refus de rejouer. Les deux cartes spéciales 38/39 sont obtenues sans écrire le hasard. |

Chaque lieu a sa visite propre. Les transactions équivalentes sont regroupées seulement quand les données et le code originaux sont identiques ; tous les croisements lieu × inventaire ne sont pas rejoués artificiellement.

## Point 4 — équipements et annexes

Les huit récompenses sont effectivement obtenues : deux armures, deux épées, le bouclier de dragon, les deux pommes et l'huile cachée. Les huit contextes sont ensuite revisités, avec contacts des anciens emplacements des donneurs et indices, sans second don ni modification des ressources.

**Les neuf dialogues du catalogue original de ces quêtes sont tous affichés et acquittés** : AC1E, A52F, 8E5C, 8E94, 8ED9, 8BEA, 8FE3, 90BF et 905B. Les cas couvrent l'absence de Foudre, la vie maximale inférieure à 56, le sixième cristal absent/présent, et la possession préalable d'une pomme ou d'huile.

Pour atteindre les états précoces, des détours réels sont utilisés : corde prise avant le troisième cristal ; autre branche entrant au troisième labyrinthe avant de finir le deuxième, sans apprendre Foudre. Les deux accès derrière les cheminées sont empruntés avant et après les dons. La corrosion résulte d'un vrai contact ennemi après retrait de la protection ; l'huile est réellement consommée pour lever l'effet.

## Aides déclarées et limites

L'aide d'approche est enregistrée et interdite pendant les boss. Deux essais séparés utilisent l'argent infini déjà autorisé : achats normaux jusqu'à 99 clés, puis refus ; achat normal d'une pomme avant le premier don de Saylun, puis réponse 905B. Ces deux branches ont leur propre relecture et restent identifiées comme tests monétaires assistés. Aucune clé, pomme, vie, créature ou étape de quête n'est injectée.

Cette clôture porte sur les deux obligations SMS demandées. Les trois textes DA58/DA7C/ED3C restent au point 5. Le montage vidéo exhaustif et les annexes restent au point 6. La comparaison correspondante sur Mega Drive, notamment en PAL/NTSC, n'est pas déduite de ces preuves SMS. Les deux lignes d'argent AD/F3 sans entrée directe restent un audit distinct ; elles ne sont pas comptées comme lieux de services supplémentaires.

[Relevé détaillé et hashes](../../analysis/sms_points_3_4_closure.json).
'''
    (folder/'RAPPORT.md').write_text(text,encoding='utf-8')
    print(json.dumps(dict(passed=True,point3='complete',point4='complete',receipts=len(selected),quest_texts=len(required),successful_offers=len(expected))),flush=True)


if __name__=='__main__':main()
