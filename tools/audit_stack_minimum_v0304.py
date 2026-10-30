"""Correct published sampled-stack margins using existing instruction records.

Historical raw profiles/reports are read only. This erratum distinguishes their
selected-entry minimum from the lower every-instruction observation.
"""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence


def main():
    rows = []
    for dungeon in range(1, 7):
        name = f'validation/stack-v0304-d{dungeon}-all/stack_report.json'
        raw = evidence(ROOT/name)
        profile = json.loads(raw)
        assert profile['all_instructions'] and not profile['invalid_heap_examples']
        assert profile['md_sha256'] == 'b7b4e15008a6f0a913c9ad43f15386abcdfbb719e5a575873d92712ba52503a8'
        sampled = min(item['sp'] for item in profile['minima'].values())
        instruction = min(item['sp'] for item in profile['instruction_minima'])
        boundary = max(item['end']+2 for item in profile['heap_changes'])
        assert sampled == profile['minimum_sp'] == 63472 and instruction == 63454 and boundary == 62976
        assert sha(evidence(ROOT/name)) == sha(raw)
        rows.append(dict(dungeon=dungeon, frames=profile['frames'], profile=name, profile_sha256=sha(raw),
                         sampled_minimum_sp=sampled, instruction_minimum_sp=instruction,
                         heap_boundary=boundary, sampled_margin_bytes=sampled-boundary,
                         corrected_instruction_margin_bytes=instruction-boundary))
    result = dict(passed=True, version=304, historical_profiles_unchanged=True, production_rom_unchanged=True,
                  corrected_margin_bytes=478, previously_published_sampled_margin_bytes=496,
                  discrepancy_bytes=18, profiles=rows,
                  validator_sha256=sha((ROOT/'tools/audit_stack_minimum_v0304.py').read_bytes()),
                  limits=['Observed on the six recorded v304 routes,starting normal-instruction SP observations at frame14.',
                          'Positive observed margin and valid heap headers do not bound future paths or every possible input sequence.'])
    (ROOT/'analysis/stack_minimum_v0304_erratum_report.json').write_bytes((json.dumps(result, indent=2)+'\n').encode())
    text = '# v304 : correction de la mesure minimale de pile\n\n'
    text += 'Les anciennes syntheses annoncaient496 octets comme marge minimale. Ce nombre utilise les points instrumentes (entrees de fonctions), alors que les profils avaient aussi conserve le minimum avant chaque instruction normale du68000.\n\n'
    text += 'Le minimum aux points instrumentes est63472 ; le minimum par instruction est63454. La limite du tas est62976. La marge observee correcte est donc **478 octets**, soit18 de moins que la synthese precedente. Les en-tetes du tas sont valides sur ces parcours.\n\n'
    text += '| Parcours termine | Frames | Marge aux points instrumentes | Marge par instruction |\n| --- | ---: | ---: | ---: |\n'
    for row in rows:
        text += f"| D{row['dungeon']} | {row['frames']} | 496 | 478 |\n"
    text += '\nLes profils bruts et anciens rapports restent conserves avec leurs empreintes. Le [rapport d\x27audit](stack_minimum_v0304_erratum_report.json) lie les six mesures et leurs hashes. Le profileur courant utilise maintenant le minimum par instruction lorsque ce releve est disponible et expose separement le minimum des points instrumentes.\n\n'
    text += 'Il s\x27agit d\x27une correction de verification et de documentation. La ROM ne change pas. Cette marge observee ne prouve pas la securite de tous les chemins futurs ; aucun chevauchement avec le tas n\x27est observe dans ces six parcours.\n'
    (ROOT/'analysis/stack_minimum_v0304_erratum.md').write_bytes(text.encode())
    print('Six immutable v304 profiles:sampled margin496;actual instruction margin478;18-byte correction;ROM unchanged')


if __name__ == '__main__':
    main()
