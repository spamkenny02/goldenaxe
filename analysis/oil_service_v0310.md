# v0310 : huile et escaliers après le deuxième cristal

Le [bilan lié aux captures](oil_service_v0310_report.json) valide une visite
réelle de la maison C7 après D2. La ROM SMS, en 6482, donne gratuitement
l'objet si C0E8 est nul ; la visite conserve donc les deux pièces du héros.

Le parcours entre en 1F à 46346, monte en 0F, reçoit l'huile, redescend en 1F,
puis ressort en C7 à 47077. Le drapeau du don est positionné. Le héros reste
à 31 PV et 24 PM ; les deux cristaux sont conservés. Les 128 mots du HUD
physique correspondent au miroir SMS après le retour, dont l'image a été inspectée.

L'outil `natural_oil_stairs.py` accepte maintenant explicitement un préfixe
assisté déjà vérifié. Il rejoue seulement ses anciennes écritures de blessures,
sans en ajouter pendant la visite. Les journaux de l'approche et du service
sont identiques ; aucun objet, argent, acteur ou progression n'est injecté,
et aucun import SRAM ou état principal n'est utilisé. L'option reste explicite.

L'approche et la visite ont chacune une relecture indépendante par commandes
fixes : 65 536 octets de RAM et PNG final exacts. Ce résultat ne prouve pas
la phase R/IRQ globale ni toute la fidélité audiovisuelle. La ROM v310 est inchangée.
