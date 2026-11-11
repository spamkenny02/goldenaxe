"""Original French game dossier, with ROM-derived catalogs and a guide cross-index.

The copyrighted guide cache stays under ignored validation/. Its prose, dialogue
transcriptions and ASCII maps are not redistributed in the generated package.
"""
import collections,csv,hashlib,json,re,subprocess,sys,zipfile
from pathlib import Path
from run_core import ROOT
from natural_dungeon_route import World
from extract_title import rle_planes

DATE='2026-11-11'
URL='https://gamefaqs.gamespot.com/sms/588075-golden-axe-warrior/faqs/64050'
OUT=ROOT/'reports'/('gaw-reference-'+DATE)


def read(name):return json.loads((ROOT/'analysis'/name).read_bytes())
def sha(data):return hashlib.sha256(data).hexdigest()
def coord(n):return chr(65+(n&15))+str(n>>4)
def signed(n):return n if n<128 else n-256
def csvfile(name,rows):
    assert rows
    with (OUT/name).open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def table(headers,rows):
    return '| '+' | '.join(headers)+' |\n| '+' | '.join('---' for _ in headers)+' |\n'+''.join('| '+' | '.join(str(v).replace('|','/') for v in row)+' |\n' for row in rows)
def crows(file,array):
    s=(ROOT/'megadrive/src'/file).read_text()
    body=re.search(r'\b'+re.escape(array)+r'\s*(?:\[[^\]]*\])+\s*=\s*\{(.*?)\};',s,re.S)[1]
    return [list(map(int,x.split(','))) for x in re.findall(r'\{([\d, ]+)\}',body)]


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    rom=(ROOT/'input/original.sms').read_bytes();world=World()
    guide_path=ROOT/'validation/gamefaqs-64050-source/guide-numbered.txt'
    guide={int(n):s for n,s in re.findall(r'^L(\d+): ?(.*)$',guide_path.read_text(encoding='utf-8'),re.M)}
    assert set(range(119,2790)).issubset(guide),'A source interval is missing'
    guide_screens={}
    for n,s in guide.items():
        if 1318<=n<2019:
            m=re.match(r'\s*([A-O](?:1[0-5]|[1-9]))\s*-',s)
            if m:guide_screens[m[1]]=n
    assert len(guide_screens)==225,(len(guide_screens),set(chr(65+x)+str(y) for x in range(15) for y in range(1,16))-set(guide_screens))
    doors=read('doors_reference.json');plain=read('plain_house_dialogue_reference.json')['contexts']
    conditional=read('conditional_house_reference.json');coverage=read('sms_npc_coverage_report.json')
    checklist=read('full_completion_checklist.json');assets=read('merchant_assets.json')
    csvfile('suivi_173_obligations.csv',[dict(
        id=c['id'],category=c['category'],
        context=json.dumps(c['context'],ensure_ascii=False,sort_keys=True),
        required_variants=' ; '.join(c['required_variants']),
        sms_status=c['sms_status'],md_status=c['md_status'],
        comparison_status=c['sms_md_comparison_status'],source=c['static_basis'])
        for c in checklist['cases']])
    gold=read('house_gold_reference.json')['records'];fairies=read('fairy_reference.json')['records']
    healer=crows('healer_data.c','healer_prices');paid=read('paid_passage_reference.json')['routes']
    rewards=read('item_rewards_reference.json')['records']
    types=rom[0x3234e:0x3334e];max_type=max(types);assert max_type==0x7c
    actor_rows=[]
    for t in range(0x20,max_type+1):
        off=0x320ea+(t-0x20)*4;hp,attack,defense,flags=rom[off:off+4]
        rooms=[n for n in range(512) if t in types[n*8:n*8+8]]
        actor_rows.append(dict(type_id=f'0x{t:02X}',health_raw=hp,attack_raw=attack,defense_raw=defense,
            initial_flags=f'0x{flags:02X}',stats_file_offset=f'0x{off:05X}',
            initial_room_count=len(rooms),initial_rooms=' '.join(f'0x{x:03X}' for x in rooms),
            note='Absence de la liste initiale ne signifie pas inutilisé : apparitions dynamiques possibles.'))
    csvfile('acteurs_statistiques_rom.csv',actor_rows)
    shop_rows=[]
    for outside,mode,param in assets['towns']:
        if mode==0:goods=' ; '.join(f'item {a}: {b} cornes' for a,b,_ in assets['goods'][param])
        elif mode==1:goods=f'pomme dorée : {param} cornes'
        else:goods=' ; '.join(f'+{rom[0x75ac+i]*8} points de magie : {rom[0x75af+i]} cornes' for i in range(3))
        shop_rows.append(dict(coordinate=coord(outside),room_id=f'0x{outside:02X}',mode=mode,
            category=['marchandises','pomme dorée','recharge magie'][mode],offers=goods,source='merchant_assets.json; ROM 75AC..75B1'))
    csvfile('commerces_rom.csv',shop_rows)
    csvfile('dons_et_prelevements_rom.csv',[dict(coordinate=coord(n),room_id=f'0x{n:02X}',amount_signed=signed(v),
        raw_byte=f'0x{v:02X}',once_flag='outside[room] & 2',source='house_gold_reference.json') for n,v in gold])
    csvfile('fees_rom.csv',[dict(coordinate=coord(n),room_id=f'0x{n:02X}',kind='vie' if k==1 else 'magie',
        capacity_gain_points=8,display_units=1,source='fairy_reference.json') for n,k in fairies])
    pnjs=[];seen={(v['outside'],v['room'],v['coordinate'],v['text_pc']) for v in coverage['visits']}
    for p in plain:
        off=0xc000+(p['text_pc']&0x3fff);end=rom.index(0,off)
        pnjs.append(dict(category='contexte ordinaire',coordinate=coord(p['outside']),outside_id=f'0x{p["outside"]:02X}',
            interior_id=f'0x{p["room"]:02X}',trigger_coordinate=f'0x{p["coordinate"]:04X}',variant='sélection courante',
            text_cpu=f'0x{p["text_pc"]:04X}',text_file_offset=f'0x{off:05X}',text_bytes=end-off,text_sha256=sha(rom[off:end+1]),
            sms_played_and_fixed_replayed=(p['outside'],p['room'],p['coordinate'],p['text_pc']) in seen))
    observed={}
    for f in (ROOT/'analysis').glob('sms-conditional-*.json'):
        b=json.loads(f.read_bytes())
        if b.get('passed'):
            for v in b['visits']:observed[(b['outside'],b['room'],v['coordinate'],v['text_pc'])]=True
    for i,(room,outside,position,handler) in enumerate(conditional['nodes']):
        ids=conditional['text_pcs'][i*2:i*2+2] if outside==0xce else conditional['text_pcs'][6:]
        labels=['avant cristal 9','après cristal 9'] if outside==0xce else ['prérequis absent','récompense 100','après récompense']
        for pc,label in zip(ids,labels):
            off=0xc000+(pc&0x3fff);end=rom.index(0,off)
            pnjs.append(dict(category='contexte conditionnel',coordinate=coord(outside),outside_id=f'0x{outside:02X}',
                interior_id=f'0x{room:02X}',trigger_coordinate=f'0x{position:04X}',variant=label,
                text_cpu=f'0x{pc:04X}',text_file_offset=f'0x{off:05X}',text_bytes=end-off,text_sha256=sha(rom[off:end+1]),
                sms_played_and_fixed_replayed=observed.get((outside,room,position,pc),False)))
    assert len(pnjs)==74
    csvfile('dialogues_ordinaires_et_conditionnels.csv',pnjs)
    towns={0x94:'Miliver',0xc7:'Saylun',0x55:'Kari-Kari',0x22:'Numibi',0x57:'Dagorald',0xf0:'Riskas',0x4c:'Sid',0x2e:'Eren',0xfe:'Aires',0xce:'Halls'}
    masters={0xe6:'Gillian / Foudre',0xa3:'Battler / Terre',0x2c:'Tyris / Feu',0xaa:'Linda / Eau'}
    outdoor=[];indoor=[]
    for room in range(512):
        ptr=int.from_bytes(world.arrays['world_room_index'][room*2:room*2+2],'little')
        cells=bytearray(160)
        if ptr!=65535:rle_planes(world.arrays['world_room_streams'],ptr,cells,0,1)
        actors=collections.Counter(types[room*8:room*8+8]);actors.pop(0,None)
        actor_string=' '.join(f'{n}x0x{t:02X}' for t,n in sorted(actors.items()))
        if room<256 and room>=16 and room&15!=15:
            local=[d for d in doors['direct_unconditional_doors'] if d['room']==room]
            dungeon=[d for d in doors['direct_unconditional_dungeon_doors'] if d['room']==room]
            shops=[x for x in shop_rows if x['room_id']==f'0x{room:02X}']
            outdoor.append(dict(coordinate=coord(room),room_id=f'0x{room:02X}',village=towns.get(room,''),
                guide_line=guide_screens[coord(room)],direct_doors=len(local),
                door_targets=' '.join(f'0x{x["target"]:02X}@{x["x"]},{x["y"]}' for x in local),
                dungeon=' '.join(str(d['index']) for d in dungeon),teacher=masters.get(room,''),
                ordinary_contexts=sum(c['outside']==room for c in plain),
                conditional_contexts=sum(c[1]==room for c in conditional['nodes']),
                merchant_mode=shops[0]['category'] if shops else '',
                healer_price=next((price for n,price in healer if n==room),''),
                gold_amount=next((signed(v) for n,v in gold if n==room),''),
                fairy=next(('vie' if kind==1 else 'magie' for n,kind in fairies if n==room),''),
                paid_destination=next((coord(d) for n,d,y,x in paid if n==room),''),
                actors_initial=actor_string,cells_sha256=sha(cells),
                source='ROM et tables extraites ; ligne FAQ = index de comparaison, pas preuve de visite'))
        else:
            items=[r for r in rewards if r['room']==room]
            indoor.append(dict(room_id=f'0x{room:03X}',class_name='labyrinthe' if room>=256 else 'intérieur',
                map_index_present=ptr!=65535,map_stream_index=f'0x{ptr:04X}',
                room_script=f'0x{int.from_bytes(rom[0xb762+room*2:0xb764+room*2],"little"):04X}',
                actors_initial=actor_string,item_records=len(items),
                item_inventory_slots=' '.join(str(r.get('inventory_offset','')) for r in items),
                cells_sha256=sha(cells) if ptr!=65535 else '',note='Identifiant interne ; présence statique ne prouve pas accessibilité.'))
    assert len(outdoor)==225 and len(indoor)==287
    csvfile('monde_225_ecrans.csv',outdoor);csvfile('interieurs_287_identifiants.csv',indoor)
    bossrooms=[0x175,0x144,0x1c3,0x180,0x163,0x115,0x179,0x196,0x1ac,0x14c]
    items=['Hache de combat','Torche','Corde magique','Canoë','Bottes rapides','Cloche de glace','Bateau','Clé du voleur','Ballon magique','Hache d’or']
    labs=[]
    for n in range(1,11):
        door=next(d for d in doors['direct_unconditional_dungeon_doors'] if d['index']==n)
        br=bossrooms[n-1];bt=next(t for t in types[br*8:br*8+8] if 0x63<=t<=0x6d)
        off=0x320ea+(bt-0x20)*4
        labs.append(dict(number=n,coordinate=coord(door['room']),entrance_id=f'0x{door["target"]:03X}',
            major_reward=items[n-1],boss_room=f'0x{br:03X}',boss_type=f'0x{bt:02X}',
            boss_health_raw=rom[off],boss_attack_raw=rom[off+1],boss_defense_raw=rom[off+2],
            outcome='cristal '+str(n) if n<10 else 'fin du jeu',source='doors_reference.json ; actor table ROM 3234E / stats 320EA'))
    csvfile('labyrinthes_et_boss_rom.csv',labs)
    # The guide's room numbering is local to its diagrams, not the SMS room ID.
    roman=['I','II','III','IV','V','VI','VII','VIII','IX','X'];diagram_labels=[]
    for numeral in roman:
        start=next(n for n in sorted(guide) if n>2020 and guide[n].strip()=='Labyrinth '+numeral)
        ascii_lines=[]
        for n in range(start+1,start+60):
            s=guide[n]
            if ascii_lines and re.search(r'[a-zA-Z]{4}',s) and 'n/a' not in s:break
            if '|' in s:ascii_lines.append(s)
        labels=[int(x) for s in ascii_lines for x in re.findall(r'(?<!\w)\d+',s)]
        diagram_labels.append(dict(labyrinth=numeral,guide_line=start,largest_local_label=max(labels)))
    village_rows=[]
    for room,name in towns.items():
        village_rows.append([name,coord(room),f'0x{room:02X}',sum(p['outside']==room for p in plain),sum(p[1]==room for p in conditional['nodes']),next((price for n,price in healer if n==room),'—')])
    meta=dict(report_date=DATE,guide=dict(url=URL,author='Andrew Light / lighty691',version='1.00',date='2012-04-07',
        numbered_source_sha256=sha(guide_path.read_bytes()),cached_lines=len(guide),world_entries=len(guide_screens),diagrams=diagram_labels),
        rom_sha256=sha(rom),rom_bytes=len(rom),git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        counts=dict(world_screens=225,interior_id_slots=287,actor_statistics=len(actor_rows),shops=len(shop_rows),
            ordinary_contexts=len(plain),conditional_variants=9,ordinary_played=coverage['observed_acknowledged_conversations'],
            conditional_played=sum(p['sms_played_and_fixed_replayed'] for p in pnjs if p['category']=='contexte conditionnel'),
            known_obligations=len(checklist['cases'])),all_npcs_complete=False,all_side_quests_complete=False)
    meta['git_head_role']='Base de travail ; des données de validation locales plus récentes sont incluses dans ce rapport.'
    source_names=['doors_reference.json','plain_house_dialogue_reference.json',
        'conditional_house_reference.json','sms_npc_coverage_report.json',
        'full_completion_checklist.json','merchant_assets.json',
        'house_gold_reference.json','fairy_reference.json',
        'paid_passage_reference.json','item_rewards_reference.json']
    meta['input_sha256']={'analysis/'+n:sha((ROOT/'analysis'/n).read_bytes()) for n in source_names}
    (OUT/'references_et_perimetre.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    report=INTRO+table(['Village','Repère','ID SMS','Contextes ordinaires','Contextes conditionnels','Auberge (cornes)'],village_rows)+VILLAGES_END
    report+=table(['No','Entrée','Objet majeur','Boss : ID / salle','PV / attaque / défense bruts'],
        [[l['number'],l['coordinate'],l['major_reward'],l['boss_type']+' / '+l['boss_room'],f'{l["boss_health_raw"]} / {l["boss_attack_raw"]} / {l["boss_defense_raw"]}'] for l in labs])
    report+=DUNGEONS_END
    report+=table(['Catégorie de suivi','Entrées initiales'],list(checklist['category_counts'].items()))
    report+=ENDING.format(ordinary=coverage['observed_acknowledged_conversations'],conditional=meta['counts']['conditional_played'],sha=sha(rom),size=len(rom))
    (OUT/'RAPPORT_COMPLET_JEU.md').write_text(report,encoding='utf-8')
    manifest={p.name:dict(bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in OUT.iterdir() if p.is_file() and p.name!='manifest.json'}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    archive=ROOT/'handoff'/('gaw-rapport-jeu-'+DATE+'.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(OUT.iterdir()):
            if p.is_file():z.write(p,'rapport-jeu/'+p.name)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for name,v in manifest.items():assert sha(z.read('rapport-jeu/'+name))==v['sha256']
    archive.with_suffix('.zip.sha256').write_text(sha(archive.read_bytes())+'  '+archive.name+'\n')
    print(json.dumps(dict(report=str(OUT/'RAPPORT_COMPLET_JEU.md'),archive=str(archive),counts=meta['counts']),ensure_ascii=False))


INTRO='''# Golden Axe Warrior — dossier de référence du jeu

Date : 11 novembre 2026. Périmètre : la ROM Master System fournie et le projet de portage Mega Drive. Ce dossier décrit le jeu et ses obligations de validation ; il ne certifie pas un parcours 100 % achevé.

## 1. Sources et méthode

Le [guide d’Andrew Light, lighty691, version 1.00 du 7 avril 2012](https://gamefaqs.gamespot.com/sms/588075-golden-axe-warrior/faqs/64050) a été consulté en entier. Il organise l’information en objets, villages, ennemis, carte extérieure et dix labyrinthes. Ses 225 repères servent à indexer notre inventaire. Sa description d’un trajet ne constitue pas une preuve d’exécution de notre ROM ni du portage.

Les données chiffrées et catalogues de ce dossier sont recalculés depuis la ROM fournie et les tables du projet. Les explications techniques sont notre analyse des routines et des captures, distincte du texte du guide. Les dialogues anglais, les plans ASCII et le parcours rédigé de l’auteur ne sont pas reproduits. La copie de travail du guide reste dans le cache local de validation.

Trois niveaux de preuve sont utilisés : **extrait** = donnée statique de la ROM ; **modèle** = règle lisible dans la traduction C, à confirmer selon le cas ; **joué et rejoué** = interaction observée puis reproduite avec les mêmes entrées et un contrôle de la RAM/image finales. La présence d’un objet dans une table ne prouve pas qu’il a été obtenu.

## 2. Structure de l’aventure

Le héros part d’un cimetière proche du premier village. L’objectif central consiste à reprendre neuf cristaux, accéder au palais, récupérer la Hache d’or et vaincre Death Adder. Le dénouement comprend une scène de réunion des cristaux, le texte final, le générique et le retour à l’introduction.

Le jeu combine exploration, combats en temps réel, indices de PNJ et ouvertures de terrain. La progression repose autant sur les outils que sur les cristaux : arbre à couper, rocher à briser, mur à gravir, rivière à traverser, bateau à embarquer et passage à payer sont des obstacles différents. Les allers-retours sont normaux : certains équipements ou enseignements ne sont proposés qu’après un seuil de progression.

La carte extérieure contient **15 × 15 = 225 écrans**. Les colonnes sont A–O et les lignes 1–15. Un identifiant SMS extérieur s’écrit `0xYX` : X détermine la colonne, Y la ligne. Par exemple `0x94` = E9 et `0x3E` = O3. Un repère du guide, une salle numérotée par l’auteur et un identifiant mémoire sont trois références différentes.

Le fichier [monde_225_ecrans.csv](monde_225_ecrans.csv) donne pour chaque écran les portes, PNJ connus, services, acteurs initiaux et références. Le fichier [interieurs_287_identifiants.csv](interieurs_287_identifiants.csv) couvre les emplacements d’identifiants d’intérieurs et de labyrinthes, y compris les emplacements non utilisés. **287 identifiants ne signifient pas 287 pièces accessibles.**

## 3. Commandes, inventaire et interface

La croix dirige le héros ; un bouton ouvre l’inventaire, l’autre utilise l’équipement sélectionné. L’action dépend donc de la sélection : arme, sort, objet de soin ou outil. Le déplacement, l’orientation et l’état du héros interviennent dans les collisions et les interactions.

L’inventaire stocke 17 emplacements principaux : épée, hache, huile, torche, quatre magies, pomme, plume, cloche, ballon, canoë, corde, bottes, clé du voleur et bateau. L’armure et le bouclier ont leurs propres niveaux. Les améliorations remplacent les versions inférieures ; le bateau, le canoë et plusieurs outils modifient aussi les possibilités de déplacement.

Le HUD associe l’objet choisi, la vie, la magie, les cornes et les clés. Dans les données du projet, **8 points correspondent à une unité de jauge**. La vie et la magie commencent chacune à 24 points, soit trois unités. Les limites sont de 128 points, soit seize unités. Les cornes sont enregistrées sur un octet ; les opérations d’achat et de don doivent respecter les plafonds et les limites propres à chaque objet.

## 4. Armes et protections

| Famille | Progression | Fonction à contrôler |
| --- | --- | --- |
| Épées | courte → longue → de feu | Portée, dégâts, animation, remplacement de l’ancienne version |
| Haches | de combat → d’or | Combat et coupe des végétaux ; usage obligatoire de l’or contre le dernier adversaire |
| Armures | cotte de mailles → plates → dragon | Réduction des dégâts et palette ; effet de la corrosion séparé du niveau possédé |
| Boucliers | petit → chevalier → dragon | Réflexion/arrêt des projectiles suivant le niveau et l’orientation |

Le bouclier de chevalier figure à 250 cornes dans la table marchande correspondante. La longue épée est liée au donneur d’A5 et à un seuil de vie ; l’armure de plates est donnée en H2, celle du dragon en B11 et l’épée de feu en K6. Le bouclier du dragon relève de la maison M4 et du sixième cristal. Ces conditions ne sont pas interchangeables : une arme améliore l’attaque, un bouclier ne protège pas nécessairement de tous les contacts corporels.

Les valeurs d’attaque et de défense brutes ne sont pas directement des nombres de coups. Défense de la cible, phase vulnérable, projectiles, charge et animation interviennent. Le catalogue des acteurs conserve les valeurs d’origine sans transformer une observation ponctuelle en règle universelle.

## 5. Objets, outils et consommables

| Élément | Fonction dans le modèle du jeu | Point de vigilance |
| --- | --- | --- |
| Huile magique | Annule la corrosion/malédiction de l’armure | **Ce n’est pas une recharge de magie** ; consommation conditionnelle |
| Torche | Éclaire les pièces obscures | Retour dans une pièce, état des lampes et restauration des palettes |
| Pomme dorée | Remplit la vie | Conservée si la vie est déjà pleine ; ne remplit pas la magie |
| Plume magique | Retour au dernier lieu de sauvegarde | Usage extérieur et point de destination ; distinct de Continue |
| Cloche de glace | Gèle la lave et modifie/révèle des éléments de terrain | Certaines ouvertures persistantes demandent ensuite une action ou un sort |
| Ballon magique | Affiche une carte plus détaillée | Objet d’observation, pas un moyen de transport libre |
| Canoë | Autorise certains passages d’eau | Ne donne pas l’accès maritime du bateau |
| Corde | Permet des ascensions aux endroits appropriés | Alignement, changement d’écran et conservation du terrain de corde |
| Bottes | Accélèrent le déplacement | Collisions, pas complets et cadence d’animation doivent rester cohérents |
| Bateau | Navigation depuis les embarcadères, avec attaque spécifique | Possession et position d’embarquement sont deux conditions différentes |
| Clé du voleur | Ouvre les portes verrouillées sans dépenser de clé ordinaire | N’ouvre pas automatiquement les portes de combat ou les mécanismes |
| Clés ordinaires | Déverrouillage avant la clé permanente | Achat, consommation, plafond et état de la porte |
| Cristaux | Progression principale et gain de capacité de vie | Neuf drapeaux distincts et conditions d’accès au palais |
| Nourriture et pots au sol | Récupération après apparition/ramassage | Quantités, plafonds, durée de présence et son de prise |

Les pièces d’argent du jeu sont des **cornes**, pas une monnaie extérieure au jeu. La table de dons comporte des montants positifs et négatifs ; il ne faut pas confondre un don, une taxe, le prix d’un service et un butin d’ennemi.

## 6. Les quatre magies et leurs maîtres

Les règles ci-dessous sont celles du modèle de sélection dérivé des routines SMS ; les seuils restent identifiés même lorsqu’une variante n’a pas encore été jouée dans notre parcours.

| Magie | Maître et repère | Obtention/amélioration | Coût d’usage courant |
| --- | --- | --- | --- |
| Foudre | Gillian, G14 | Introduction puis pomme dorée ; niveau 2 gratuit à 72 points de vie maximale | 8 points ; gestion de la charge à contrôler |
| Terre | Battler, D10 | Niveau 1 : 50 cornes ; niveau 2 : 100 cornes et 72 points de vie maximale | 8 points |
| Feu | Tyris, M2 | Premier enseignement à 72 points de vie maximale ; second après les neuf cristaux | 32 points |
| Eau | Linda, K10 | Premier enseignement ; retour avec un autre message | 24 points |

Les niveaux cibles sont **2 / 2 / 2 / 1**. La routine examinée ne donne pas un deuxième niveau d’Eau. Terre sert aux obstacles et à l’immobilisation ; Feu est un effet de zone ; Eau restaure la vie. Le modèle de soin d’Eau ajoute 16 ou 32 points selon le contexte de terrain : son application précise doit être contrôlée en situation, pas remplacée par une description approximative.

### Une conséquence importante de l’ordre des récompenses

Une première magie apprise tente d’ajouter 24 à la capacité de magie, mais la routine ne conserve le nouveau total que s’il est **strictement inférieur à 128**. Les fées ajoutent 8 en plafonnant à 128. Prendre toutes les fées de magie avant les derniers enseignements peut donc laisser une jauge finale plus basse.

Exemple recalculé : avec Foudre et Terre apprises, la capacité peut être de 72. Quatre fées l’amènent à 104 ; un enseignement de 24 donnerait 128, rejeté par le test strict, et les enseignements suivants ne compensent plus cette limite. Une route visant toutes les capacités doit réserver des récompenses appropriées pour la fin. Cette remarque vient du code analysé, pas d’une simple estimation de progression.

## 7. Villages et personnages

Les noms sont conservés comme repères communs avec la FAQ. Les comptes ci-dessous sont ceux de nos tables : ils incluent des contextes d’interaction, qui ne sont pas tous des personnages vivants distincts. Les vendeurs, soigneurs et sauvegardes sont comptés séparément.

'''

VILLAGES_END='''
Les habitants donnent des indications géographiques, des informations sur les équipements, des éléments de récit et parfois des récompenses. Une maison peut réunir plusieurs interlocuteurs et plusieurs services. Des pièces sans habitants peuvent néanmoins contenir une interaction ou un accès derrière la cheminée.

Le [catalogue des dialogues](dialogues_ordinaires_et_conditionnels.csv) identifie 65 contextes ordinaires et neuf variantes pour quatre contextes conditionnels. Il fournit les adresses du texte et leur empreinte, sans confondre une adresse de retour du formateur avec le début d’une phrase affichée.

## 8. Économie et services

### Récompenses annexes et conditions locales

Les conditions suivantes proviennent du répartiteur de quêtes traduit dans `house_quest.inc`. Elles précisent les récompenses facultatives ; l'accès géographique à la maison peut demander d'autres outils.

| Repère | Récompense | Condition locale du modèle |
| --- | --- | --- |
| J9 | Pomme dorée | Foudre connue et aucune pomme portée |
| A5 | Épée longue | Foudre connue, vie maximale ≥ 56 et épée actuelle inférieure au niveau 2 |
| H2 | Armure de plates | Foudre connue et armure inférieure au niveau 2 |
| B11 | Armure du dragon | Foudre connue et armure inférieure au niveau 3 |
| K6 | Épée de feu | Foudre connue ; vérifier le drapeau local de remise et la revisite |
| M4 | Bouclier du dragon | Sixième cristal obtenu ; donneur et interlocuteur d'indice séparés |
| H12 | Pomme dorée | Aucune pomme portée, dans la pièce arrière concernée |
| F5 | Huile magique | Aucune huile portée, dans la pièce arrière concernée |

Les cinq maisons J9/A5/H2/B11/K6 associent chacune un donneur et un interlocuteur d'indice distincts. Obtenir l'objet ne couvre donc pas les dix interactions. Pour chaque chaîne : parler avant le prérequis, obtenir la récompense par les commandes du jeu, acquitter le message, sortir puis revenir. Pour un consommable, tester aussi son absence et sa présence sans présumer qu'une revisite accorde toujours un nouveau don.

L'échange de la pomme avec Gillian relie une récompense annexe à un enseignement ; il faut conserver la différence entre posséder la pomme, la remettre et connaître déjà Foudre. Les fées, les équipements, les enseignements avancés et les indices de terrain constituent des chaînes séparées. Le [suivi des 173 obligations](suivi_173_obligations.csv) conserve les préconditions et les variantes attendues, avec leur état SMS et MD ; il reste un inventaire de travail, pas une preuve d'exhaustivité définitive.

La table marchande comprend **23 lieux** : 14 marchands de marchandises, cinq vendeurs de pommes et quatre points de recharge magique. Le [catalogue marchand](commerces_rom.csv) détaille chaque offre et son prix.

Une recharge magique propose +16, +32 ou +64 points pour 20, 30 ou 50 cornes. La vente est limitée par la capacité disponible. L’huile vendue dans d’autres boutiques répare l’armure : la distinction est indispensable pour planifier une exploration sans magie.

Les onze lieux de soin recensés comprennent cinq soins gratuits et six payants à 20 ou 40 cornes. Une nuit restaure la vie et préserve la magie dans le modèle étudié. Il faut tester l’acceptation, le refus, l’argent insuffisant et le cas où la vie est déjà pleine.

Les six extrémités des passages payants forment trois liaisons : **K1–M3, G3–H8 et N6–G9**, à 10 cornes par trajet. Le repère d’arrivée et les coordonnées de dépôt comptent : posséder le bateau ne garantit pas qu’un chemin statique trouve toutes les traversées possibles.

Le [catalogue des dons/prélèvements](dons_et_prelevements_rom.csv) comporte 33 lignes : 19 positives et 14 négatives. Ces lignes sont des sélections de table, pas une preuve de 33 visites. Une récompense conditionnelle supplémentaire de 100 cornes existe à Numibi après le prérequis de progression ; sa revisite n’accorde pas une nouvelle récompense.

Le jeu de hasard a quatre accès extérieurs identifiés : D1, M5, H10 et O13. L’entrée coûte 10 cornes ; les résultats dépendent du tirage et peuvent faire gagner ou perdre de la monnaie. Il faut distinguer mise, résultat brut, solde final, plafonnement et proposition de rejouer. Ce système nécessite des preuves propres ; une partie gagnée ne couvre pas toutes ses branches.

## 9. Fées et capacités maximales

Quatre récompenses augmentent la vie : **I1, N1, C8, J12**. Quatre augmentent la magie : **C3, A12, F14, M14**. Chaque gain vaut 8 points, soit une unité de jauge. Les emplacements, types et valeurs sont dans [fees_rom.csv](fees_rom.csv).

La vie maximale théorique s’obtient par 24 points initiaux + 72 pour les neuf cristaux + 32 pour les quatre gains de vie = **128**. Ce calcul ne prouve pas l’obtention des récompenses dans notre partie. Pour la magie, appliquer la véritable règle des enseignements et le plafond des fées, plutôt que d’additionner sans condition toutes les récompenses.

Chaque fée doit être contrôlée lors de l’obtention et lors d’un retour : drapeau persistant, absence de double gain, mise à jour du HUD et conservation des autres ressources. Les objets de progression et les récompenses de capacité ne doivent pas être introduits par une sauvegarde de test dans le parcours de preuve.

## 10. Combats et bestiaire

La FAQ sépare 16 familles extérieures et 14 familles de labyrinthes. Les regroupements visuels ne correspondent pas directement aux types internes. Notre catalogue [acteurs_statistiques_rom.csv](acteurs_statistiques_rom.csv) conserve **93 enregistrements statistiques, types 0x20–0x7C**, avec PV, attaque, défense, drapeaux et apparitions initiales. Des projectiles, effets ou acteurs invoqués partagent cet espace : ce ne sont pas 93 espèces d’ennemis.

| Ensemble visuel | Comportements à vérifier dans le portage |
| --- | --- |
| Créatures gélatineuses, ogres, scorpions | Variantes de couleur, division éventuelle, poursuite, portée et projectiles |
| Rebondisseurs, vers, fouisseurs | Sauts, accélérations, apparition de trous et collisions pendant l’animation |
| Tornades et créatures intermittentes | Périodes de vulnérabilité, exposition du point faible, durée des états |
| Chevaliers et géants | Orientation, cadence des tirs/lancers, contact et protection par le bouclier |
| Arbres animés, créatures de neige et de feu | Déclenchement, attaques persistantes, interactions avec la cloche |
| Créatures marines | Apparition, trajectoires, embarquement et attaque spécifique du bateau |
| Squelettes, trolls et chauves-souris | Déplacement, obstacles, charge et réaction aux coups |
| Feux, esprits, fantômes et mages | Téléportation, apparition, duplication, activation par la position du héros |
| Coquilles et yeux | Faces vulnérables, lignes de tir, sens d’attaque et états fermés |
| Voleurs et ennemis corrosifs | Argent retiré, capture/libération, corrosion et remède |
| Briques animées et faux coffres | Réveil, camouflage, ouverture de pièce et distinction du vrai trésor |

Les pièges au sol, flèches et dangers persistants demandent une vérification séparée des ennemis tuables. Une salle peut autoriser un mécanisme sans qu’il soit nécessaire de supprimer tous les dangers. Les ennemis quittant l’écran pendant un changement de carte ne doivent pas être assimilés à ceux de la nouvelle salle.

## 11. Les dix labyrinthes

Les entrées, objets majeurs et caractéristiques ci-dessous sont recoupés avec les tables de la ROM. Les PV/attaque/défense sont des **octets internes**, pas une prédiction du nombre de coups à porter. La numérotation locale des plans de l’auteur n’est pas celle de la RAM SMS.

'''

DUNGEONS_END='''
Le [tableau technique des labyrinthes](labyrinthes_et_boss_rom.csv) contient les identifiants d’entrée et les salles des adversaires finaux. Les labyrinthes tardifs ajoutent des combats intermédiaires ; le seul adversaire du tableau ne résume donc pas tous les combats d’une zone.

La progression alterne quatre types de portes : accès payant en clé, ouverture après combat, mécanisme mural et transformation par sort. Les téléporteurs et ponts ajoutent des connexions qui ne sont pas de simples voisinages sur une grille. Une route correcte doit distinguer la visite d’une salle, la récupération de son objet et la résolution d’un mécanisme ouvrant une autre salle.

Le cinquième cristal déclenche un changement extérieur important. Le canoë, le bateau et la cloche élargissent ensuite les parcours possibles. Après les neuf cristaux, le retour auprès de Tyris et l’accès au palais constituent encore des étapes distinctes. Le neuvième adversaire n’est pas le combat final de l’aventure.

Dans le palais, la Hache d’or doit être réellement obtenue avant le dernier combat. Les gardiens intermédiaires et Death Adder ont leurs propres phases de vulnérabilité et de récupération. Le test d’un boss doit couvrir ses projectiles ou satellites, les dégâts réels, sa défaite, l’octroi de récompense et la transition qui suit.

## 12. Sauvegarde, mort et reprise

La structure de sauvegarde source examinée occupe 592 octets et le service propose trois emplacements. Le dernier emplacement choisi et le lieu de reprise sont des informations distinctes. Mort/Continue, sauvegarde manuelle, retour par plume et nouvelle partie ne doivent pas être fusionnés en un comportement unique.

Pour valider ce système : contrôler annulation, sélection des trois emplacements, écrasement, nom, inventaire, cristaux, argent, état des récompenses et lieu exact de réapparition. Les fichiers de test qui importent volontairement un état sont utiles pour diagnostiquer un cas, mais ne constituent pas une preuve de parcours continu.

## 13. Texte, images, animation et audio

Les textes couvrent récit initial, indications, choix, commerce, refus, récompenses, descriptions d’objets, messages conditionnels, mort et épilogue. Pour chacun, vérifier déclencheur, pages, nombres insérés, acquittement, conservation de l’état et restauration de la scène.

Les graphismes à comparer comprennent introduction, cape, logo, villages, cavernes, labyrinthes, HUD, inventaire, portraits, sorts plein écran et crédits. Une capture finale correcte ne suffit pas : un mauvais ordre de chargement peut encore produire une image parasite pendant une transition.

Pour l’animation, relever séparément durée des poses, déplacement réel, invulnérabilité, émergence des monstres, scrolling et ouverture des fenêtres. PAL et NTSC sont deux campagnes de validation ; un résultat NTSC ne certifie pas le même comportement en PAL.

La partie sonore comporte musiques, bruitages, priorités et interruptions. L’ouverture d’un dialogue, une commande de menu, un achat, un sort, une porte et la mort d’un ennemi peuvent chacun émettre un événement différent. Contrôler la commande demandée, le flux PSG et le son capturé. Un fichier vidéo sans erreur de décodage prouve l’intégrité du fichier, pas une équivalence musicale SMS/MD.

## 14. Ce que « 100 % » doit signifier pour ce projet

Le parcours principal terminé, l’inventaire final, toutes les récompenses facultatives et l’ensemble des interactions sont des objectifs différents. Pour répondre à la demande du projet, il faut couvrir les PNJ et services, les quêtes secondaires et leurs états pertinents, puis conserver les preuves. Les choix incompatibles peuvent nécessiter des branches explicites.

Le tableau suivant représente les obligations initiales de notre suivi. Une ligne « audit » peut recouvrir plusieurs lieux ou plusieurs résultats ; le total ne doit pas servir de dénominateur pour un pourcentage de finition.

'''

ENDING='''
### État des preuves au moment du rapport

- Campagne SMS jusqu’au générique : terminée et rejouée ; neuf cristaux et Hache d’or obtenus, Death Adder vaincu.
- Contextes ordinaires : **{ordinary}/65** joués et rejoués ; O3 reste à atteindre dans le relevé actuel.
- Contextes conditionnels sélectionnés : **{conditional}/9 variantes**, correspondant à quatre contextes, jouées et rejouées.
- Ensemble des PNJ et quêtes secondaires : **pas encore certifié complet**.
- Portage Mega Drive et vérification globale PAL/NTSC : ne se déduisent pas de ces résultats SMS.

La vidéo longue de la campagne et l’annexe des neuf variantes conditionnelles restent explicitement partielles pour l’objectif global. Elles ne sont pas présentées comme une vidéo 100 %.

### Points à résoudre avant une certification

1. Finir le contexte O3 et vérifier les accès réels plutôt que la seule proposition de trajet.
2. Terminer les enseignements et récompenses de capacité dans un ordre compatible avec les jauges maximales.
3. Visiter tous les vendeurs, soins, sauvegardes, passages et jeux ; couvrir les refus et retours pertinents.
4. Vérifier les récompenses d’équipement, les indices associés, les accès derrière les cheminées et la corrosion/remède.
5. Réconcilier les textes signalés aux offsets SMS `0xDA58`, `0xDA7C`, `0xED3C`. Ils restent non déclenchés dans les preuves retenues ; cela ne suffit pas à les déclarer inutilisés.
6. Rejouer le parcours final retenu et enregistrer la vidéo correspondante, avec les branches annexes identifiées.
7. Reproduire les conditions sur Mega Drive et comparer textes, images intermédiaires, animation, collisions, sons et cadence régionale.

## 15. Fichiers livrés et limites

- `monde_225_ecrans.csv` : inventaire extérieur calculé depuis la ROM, avec renvoi à chaque entrée du guide.
- `interieurs_287_identifiants.csv` : espace des identifiants internes, présence des cartes et acteurs initiaux.
- `acteurs_statistiques_rom.csv` : statistiques brutes ; les apparitions dynamiques ne sont pas assimilées aux listes initiales.
- `dialogues_ordinaires_et_conditionnels.csv` : 74 sélections connues, adresses, tailles, empreintes et état de visite.
- `commerces_rom.csv`, `dons_et_prelevements_rom.csv`, `fees_rom.csv` : économie et récompenses.
- `labyrinthes_et_boss_rom.csv` : entrées, objets majeurs, salles et statistiques des adversaires principaux.
- `suivi_173_obligations.csv` : interactions, préconditions, variantes et états de validation SMS/MD recensés.
- `references_et_perimetre.json`, `manifest.json` : périmètre, provenance et intégrité des fichiers.

Des relevés historiques du projet contiennent encore des champs tels que `implemented: false`. Ils décrivent parfois une ancienne étape et ne doivent pas remplacer l’examen du code actuel ni les rapports de relecture récents. Inversement, une fonction présente dans le code ne prouve pas que toutes ses conditions ont été testées.

ROM examinée : {size} octets ; SHA-256 `{sha}`.

Sources techniques du projet : `analysis/doors_reference.json`, `plain_house_dialogue_reference.json`, `conditional_house_reference.json`, `house_gold_reference.json`, `fairy_reference.json`, `merchant_assets.json`, `item_rewards_reference.json`, `full_completion_checklist.json`, `sms_npc_coverage_report.json` ; code `megadrive/src/source_spell_teacher.c`, `house_quest.inc`, `merchant.inc`, `healer.inc`, `minigame.inc`, `save.inc`, `main.c`, `actors.c`. Les CSV indiquent les offsets utiles quand ils sont déterminés.

Ce dossier constitue une base de spécification et d’audit du jeu, avec un inventaire reproductible. La clôture de chaque test reste fondée sur ses propres preuves.
'''


if __name__=='__main__':main()
