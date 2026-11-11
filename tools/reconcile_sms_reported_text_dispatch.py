"""Exclude adjacent-NPC/formatter-return explanations for the three reported strings.

This bounded proof deliberately does not assert global ROM unreachability.
"""
import hashlib,json
from run_core import ROOT


def main():
    rom=(ROOT/'input/original.sms').read_bytes()
    plain=json.loads((ROOT/'analysis/plain_house_dialogue_reference.json').read_bytes())
    conditional=json.loads((ROOT/'analysis/conditional_house_reference.json').read_bytes())
    runtime=json.loads((ROOT/'analysis/selected_sms_missing_texts_runtime_audit.json').read_bytes())
    fb=next(c for c in plain['contexts'] if c['outside']==0xfb and c['room']==0x8f)
    assert fb['text_pc']==0x99f1 and rom.index(0,0xd9f1)+1==0xda58
    assert rom.index(0,0xda58)+1==0xda7c and rom.index(0,0xece3)+1==0xed3c
    wrapper=bytes.fromhex('cd0c05cd950b3a21c0e63f28f6c3e21d')
    assert rom[0x6277:0x6287]==wrapper
    handler=bytes.fromhex('2187a811e3ac3ad7c0873001ebc37762')
    assert rom[0x6624:0x6634]==handler
    pcs={c['text_pc'] for c in plain['contexts']}|set(conditional['text_pcs'])
    assert not pcs&{0x9a58,0x9a7c,0xad3c}
    result=dict(source_sha256=hashlib.sha256(rom).hexdigest(),
        global_unused_in_sms_proven=False,rom_modified=False,
        fb_npc=dict(outside='0xFB',interior='0x8F',coordinate=f'0x{fb["coordinate"]:04X}',
            selected_text_cpu='0x99F1',selected_text_file='0xD9F1',returned_next_text_cpu='0x9A58',
            wrapper='0x6277..0x6286',wrapper_bytes=wrapper.hex(),
            conclusion='The wrapper calls 050C once, waits for input and jumps to 1DE2. It does not display returned HL or the adjacent 9A58/9A7C strings.'),
        halls_npc=dict(outside='0xCE',interior='0x02',coordinate='0x0344',handler='0x6624..0x6633',
            handler_bytes=handler.hex(),condition='C0D7 bit7: ninth crystal',
            selected_before='0xA887',selected_after='0xACE3',returned_next_after='0xAD3C',
            conclusion='This handler selects one of exactly two strings then jumps to 6277. It has no Ice Bell branch and never selects AD3C.'),
        current_runtime_audit=runtime,
        classification='Adjacent ordinary/conditional NPC routes excluded; no observed gameplay omission established; another trigger is not ruled out globally.',
        remaining_requirement='Complete call/data-flow proof for every text entry path, or an actual source trigger for the three strings. Absence of a raw pointer alone is insufficient.')
    (ROOT/'analysis/reported_text_dispatch_reconciliation.json').write_text(json.dumps(result,indent=2)+'\n')
    text='''# Réconciliation des trois textes signalés

Les chaînes SMS DA58, DA7C et ED3C existent bien. Leur absence littérale des ressources MD avait été constatée ; aucun nouveau déclencheur n'est inventé pour les rendre visibles.

Le PNJ de FB/8F sélectionne 99F1, dont le texte se termine juste avant DA58. Le formateur retourne alors HL=9A58. Le code original 6277–6286 appelle le formateur une seule fois, attend une commande, puis saute à 1DE2 : il n'affiche pas la chaîne suivante. DA7C suit DA58, mais aucune de ces deux chaînes n'est sélectionnée par ce PNJ. Le simple voisinage dans la banque de texte ne définit donc pas une quête Terre supplémentaire chez lui.

Le troisième PNJ de Halls (CE/02, position 0344) sélectionne A887 avant le neuvième cristal et ACE3 après. Son code 6624–6633 ne lit aucun état de cloche et rejoint le même affichage unique. ED3C suit physiquement le texte ACE3 : le retour HL=AD3C observé après celui-ci n'est pas une nouvelle entrée de dialogue.

Les relevés d'exécution distinguent les appels 050C/0524 des retours du formateur et du wrapper. Le JSON associé conserve les octets de code vérifiés, les contextes et les relevés retenus. Les trois adresses ne figurent ni dans les 65 sélections ordinaires exportées ni dans les neuf variantes conditionnelles connues.

Conclusion limitée : les PNJ voisins et le pointeur de retour ne sont pas des déclencheurs de ces trois textes. Cela écarte cette explication d'un dialogue manquant dans le portage. L'inutilisation globale dans toute la ROM n'est pas encore démontrée ; ce point reste ouvert jusqu'à une preuve complète de flux ou un déclenchement réel.
'''
    (ROOT/'analysis/reported_text_dispatch_reconciliation.md').write_text(text,encoding='utf-8')
    print('Adjacent NPC dispatch and ignored return pointers proved; global unused status remains open.')


if __name__=='__main__':main()
