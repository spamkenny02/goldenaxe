"""Adapt report publication for the candidate, preserving all save/reload checks."""
import ast
from pathlib import Path
root=Path(__file__).resolve().parents[2];project=root/'validation/c0046-campaign01/isolated/project'
text=(root/'tools/validate_game_written_save.py').read_text()
start=text.index(" versions=json.loads((ROOT/'versions/index.json').read_bytes())")
end=text.index(" print('Real save fixed replay",start)
# Candidate identities are separate from numbered production releases; never invent a version entry.
text=text[:start]+""" assert digest=='9e747d38e0c6fb2d69b7c1aa8c2b296a61e8b6af41171d14e543ed9a6cb49cf5'
 assert a.release_report_name=='game_written_save_c0046_nine_crystals_report.json'
 release_path=ROOT/'analysis'/a.release_report_name;assert not release_path.exists()
 release_report=dict(result,candidate='c0046',md_sha256=digest)
 release_path.write_bytes((json.dumps(release_report,indent=2)+'\\n').encode())
"""+text[end:]
ast.parse(text)
target=project/'tools/validate_candidate_game_written_save_c0046.py';assert not target.exists();target.write_text(text,encoding='utf-8')
p=project/'tools/continue_after_d9_c0046.py';text=p.read_text()
assert text.count('validate_game_written_save.py')==2
text=text.replace('validate_game_written_save.py','validate_candidate_game_written_save_c0046.py').replace('V0317','c0046')
ast.parse(text);p.write_text(text,encoding='utf-8')
print('Candidate save validator prepared: unchanged runtime checks; candidate report replaces production-index lookup')
