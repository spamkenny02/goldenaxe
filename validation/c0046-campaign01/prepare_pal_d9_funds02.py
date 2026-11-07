"""Fix funding-controller stop: finish the whole loop before claiming room clearance."""
from pathlib import Path
root=Path(__file__).resolve().parents[2];project=root/'validation/c0046-campaign01/isolated/project'
s=(project/'tools/collect_pal_d9_funds01.py').read_text()
s=s.replace("if state['room']==args.target_room:","if state['room']==args.target_room and itinerary_index==len(itinerary)-1:")
s=s.replace("if done is not None:report.update(passed=True,failure=None,stop_reason='ordinary_gold_collected')", "if done is not None:report.update(passed=True,failure=None,stop_reason='ordinary_gold_collected')\n else:report.update(passed=False,failure=report['failure'] or 'gold_goal_not_reached')")
p=project/'tools/collect_pal_d9_funds02.py';assert not p.exists();p.write_text(s)
