"""Inventory direct text-front-end byte candidates and verified runtime callers.

Raw candidates include data and overlapping instructions. This is an audit
worklist, not a whole-ROM reachability or computed-pointer proof.
"""
import collections,hashlib,json
from extract_room_clear import z80
from run_core import ROOT


def main():
    rom=(ROOT/'input/original.sms').read_bytes()
    audit=json.loads((ROOT/'analysis/selected_sms_missing_texts_runtime_audit.json').read_bytes())
    targets={0x50c,0x524,0x6277,0x7444,0x779b}
    ops={0xc3,0xcd}|set(range(0xc2,0xfb,8))|set(range(0xc4,0xfd,8))
    candidates=[]
    for offset in range(len(rom)-2):
        target=int.from_bytes(rom[offset+1:offset+3],'little')
        if rom[offset] not in ops or target not in targets:continue
        # This context begins at a possible immediate HL load, not a proved
        # instruction boundary; preserve raw bytes so the limitation is visible.
        begin=offset
        for p in range(max(offset-32,offset//0x4000*0x4000),offset):
            if rom[p]==0x21:begin=p
        context=[];p=begin
        while p<=offset:
            ins=z80.decode(rom[p:p+8],p)
            if not ins.len:break
            context.append(dict(offset=f'0x{p:05X}',bytes=rom[p:p+ins.len].hex(),instruction=z80.decoded2str(ins)))
            p+=ins.len
        candidates.append(dict(offset=offset,bank=offset//0x4000,target=target,
            cpu_address=offset if offset<0x8000 else 0x8000+(offset&0x3fff),
            raw_context_hex=rom[max(0,offset-32):offset+3].hex(),candidate_context=context,
            boundary_proven=False,executable_proven=False))
    counts=collections.Counter();texts=collections.defaultdict(set);examples={}
    for row in audit['selected_recordings']:
        observation=json.loads((ROOT/'validation'/row['trace']/'dialogue_observations.json').read_bytes())
        for e in observation['events']:
            if e['event_pc'] not in (0x50c,0x524):continue
            key=(e['event_pc'],e['caller']);counts[key]+=1;texts[key].add(e['text_pc'])
            examples.setdefault(key,dict(trace=row['trace'],frame=e['frame'],outside=e['outside'],room=e['room']))
    callers=[dict(frontend=pc,stack_return=caller,possible_call_site=(caller-3)&65535,
        selected_text_pcs=sorted(texts[pc,caller]),event_occurrences=count,example=examples[pc,caller])
        for (pc,caller),count in sorted(counts.items())]
    house_sites=[r for r in candidates if r['target']==0x50c and r['bank']<2]
    house_coverage=[]
    for r in house_sites:
        assert rom[r['offset']]==0xcd
        key=(0x50c,r['offset']+3)
        assert key in counts,('Unobserved literal fixed-bank house frontend caller',r)
        house_coverage.append(dict(call_site=r['offset'],return_pc=key[1],example=examples[key],
            selected_text_pcs=sorted(texts[key]),observed=True))
    result=dict(source_sha256=hashlib.sha256(rom).hexdigest(),direct_operand_candidates=candidates,
        verified_runtime_callers=callers,selected_recordings=len(audit['selected_recordings']),
        all_literal_fixed_bank_050c_call_sites_observed=True,
        literal_fixed_bank_050c_call_site_count=len(house_coverage),house_entry_call_sites=house_coverage,
        target_strings=[dict(offset=o,pc=0x8000+(o&0x3fff),
            bytes_hex=rom[o:rom.index(0,o)+1].hex()) for o in (0xda58,0xda7c,0xed3c)],
        global_unused_proven=False,complete_call_data_flow_proof=False,
        remaining=['Prove code boundaries and eliminate data/overlapping byte candidates.',
            'Resolve computed and indirect control flow, argument origins and all formatter re-entry paths.',
            'Do not infer global unreachability from direct operands or repeated runtime prefixes.'],
        observations_include_shared_boot_prefixes=True,rom_modified=False)
    (ROOT/'analysis/sms_text_frontend_sources.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# Point 5 — audit des entrées du moteur de texte','',
        f"L’audit rapproche {len(audit['selected_recordings'])} enregistrements vérifiés de {len(callers)} couples entrée/adresse de retour observés. Les préfixes de démarrage communs sont comptés plusieurs fois ; ce nombre ne représente pas des conversations distinctes.",'',
        'Les appels directs possibles vers 050C, 0524, 6277, 7444 et 779B sont inventoriés sur les 256 Kio. Les correspondances brutes peuvent être des données ou commencer au milieu d’une instruction. Elles restent des candidats à analyser, pas des appels exécutables certifiés.','',
        f'Les {len(house_coverage)} appels littéraux vers 050C dans les deux banques fixes ont tous leur adresse de retour observée en exécution. Cela couvre ces sites d’appel, sans prouver toutes les valeurs possibles de leur argument ni éliminer les appels indirects.','',
        '| Entrée | Retour pile | Textes sélectionnés distincts |','| --- | --- | --- |']
    lines += [f"| {r['frontend']:04X} | {r['stack_return']:04X} | {', '.join(f'{p:04X}' for p in r['selected_text_pcs'])} |" for r in callers]
    lines += ['', 'Aucun des trois textes DA58, DA7C ou ED3C n’est déclenché dans ces enregistrements. Le point 5 reste ouvert : le flux indirect et les pointeurs calculés ne sont pas encore entièrement prouvés. Aucun dialogue ou état de quête n’est ajouté à la ROM sur cette seule absence.', '', '[Données, octets et contextes de désassemblage](sms_text_frontend_sources.json).']
    (ROOT/'analysis/sms_text_frontend_sources.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(dict(candidates=len(candidates),runtime_caller_pairs=len(callers),global_unused_proven=False)))


if __name__=='__main__':main()
