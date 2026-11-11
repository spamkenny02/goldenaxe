"""Reconcile the known literal house front-end argument construction sites.

The finite ordinary-house context inventory is an explicit assumption here.
Uninventoried indirect control flow remains outside this bounded certificate.
"""
import hashlib,json
from run_core import ROOT


def main():
    rom=(ROOT/'input/original.sms').read_bytes()
    frontend=json.loads((ROOT/'analysis/sms_text_frontend_sources.json').read_bytes())
    plain=json.loads((ROOT/'analysis/plain_house_dialogue_reference.json').read_bytes())
    targets={0x9a58,0x9a7c,0xad3c}
    direct={0x6061:(0x605e,0x911e),0x61df:(0x61dc,0x8bcd),0x64cd:(0x64ca,0x8e30),
        0x6502:(0x64ff,0x8df6),0x6660:(0x665c,0xa0e6),0x66ca:(0x66c7,0xb90e),
        0x683b:(0x6838,0xb95f),0x685b:(0x6858,0xb982),0x6880:(0x687d,0xb9bf),0x6890:(0x688d,0xba8e)}
    for site,(load,pc) in direct.items():
        assert rom[site:site+3]==bytes.fromhex('cd0c05')
        assert rom[load:load+3]==b'\x21'+pc.to_bytes(2,'little')
        assert rom[load+3:site] in (b'',b'\xc5')
    wrapper={0x5fe9:{0x9035},0x6006:{0x9021},0x621b:{0xa52f,0xac1e},
        0x6290:{0x8fe3},0x6296:{0x8bea},0x647f:{0x90bf},0x6494:{0x905b},
        0x6631:{0xa7ce,0xac65,0xa852,0xacb5,0xa887,0xace3},
        0x6675:{0xa077},0x667b:{0xa17f},0x669a:{c['text_pc'] for c in plain['contexts']},
        0x66d5:{0xb930},0x670e:{0xb94d},0x6772:{0xb9d7,0xba20},0x68a4:{0xb930}}
    sites={r['offset'] for r in frontend['direct_operand_candidates'] if r['target']==0x6277 and r['bank']<2}
    assert sites==set(wrapper),(sites-set(wrapper),set(wrapper)-sites)
    assert {r['offset'] for r in frontend['direct_operand_candidates'] if r['target']==0x50c and r['bank']<2}==set(direct)|{0x6277}
    assert rom[0x6213:0x621b]==bytes.fromhex('212fa51803211eac')
    assert rom[0x6614:0x6634]==bytes.fromhex('21cea71165ac180e2152a811b5ac18062187a811e3ac3ad7c0873001ebc37762')
    assert rom[0x667e:0x669d]==bytes.fromhex('3aa6c0e677fe14c02a60c0ed42c0f1eb3abbc0be235e23562320f8ebc37762')
    assert rom[0x626a:0x627a]==bytes.fromhex('21d98e180821948e1803215c8ecd0c05')
    for site,pcs in wrapper.items():
        if site in (0x621b,0x6631,0x669a,0x6772,0x66d5):continue
        assert len(pcs)==1 and rom[site-3:site]==b'\x21'+next(iter(pcs)).to_bytes(2,'little')
    assert rom[0x6768:0x6775]==bytes.fromhex('fe3821d7b928032120bacd7762')
    assert rom[0x66d0:0x66d8]==bytes.fromhex('2130b9fe00ca7762')
    # Validate every exported ordinary row directly against its original ROM table.
    table_rows=[]
    for context in plain['contexts']:
        wanted=bytes([context['outside']])+context['text_pc'].to_bytes(2,'little')
        p=context['table'];matches=[]
        for offset in range(p,min(p+768,0xc000),3):
            if rom[offset:offset+3]==wanted:matches.append(offset)
        assert matches,(context,wanted.hex())
        table_rows.append(dict(outside=context['outside'],room=context['room'],coordinate=context['coordinate'],
            text_pc=context['text_pc'],table=context['table'],matching_rom_rows=matches))
    domain={pc for _,pc in direct.values()}|{0x8ed9,0x8e94,0x8e5c}
    for pcs in wrapper.values():domain.update(pcs)
    assert not domain&targets
    result=dict(source_sha256=hashlib.sha256(rom).hexdigest(),passed=True,
        scope='Known literal fixed-bank house frontend calls, literal/relative wrapper edges and inventoried ordinary-context tables.',
        fixed_bank_050c_call_sites=11,nonwrapper_immediate_sites={f'{site:04X}':dict(load=load,text_pc=pc) for site,(load,pc) in direct.items()},
        direct_wrapper_sites={f'{site:04X}':sorted(pcs) for site,pcs in wrapper.items()},
        wrapper_relative_or_fallthrough_arguments=[0x8ed9,0x8e94,0x8e5c],ordinary_table_rows=table_rows,
        known_house_argument_domain=sorted(domain),reported_targets_selected=False,
        global_unused_in_sms_proven=False,complete_call_data_flow_proof=False,
        assumptions_and_limits=['The 65 ordinary contexts are the existing independently checked inventory, not a new proof of all reachable contexts.',
            'Immediate sites are checked byte for byte; the two selector blocks and ordinary wrapper are preserved verbatim.',
            'All literal edges into6277 and all literal050C calls in fixed banks are accounted for. This does not rule out an unclassified indirect edge or alternate argument construction outside those paths.',
            '7444/779B service and teaching paths are inventoried separately in sms_text_frontend_sources.json; they are not certified by this house-domain audit.'],
        rom_modified=False)
    (ROOT/'analysis/sms_standard_house_text_domains.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,known_argument_pcs=len(domain),literal_wrapper_edges=len(wrapper),targets_selected=False,global_unused_proven=False)))


if __name__=='__main__':main()
