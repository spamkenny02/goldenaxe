"""Cross-reference the provided guide, original code and eight played scenarios."""
import hashlib,json,shutil
from run_core import ROOT
from extract_room_clear import z80


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source=ROOT/'input/original.sms';rom=source.read_bytes()
    guide=ROOT/'validation/gamefaqs-64050-source/guide-numbered.txt'
    assert sha(guide)=='a280984598af274a8a1126df34aff50cf421785276acfb76691838bba6c6f351'
    folder=ROOT/'reports/gaw-textes-guide-2026-11-12';folder.mkdir(parents=True,exist_ok=True)
    ordinary=[];fixed=[];pictures=[]
    cases=['l10-earth1','l10-earth2','l15-earth2','aires-bell','aires-after-linda']
    for case in cases:
        selected=json.loads((ROOT/f'analysis/sms_guide_text_test_{case}.json').read_bytes());assert selected['passed']
        path=ROOT/'validation'/selected['trace'];capture=json.loads((path/'capture.json').read_bytes())
        played=json.loads((path/'report.json').read_bytes())
        proof=path.with_name(path.name+f'-assisted-fixed-replay-{capture["frames"]}')/'replay_report.json'
        replay=json.loads(proof.read_bytes());assert replay['passed'] and replay['whole_ram_bytes']==8192 and replay['final_png_exact']
        assert replay['evidence']=={name:sha(path/name) for name in ('capture.json','controls.json','assistance.json')}
        assert all(v['render_completed'] for v in played['visited'])
        observation=json.loads((path/'dialogue_observations.json').read_bytes())
        actual_entries=[dict(frame=e['frame'],text_pc=e['text_pc'],caller=e['caller'],room=e['room'])
            for e in observation['events'] if e['frame']>played['prefix_end'] and e['event_pc'] in (0x50c,0x524)]
        ordinary.append(dict(case=case,selected_test=selected,interaction_report=played,replay_report=replay,
            actual_formatter_entries=actual_entries,replay_path=proof.relative_to(ROOT).as_posix(),observer_sha256=sha(path/'dialogue_observations.json')))
        wanted=0xa937 if case.startswith('aires') else 0x96ec if case.startswith('l10') else 0x99f1
        visit=next(v for v in played['visited'] if v['text_pc']==wanted)
        event=next(e for e in observation['events'] if e['event_pc']==0x627a and visit['entry_frame']<=e['frame']<=visit['acknowledged_and_walked_away_frame'])
        frame=event['frame']+1;picture=path/f'frame_{frame:05d}.png';assert picture.exists()
        target=folder/(case+'.png');shutil.copyfile(picture,target)
        pictures.append(dict(case=case,file=target.name,source=str(picture),sha256=sha(picture),frame=frame,text_pc=wanted))
    for case in ('battler-terre1-outer02','battler-terre2-outer02','battler-retour-outer02'):
        path=ROOT/'validation/sms-guide-fixed-dialogues'/case
        report=json.loads((path/'report.json').read_bytes())
        assert report['passed'] and report['whole_ram_exact'] and report['final_pixels_exact'] and report['whole_ram_bytes']==8192
        fixed.append(dict(case=case,report=report,observer_sha256=sha(path/'dialogue_observations.json')))
        for index,entry in enumerate(report['completed_renderings']):
            picture=path/f'frame_{entry["capture_frame"]:05d}.png';target=folder/(case+f'-{index}.png')
            shutil.copyfile(picture,target);pictures.append(dict(case=case,file=target.name,source=str(picture),
                sha256=sha(picture),frame=entry['capture_frame'],text_pc=entry['text_pc']))
    assert rom[0xad19:0xad2f]==bytes.fromhex('01ec02112fadcd7e660148021138adcd7e66cdd065c9')
    assert rom[0xad3e:0xad41]==bytes.fromhex('fe37a9')
    assert rom[0x7a56:0x7a5d]==bytes.fromhex('3ae5c0fe012830')
    p=0x7a56;loads=[]
    while p<0x7ac8:
        instruction=z80.decode(rom[p:p+8],p);assert instruction.len
        if rom[p]==0x21:loads.append(dict(address=p,text_pc=int.from_bytes(rom[p+1:p+3],'little')))
        p+=instruction.len
    assert p==0x7ac8 and {v['text_pc'] for v in loads}=={0xb06f,0xb165,0xb225,0xb233,0xb333,0xb35d,0xb3e5,0xb3a0,0x8bcd}
    md=ROOT/'versions/v0321-89c58333/gaw-megadrive-v0321.bin';native=md.read_bytes();missing=[]
    for offset in (0xda58,0xda7c,0xed3c):
        text=rom[offset:rom.index(0,offset)+1];assert text not in native
        missing.append(dict(sms_offset=f'0x{offset:04X}',cpu_pointer=0x8000+(offset&0x3fff),
            original_bytes_hex=text.hex(),present_in_sms=True,present_verbatim_in_v321=False,
            attributed_speaker_proven=False,unused_in_sms_proven=False))
    all_pcs={v['text_pc'] for c in ordinary for v in c['actual_formatter_entries']}
    all_pcs.update(v['text_pc'] for c in fixed for v in c['report']['actual_entries'])
    assert not all_pcs&{0x9a58,0x9a7c,0xad3c}
    result=dict(date='2026-11-12',source_sha256=sha(source),md_v321_sha256=sha(md),passed=True,
        guide=dict(url='https://gamefaqs.gamespot.com/sms/588075-golden-axe-warrior/faqs/64050',
            numbered_source_sha256=sha(guide),locations=[
                dict(location='D10',speaker='Battler',lines=[1491,1499],role='Earth teacher; upgrade also described at2380'),
                dict(location='L10',speaker='unnamed informant',lines=[1860,1863],role='Advice about Earth level2'),
                dict(location='L15',speaker='unnamed informant',lines=[1879,1882],role='Death Adder rumour, preceding the first target physically in ROM'),
                dict(location='Aires O15, right house',speaker='unnamed resident on the left',lines=[607,617],role='Remembers being told the Bell has a mysterious power, but cannot recall it')],
            exact_three_target_replies_attributed_by_guide=False),
        reported_strings=missing,ordinary_gameplay_checks=ordinary,fixed_gameplay_checks=fixed,pictures=pictures,
        new_scenarios_played=8,source_argument_checks=dict(
            aires_room3_script='0xAD19..0xAD2E',aires_script_bytes=rom[0xad19:0xad2f].hex(),
            aires_left_npc_table='base0xAD38, row0xAD3E: FE 37 A9',aires_selected_text='0xA937',
            aires_selection_inputs=['stationary Up','NPC coordinate','previous exterior room'],
            aires_bell_or_water_condition=False,
            battler_handler='0x7A56..0x7AC7 plus common7B18..7B32',
            battler_possible_text_pcs=[0xb06f,0xb165,0xb225,0xb233,0xb333,0xb35d,0xb3e5,0xb3a0,0x8bcd],
            battler_verified_immediate_load_sites=loads,
            earth_level_address='0xC0E5',original_handler_hex=rom[0x7a56:0x7ac8].hex()),
        source_trigger_found=False,global_unused_proven=False,point5_complete=False,rom_modified=False,
        limits=['Guide contexts identify candidates, not a confirmed speaker for any of the three target replies.',
            'Aires without Bell ownership was not naturally reached by these tests; the candidate handler is statically unconditional on Bell ownership.',
            'Initial failed controller trials and the Water-zero extra baseline are retained only as diagnostics, not admitted as the after-Linda case.',
            'This excludes the checked source NPC routes, not every possible unclassified indirect route in the whole ROM.'])
    (ROOT/'analysis/sms_guide_text_investigation.json').write_text(json.dumps(result,indent=2)+'\n')
    (folder/'PREUVES.json').write_text(json.dumps(result,indent=2)+'\n')
    text='''# Trois textes SMS — code, guide et jeu

Les chaînes DA58, DA7C et ED3C existent dans la ROM SMS fournie. Leurs octets exacts sont absents de la V321. Aucun locuteur des trois répliques n'est encore démontré.

## Repères du guide et vérifications

Le [guide d'Andrew Light](https://gamefaqs.gamespot.com/sms/588075-golden-axe-warrior/faqs/64050) situe Battler en D10, un informateur sur Terre niveau 2 en L10, et un habitant qui a oublié le pouvoir de la cloche dans la maison droite d'Aires, O15. Il n'attribue pas les trois répliques précises signalées. Ces correspondances thématiques servent de pistes, pas d'attributions certaines.

| Candidat | Essai SMS réellement effectué | Texte sélectionné |
| --- | --- | --- |
| Battler, D10 | Premier achat : Terre 0 → 1, 50 cornes débitées | B06F puis B35D |
| Battler, D10 | Amélioration : Terre 1 → 2, 100 cornes débitées | B233 puis B3E5 : « A apprit la seconde Magie Terre. » |
| Battler, D10 | Revisite avec Terre 2 | B333 : « Je n'ai plus rien à t'apprendre. » |
| Informateur L10 | Visite avec Terre 1, puis avec Terre 2 | 96EC dans les deux cas : indice sur les rochers cassables |
| Informateur L15 | Revisite avec Terre 2 et neuf cristaux | 99F1 : rumeur sur Death Adder, conforme au repère L15 du guide |
| Aires, maison droite, habitant à gauche | Cloche réellement sélectionnée puis sonnée dehors ; nouvelle conversation | A937 : il dit toujours ne pas se souvenir |
| Même habitant d'Aires | Après ouverture réelle du passage de Linda et apprentissage d'Eau | A937 également ; Eau 1 et drapeau AA ouvert sont contrôlés |

Huit scénarios ont été rejoués depuis le démarrage de la ROM. Les cinq visites nouvelles ont une relecture indépendante reproduisant les 8192 octets de RAM et l'image finale. Les trois relectures de Battler reproduisent aussi exactement ces états. Aucun objet, niveau de magie, argent ou état de quête n'est injecté ; la protection d'approche héritée reste déclarée. Pour Battler, l'adresse de retour et la position de pile distinguent la fin du message du retour interne après impression du nom du héros.

## Ce que sélectionne le code original

Dans la pièce 03 d'Aires, le script AD19–AD2E appelle deux fois le sélecteur ordinaire 667E. Pour le PNJ de gauche, la table AD38 contient FE 37 A9 : le texte est A937. Cette sélection dépend de l'emplacement du PNJ et de la provenance FE. Elle ne lit ni possession de cloche, ni utilisation de cloche, ni niveau d'Eau. Le code de ce PNJ ne sélectionne pas AD3C, adresse CPU du texte ED3C.

Battler utilise le niveau de Terre en C0E5, les prérequis de vie, la réponse et l'argent disponible. Sa routine 7A56–7AC7 et sa sortie commune sélectionnent B06F, B165, B225, B233, B333, B35D, B3E5, B3A0 ou 8BCD. Les deux adresses 9A58 et 9A7C n'appartiennent pas à ces choix. Le « second papier » semble désigner le second niveau de Terre ; cette interprétation ne prouve pas quel autre PNJ aurait dû commenter son acquisition.

Le voisin physique de DA58, en L15, parle de Death Adder. Le guide confirme ce sujet. L'emplacement d'une chaîne à la suite d'une autre dans la ROM ne lui attribue donc pas le même locuteur.

## Captures des nouvelles preuves

Après achat effectif de Terre niveau 2 :

![Battler, Terre 2](battler-terre2-outer02-1.png)

Habitant d'Aires après avoir sonné la cloche :

![Aires après la cloche](aires-bell.png)

Même habitant après Linda et Eau :

![Aires après Linda](aires-after-linda.png)

## Conclusion et limites

Les tests n'établissent pas de dialogue SMS déclenché qui manquerait sur MD pour ces trois phrases. Les candidats désignés par les thèmes du guide ont des répliques différentes, confirmées par leurs sélecteurs et par l'exécution. Les trois textes restent sans locuteur ni déclencheur démontrés ; leur inutilisation globale n'est pas affirmée. La ROM V321 reste inchangée.

Le cas Aires avant possession de la cloche n'a pas été joué ici. Les essais de contrôleur échoués et un état supplémentaire sans Eau restent des diagnostics, pas des preuves de conditions remplies.

[Données, octets de code, repères de guide et rapports d'exécution](PREUVES.json).
'''
    (folder/'RAPPORT.md').write_text(text,encoding='utf-8')
    print(json.dumps(dict(passed=True,scenarios=8,pictures=len(pictures),source_trigger_found=False)),flush=True)


if __name__=='__main__':main()
