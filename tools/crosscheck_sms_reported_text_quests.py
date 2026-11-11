"""Check related observed Earth/Bell dialogue and actual release assets.

Related dialogue does not prove the three untriggered strings unused and is
not substituted for their still-unknown source triggers.
"""
import hashlib,json
from run_core import ROOT


def main():
    sms=(ROOT/'input/original.sms').read_bytes()
    mdpath=ROOT/'versions/v0321-89c58333/gaw-megadrive-v0321.bin';md=mdpath.read_bytes()
    assert hashlib.sha256(md).hexdigest()=='89c5833351312ffaa591efb1939161910a298af06437080e2cf84fb3fb8ac86e'
    audit=json.loads((ROOT/'analysis/selected_sms_missing_texts_runtime_audit.json').read_bytes());observed={}
    for row in audit['selected_recordings']:
        report=json.loads((ROOT/'validation'/row['trace']/'dialogue_observations.json').read_bytes())
        for event in report['events']:
            if event['event_pc'] not in (0x50c,0x524):continue
            observed.setdefault(event['text_pc'],dict(trace=row['trace'],frame=event['frame'],
                room=event['room'],outside=event['outside'],caller=event['caller']))
    contexts=[(0xd247,'Indice : aller au sud du port et utiliser la Cloche de Glace'),
        (0xd6ec,'Indice sur les rochers cassables avec Terre niveau 2'),
        (0xe6a5,'Cloche : identifier certains rochers cassables'),
        (0xe937,'PNJ qui ne se souvient pas du pouvoir de la cloche'),
        (0xea61,'Limite de detection de la cloche'),
        (0xf06f,'Battler : proposition de Terre niveau 1'),
        (0xf233,'Battler : proposition de Terre niveau 2'),
        (0xf3e5,'Battler : acquisition effective de Terre niveau 2'),
        (0xf333,'Battler : dialogue apres les enseignements')]
    related=[]
    for offset,label in contexts:
        pc=0x8000+(offset&0x3fff);text=sms[offset:sms.index(0,offset)+1]
        locations=[];p=0
        while (p:=md.find(text,p))>=0:locations.append(p);p+=1
        assert pc in observed and locations,(hex(offset),pc in observed,locations)
        related.append(dict(sms_offset=f'0x{offset:04X}',text_pc=pc,meaning=label,
            sms_actual_entry=observed[pc],present_verbatim_in_v321=True,md_offsets=locations,
            original_bytes_sha256=hashlib.sha256(text).hexdigest()))
    missing=[]
    for offset in (0xda58,0xda7c,0xed3c):
        text=sms[offset:sms.index(0,offset)+1];pc=0x8000+(offset&0x3fff)
        assert text not in md and pc not in observed
        missing.append(dict(sms_offset=f'0x{offset:04X}',present_verbatim_in_v321=False,
            source_trigger_observed=False,globally_unused_proven=False))
    result=dict(source_sha256=hashlib.sha256(sms).hexdigest(),md_v321_sha256=hashlib.sha256(md).hexdigest(),
        passed=True,related_dialogues=related,reported_strings=missing,rom_modified=False,
        conclusion='Related Earth acquisition/upgrade and Bell hints are actually observed on SMS and their exact assets exist in V321. This does not identify or replace the three unknown triggers. Natural MD replay of those contexts remains a separate requirement.',
        global_unused_in_sms_proven=False,point5_complete=False)
    (ROOT/'analysis/sms_reported_text_quest_crosscheck.json').write_text(json.dumps(result,indent=2)+'\n')
    text=['# Point 5 — quetes et indices lies aux trois textes','',
        'Les trois phrases DA58, DA7C et ED3C ne sont toujours pas declenchees dans les preuves retenues et ne figurent pas litteralement dans la V321. Elles ne sont pas declarees inutilisees globalement.','',
        'Le controle des dialogues lies etablit cependant les elements suivants :','',
        '| Texte SMS | Controle |','| --- | --- |']
    text += [f"| {r['sms_offset']} | {r['meaning']} : entree SMS observee et octets exacts presents dans la V321. |" for r in related]
    text += ['', 'Ces observations documentent les enseignements de Terre et les indices de la cloche deja presents. Elles ne constituent pas une preuve du declencheur des trois autres phrases, ni une validation du parcours MD correspondant. Aucun texte ou declencheur de quete n est ajoute sur cette base.', '',
        '[Traces, reperes d execution et offsets MD](sms_reported_text_quest_crosscheck.json).']
    (ROOT/'analysis/sms_reported_text_quest_crosscheck.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,related_sms_dialogues_observed=len(related),related_v321_assets_present=len(related),point5_complete=False)))


if __name__=='__main__':main()
