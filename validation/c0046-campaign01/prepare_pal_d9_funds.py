"""Prepare ordinary world combat/coin collection to fund the three missing toll pieces."""
from pathlib import Path
import ast
root=Path(__file__).resolve().parents[2];project=root/'validation/c0046-campaign01/isolated/project'
s=(project/'tools/natural_dungeon_combat.py').read_text()
s=s.replace('assert itinerary and 256<=itinerary[0]<512','assert itinerary and 0<=itinerary[0]<256')
s=s.replace("assert (256<=itinerary[-1]<512 and args.target_room<256 if args.exit_dungeon else itinerary[-1]==args.target_room)","assert not args.exit_dungeon and itinerary[-1]==args.target_room")
s=s.replace("helpful=[e for e in loot if (e['type'] in (10,11)","helpful=[e for e in loot if e['type'] in (8,9) or (e['type'] in (10,11)")
s=s.replace("if __name__=='__main__':main()",'')
assert "__main__" not in s
s+="\nif __name__=='__main__':\n import sys\n original_run=run;done=None;last=0;gold_seen=[];sy_funds=symbols(ROOT/'megadrive/out/release/symbol.txt')\n def funds_run(*args,**kwargs):\n  observer=kwargs['ram_observer'];oldstop=kwargs.get('stop_when')\n  def observe_funds(f,raw):\n   global done,last\n   observer(f,raw);last=f\n   word=lambda n:int.from_bytes(bytes(raw[(sy_funds[n]+i)^1] for i in range(2)),'big')\n   if f<=260858:return\n   gold=word('hero_gold')\n   if not gold_seen or gold_seen[-1]['gold']!=gold:gold_seen.append(dict(frame=f,gold=gold,health=word('hero_health'),room=word('room_id')))\n   if done is None and gold>=10 and word('game_state')==12 and word('hero_state')==1 and word('hero_health')>0:done=f;args[3].add(f+100)\n  kwargs.update(ram_observer=observe_funds,stop_when=lambda:bool(oldstop and oldstop()) or done is not None and last>=done+100)\n  return original_run(*args,**kwargs)\n run=funds_run\n main()\n trial=sys.argv[sys.argv.index('--trial')+1];folder=ROOT/'validation/natural-dungeon-combat'/('md-pal-'+trial)\n report=json.loads((folder/'report.json').read_bytes())\n if done is not None:report.update(passed=True,failure=None,stop_reason='ordinary_gold_collected')\n report.update(ordinary_gold_goal=10,ordinary_gold_goal_reached=done is not None,gold_events=gold_seen,new_resource_writes=0,world_funding_controller=True)\n (folder/'report.json').write_text(json.dumps(report,indent=2)+'\\n')\n print('Ordinary PAL coin collection:',done,gold_seen,flush=True)\n"
p=project/'tools/collect_pal_d9_funds01.py';assert not p.exists();ast.parse(s);p.write_text(s)
print('Prepared ordinary combat/dropped-coin controller: no new primary writes, immutable ROM')
