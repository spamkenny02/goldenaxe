"""Preserve both source snapshots and cold readers after the pre-boss wait timeout."""
from pathlib import Path
root=Path(__file__).resolve().parents[2]
path=root/'validation/c0046-campaign01/isolated/project/tools/summarize_d6_campaign_c0046.py'
text=path.read_text()
before=" names = load(ROOT/'validation/c0046-d6-finish-sources/source_index.json')"
after=""" original_names=load(ROOT/'validation/c0046-d6-finish-sources/source_index.json')
 for name,h in original_names.items():assert sha(read(ROOT/'validation/c0046-d6-finish-sources'/name.split('/')[-1]))==h
 names = load(ROOT/'validation/c0046-d6-finish-sources02/source_index.json')"""
assert text.count(before)==1
text=text.replace(before,after)
before=" for name,h in names.items():assert h==index[name.split('/')[-1]]==sha(read(ROOT/'validation/c0046-d6-finish-sources'/name.split('/')[-1]))"
after=before.replace("c0046-d6-finish-sources'","c0046-d6-finish-sources02'")
assert text.count(before)==1
text=text.replace(before,after)
before="  assert proof['final_png_exact'] and not proof['feedback_reads']"
after=before+"\n  expected_reader=(original_names if kind=='release' else names)['tools/cold_replay_stream.py']\n  assert proof['driver_sha256']==expected_reader"
assert text.count(before)==1
text=text.replace(before,after)
text=text.replace(" result = dict(passed=True,candidate='c0046',", " result = dict(passed=True,candidate='c0046',cold_replay_streams=2,pre_boss_wait_timeout_recovered=True,")
path.write_text(text,encoding='utf-8')
print('D6 audit checks both reader versions and independent cold streams')
