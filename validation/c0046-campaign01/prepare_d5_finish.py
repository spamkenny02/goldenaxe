"""Prepare the existing source-stat D5 controller for the isolated candidate."""
from pathlib import Path

root=Path(__file__).resolve().parents[2]
target=root/'validation/c0046-campaign01/isolated/project/tools'
assert target.is_dir()
for name in ('finish_d5','summarize_d5_campaign'):
    source=(root/'tools'/f'{name}_v0317.py').read_text()
    text=source.replace('v0317','c0046').replace('V317','C0046')
    if name.startswith('summarize'):
        old='7694654ec85dd6626c0e17ff1834e5893d4eb35481400a4725eac6b6f3503294'
        assert old in text
        text=text.replace(old,'9e747d38e0c6fb2d69b7c1aa8c2b296a61e8b6af41171d14e543ed9a6cb49cf5')
        text=text.replace("previous = ROOT/prior['ready_trace']", "previous = ROOT/'validation/natural-dungeon-combat'/prior['ready_trace'].split('/')[-1]")
        text=text.replace('version=317',"candidate='c0046'")
        marker=" (ROOT/'analysis/d5_campaign_c0046_report.json').write_bytes"
        assert text.count(marker)==1
        text=text.replace(marker," prefix=ROOT.relative_to(ROOT.parents[3]).as_posix()+'/'\n for stage in result['stages']:stage['trace']=prefix+stage['trace']\n result['evidence']={(k if k.startswith('analysis/') else prefix+k):v for k,v in refs.items()}\n"+marker)
    path=target/f'{name}_c0046.py'
    assert not path.exists(),path
    path.write_text(text,encoding='utf-8')
print('D5 source-stat boss and return controller prepared; not executed')
