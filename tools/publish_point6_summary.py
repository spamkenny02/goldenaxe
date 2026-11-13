"""Publish the point 6 delivery description only after every release gate passed."""
import json
from pathlib import Path
from run_core import ROOT

def main():
 release=json.loads((ROOT/'analysis/rc1_release_report.json').read_bytes());assert release['passed']
 md=json.loads((ROOT/'analysis/md_proof_montage_report.json').read_bytes());sms=json.loads((ROOT/'analysis/sms_proof_montage_report.json').read_bytes());goals=json.loads((ROOT/'analysis/md_selected_gameplay_goal_closure.json').read_bytes());assert md['passed'] and sms['passed'] and goals['passed']
 def duration(s):
  h,s=divmod(round(s),3600);m,s=divmod(s,60);return f'{h} h {m:02} min {s:02} s'
 timing=ROOT/'analysis/md_montage_timestamp_repair.json'
 if timing.exists():
  t=json.loads(timing.read_bytes());bound=json.loads((ROOT/'analysis/md_montage_boundary_pixels_report.json').read_bytes());assert md['packet_timestamps_normalized_to_native_fps'] and bound['passed'] and bound['movie_sha256']==md['movie_sha256']
  t.update(passed=True,status='repaired_full_av_decode_and_all_segment_boundaries_exact',movie_sha256=md['movie_sha256'],full_audio_video_decoded=True,boundary_report='analysis/md_montage_boundary_pixels_report.json');timing.write_bytes((json.dumps(t,indent=2)+'\n').encode())
 folder=ROOT/'reports/gaw-v0322-rc1-2026-11-13'
 text=f"""# Point 6 — parcours retenu et vidéos livrés

La V322 devient RC1 pour essais externes sur le parcours sélectionné. Le binaire
reste identique : SHA-256 `{release['md_sha256']}`, 2048 Kio, checksum ECB3.
Le statut RC qualifie les preuves ci-dessous ; il ne certifie pas une fidélité
globale 100 % ni l'absence de tout bogue.

## Parcours effectivement rejoués

- Campagnes MD NTSC et PAL depuis Nouvelle partie jusqu'à la fin et au générique :
  neuf cristaux, Hache d'or, Death Adder, zéro mort et zéro protection pendant
  le combat des boss. La protection autorisée des approches reste déclarée.
- Les 145 objectifs de service/équipement retenus sur SMS ont un résultat MD joué,
  un rejeu indépendant et une vidéo décodée. Les valeurs de progression, de vie,
  de magie et d'argent ne sont pas forcément identiques entre les deux parcours.
- 65 conversations ordinaires connues dans 41 maisons ; 48 refus de service ; 31
  maisons d'argent avec retour sans seconde récompense ; 11 lieux de soin ; 14
  lieux de sauvegarde avec véritable Continuer ; six directions de transport,
  leurs refus et retours ; quatre hôtes de jeu avec gains, pertes, carte chanceuse
  et malchanceuse ; équipements, cheminées, prérequis, indices et corrosion/remède.
- Enseignements 2/2/2/1, capacités 128/128, huit contextes de fées et les retours
  retenus chez les enseignants et fées. Les récompenses sont obtenues dans le jeu.
- Trois emplacements réellement écrits et rechargés, avec écrasement au lieu 2E.
  La limite de 99 clés utilise une branche monétaire assistée clairement annoncée,
  sans injection d'objet, de vie ni de quête. Les autres achats retenus utilisent
  l'argent réellement obtenu.

## Vidéos locales et chapitres

- MD NTSC : `{Path(md['movie']).name}` — {duration(md['duration_seconds'])},
  {md['branch_title_cards']} annexes annoncées ; SHA-256 `{md['movie_sha256']}`.
  Dossier : `videos/md/parcours-et-annexes-2026-11-13/`.
- SMS : `{Path(sms['movie']).name}` — {duration(sms['duration_seconds'])},
  campagne et annexes retenues ; SHA-256 `{sms['movie_sha256']}`.
  Dossier : `videos/sms/parcours-et-annexes-2026-11-12/`.

Chaque dossier contient `LISEZ-MOI-ET-CHAPITRES.txt`. Les vidéos restent locales,
prêtes pour l'envoi manuel demandé. Les MP4 ne sont pas intégrés à Git.
Les annexes sont des branches distinctes : elles ne sont pas présentées comme
une unique partie continue. Décodage intégral audio/vidéo, nombre d'images,
synchronisation et pixels des frontières de chaque segment vérifiés.

## Portée et limites conservées

Le registre technique conserve 409 enregistrements SMS : il contient des étapes
intermédiaires de contrôleur, des alias et des sous-parcours. Il n'est ni un
compteur de PNJ, ni une liste de 409 objectifs de jeu indépendants. Le nouveau
rapprochement vérifie les 145 objectifs sélectionnés avec des prédicats explicites,
plus les cohortes connues. Il ne transforme pas les étapes techniques non
appariées en preuves réussies. Les écarts de précondition sont indiqués dans
le rapport, notamment le soin testé à vie pleine dans certains lieux, complété
par des soins payants réels sur héros blessé.

Les textes SMS 0xDA58/0xDA7C/0xED3C restent sans déclenchement légitime démontré :
ils ne sont pas déclarés inutilisés. Deux entrées de la table monétaire n'ont
pas d'accès démontré. Le texte de Saylun avec pomme possédée correspond au texte
SMS complet au retour du formateur ; l'attente finale SMS duplique ensuite un
suffixe et son image finale ne correspond pas à l'image MD.
Des différences de raster/fondu du titre demeurent. Les preuves PAL/NTSC
complètes concernent MD ; la vidéo SMS retenue est NTSC. Aucun parcours sur
console physique ou BizHawk ne fait partie de cette qualification, et aucun
test n'affirme des formes d'onde PCM identiques ou une couverture exhaustive
de toutes les permutations de monstres, PNJ et quêtes.

## Preuves reproductibles

- [Publication RC](../../analysis/rc1_release_report.json)
- [145 objectifs et différences de contexte](../../analysis/md_selected_gameplay_goal_closure.json)
- [Registre technique inchangé](../../analysis/md_annex_replay_coverage.json)
- [Collection des extraits MD](../../analysis/md_selected_proof_video_collection.json)
- [Montage MD](../../analysis/md_proof_montage_report.json)
- [Pixels des frontières MD](../../analysis/md_montage_boundary_pixels_report.json)
- [Montage SMS](../../analysis/sms_proof_montage_report.json)
- [ROM V322](../../versions/v0322-1421abe4/gaw-megadrive-v0322.bin)

Les scripts `reconcile_md_selected_goals.py`, `collect_md_proof_videos.py`,
`build_md_proof_montage.py`, `verify_md_montage_boundaries.py` et
`finalize_rc_release.py` échouent si une preuve exigée manque.
"""
 (folder/'POINT6.md').write_text(text,encoding='utf-8',newline='\n')
 root=ROOT/'README.md';s=root.read_text(encoding='utf-8');start=s.index('**Reprise du 12 novembre' if '**Reprise du 12 novembre' in s else '**Point 6 terminé');end=s.index('Les scripts et les entrées de campagne',start)
 s=s[:start]+"""**Point 6 terminé pour le parcours retenu et ses annexes identifiées — 13 novembre 2026.**
Les campagnes MD PAL/NTSC rejoignent la fin et le générique. Les 145 objectifs
SMS sélectionnés ont leurs preuves de jeu, rejeu indépendant et vidéo MD.
Le montage MD NTSC comporte la campagne complète puis des branches annoncées,
avec chapitres, son du jeu, décodage intégral et frontières d'images vérifiées.
[Livraison, vidéos locales et limites](reports/gaw-v0322-rc1-2026-11-13/POINT6.md).

La V322 est qualifiée RC1 pour essais externes ; son binaire n'a pas changé.
Les 65 conversations ordinaires connues, 48 refus, 31 maisons d'argent, 11 soins,
14 sauvegardes/Continuer, transports, jeux, équipements, enseignements et fées
sont suivis dans [le rapprochement des objectifs](analysis/md_selected_gameplay_goal_closure.json).
Le registre de 409 enregistrements techniques reste conservé séparément ; il
n'est pas transformé en 409 objectifs de jeu validés.

La qualification ne vaut pas certification 100 % de tous les PNJ ou de la fidélité
physique : trois textes SMS sans déclencheur démontré, deux entrées monétaires
sans accès démontré, une duplication de suffixe propre à l'attente finale SMS
de Saylun et des écarts raster/fondu restent documentés. Les approches protégées
et le seul composant MD 99 clés avec aide monétaire sont annoncés dans les vidéos.
[Rapport RC](analysis/rc1_release_report.json) · [Différence Saylun](analysis/md_saylun_owned_apple_sms_suffix_difference.json).

"""+s[end:];root.write_text(s,encoding='utf-8',newline='\n')
 for platform,date in [('md','2026-11-13'),('sms','2026-11-12')]:
  p=ROOT/f'videos/{platform}/parcours-et-annexes-{date}/README.md';p.write_text(f'# Golden Axe Warrior {platform.upper()} — campagne et annexes\n\nVidéo locale et chapitres : `LISEZ-MOI-ET-CHAPITRES.txt`.\n\n[Livraison et limites](../../../reports/gaw-v0322-rc1-2026-11-13/POINT6.md). Les MP4 restent locaux.\n',encoding='utf-8',newline='\n')
 progress=ROOT/'analysis/sms_six_points_progress.json';j=json.loads(progress.read_bytes());j['date']='2026-11-13';j['points']['6_final_replay_and_video'].update(complete_selected_route_and_identified_annexes=True,md_delivery='analysis/md_proof_montage_report.json',md_selected_gameplay_goals='analysis/md_selected_gameplay_goal_closure.json',complete_100_percent_video=False);progress.write_bytes((json.dumps(j,indent=2,ensure_ascii=False)+'\n').encode())
 print('Point 6 summary published with passing release gates',flush=True)
if __name__=='__main__':main()
