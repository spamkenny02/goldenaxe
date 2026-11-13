"""Refuse a real native passage, walk away, return, then pay and traverse it."""
import argparse,json,sys
from pathlib import Path
import natural_paid_passage as game
from run_core import ROOT
from md_readonly_view import md_to_sms_view
from validate_playable_sprite_limit import symbols
from rebase_natural_campaign import evidence
from assisted_prefix import recording

def main():
 p=argparse.ArgumentParser(add_help=False);p.add_argument('--sms-reference',required=True);a,remaining=p.parse_known_args();assert '--sms' not in remaining;sys.argv=[sys.argv[0],*remaining]
 ref=json.loads(evidence(ROOT/'validation'/a.sms_reference/'report.json'));assert ref['passed'] and ref['kind']=='passage' and ref['variant']=='refuse'
 prefix=remaining[remaining.index('--prefix')+1];source=ROOT/'validation/natural-dungeon-route'/prefix;cap=json.loads((source/'capture.json').read_bytes());start=cap['frames'];prior=json.loads((source/'route_report.json').read_bytes());assert prior['house_target']==0x9f and prior['house_outside']==ref['outside']
 sy=symbols(ROOT/'megadrive/out/release/symbol.txt');initial=md_to_sms_view((source/f'ram_{start:05d}.bin').read_bytes(),sy);original=game.run;actual=[];state={};phase='refuse';modal_start=None;confirmation=None;refused=None;returned=None;folder=None
 def wrapped(*args,**kwargs):
  nonlocal folder
  folder=Path(args[2]);observe_base=kwargs['ram_observer'];control_base=kwargs['input_provider']
  def observe(frame,raw):
   nonlocal modal_start,refused,phase
   observe_base(frame,raw)
   if frame<start:return
   word=lambda n:raw[sy[n]]|raw[sy[n]+1]<<8
   state.update(modal=word('house_dialogue_active'),yes=word('minigame_confirm_selection'),room=word('room_id'),hero=word('hero_state'),game=word('game_state'),counter=word('hero_counter'),y=word('hero_y')>>8)
   if phase=='refuse' and state['modal'] and modal_start is None:modal_start=frame;args[3].add(frame+1)
   if confirmation is not None and refused is None and not state['modal']:
    r=md_to_sms_view(raw,sy);assert r[0xcf:0xf3]==initial[0xcf:0xf3] and r[0x100:0x200]==initial[0x100:0x200]
    changed=[dict(cell=i,before=initial[0x1c00+i],after=r[0x1c00+i]) for i in range(160) if r[0x1c00+i]!=initial[0x1c00+i]]
    (folder/'no-cell-observation.json').write_bytes((json.dumps(dict(frame=frame,changes=changed,gold=r[0xdd]),indent=2)+'\n').encode())
    # 38 is the animated closed NPC (28/29), replaced by floor1 on payment.
    assert all(change['cell']==0x38 and {change['before'],change['after']}=={0x28,0x29} for change in changed),'No changed more than the ordinary NPC animation pose'
    assert r[0x1c38] in (0x28,0x29) and r[0x1c38]!=1,'No opened the passage'
    refused=frame;phase='walk_away';args[3].add(frame+1)
  def control(frame):
   nonlocal confirmation,phase,returned
   if frame<=start:value=control_base(frame)
   elif phase=='walk_away':
    if state['y']>=104 and not state['counter'] and state['hero']==1:phase='pay_again';returned=frame;value=[]
    else:value=[5]
   elif phase=='refuse':
    if state['modal']:
     if frame-modal_start<160 or frame%20:value=[]
     elif state['yes']:value=[5]
     else:confirmation=frame;value=[8]
    else:value=control_base(frame)
   else:value=control_base(frame)
   if not actual or actual[-1]['buttons']!=value:actual.append(dict(frame=frame,buttons=value))
   return value
  kwargs.update(ram_observer=observe,input_provider=control);return original(*args,**kwargs)
 game.run=wrapped
 try:game.main()
 finally:game.run=original
 assert folder is not None and confirmation is not None and refused is not None and returned is not None
 report=json.loads((folder/'report.json').read_bytes());assert report['passed']
 report.update(variant='passage_refuse_then_pay',sms_reference=a.sms_reference,no_confirmation_frame=confirmation,no_completed_frame=refused,walked_away_before_return_frame=returned,no_resources_flags_and_passage_blocking_unchanged=True,npc_animation_pose_excluded_from_cell_equality=True,scope='Actual visible No, unchanged resources and permanent flags, passage remains blocked (NPC animation pose may advance); walk away, return, then actual payment and traversal to the real destination. No resource/quest/RNG fixtures.')
 (folder/'controls.json').write_bytes((json.dumps(actual,indent=2)+'\n').encode());(folder/'report.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());recording(folder,json.loads((folder/'capture.json').read_bytes()));print('Actual No then paid traversal:',refused,report['complete_frame'],flush=True)

if __name__=='__main__':main()
