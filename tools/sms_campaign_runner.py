"""Small orchestration helpers for recorded, replay-gated SMS campaign stages."""
import json
import continue_sms_npc_d4 as base
from run_core import ROOT
from cold_replay_stream import ReplayStream


class Campaign:
    def __init__(self,prefix,boss,label):
        self.family,self.current=prefix.split('/');self.boss=boss;self.label=label
        number=1
        while (ROOT/f'validation/{label}-cold-stream{number:02d}').exists():number+=1
        self.stream=ReplayStream(ROOT/f'validation/{label}-cold-stream{number:02d}',sms=True)
        base.STREAM=self.stream
        self.points=[]

    def close(self):self.stream.close();base.STREAM=None
    def cap(self):return base.read(self.family+'/'+self.current,'capture.json')
    def raw(self):return (ROOT/'validation'/self.family/self.current/f'ram_{self.cap()["frames"]:05d}.bin').read_bytes()
    def verify(self,predicate):
        base.checked(self.family,self.current,predicate)
        self.points.append(dict(trace=self.family+'/'+self.current,frames=self.cap()['frames']))
        (self.stream.folder/'selected_stages.json').write_text(json.dumps(self.points,indent=2)+'\n')
    def invoke(self,tool,args,family,name,predicate):
        if not (ROOT/'validation'/family/name).exists():base.invoke(tool,args,name)
        self.family,self.current=family,name;self.verify(predicate)
    def equip(self,slot,suffix):
        if self.raw()[0xdf]==slot:return
        trial=self.label+'-'+suffix
        self.invoke('natural_weapon_selection.py',['--sms','--assisted-prefix','--trace',self.family+'/'+self.current,
            '--slot',str(slot),'--trial',trial],base.SERVICE,'sms-'+trial,lambda r:r['passed'])
    def route(self,suffix,extra,new_episode=False,exit_proof=None,tool='assisted_boss_route.py'):
        trial='sms-'+self.label+'-'+suffix
        args=['--sms','--world-route','--boss-room',hex(self.boss),'--assisted-prefix',
              '--prefix-combat' if self.family==base.COMBAT else '--prefix-service',self.current,
              *(['--axe-terrain','--live-room-replan'] if self.raw()[0xe1] else []),
              *(['--rope-terrain'] if self.raw()[0xed] else []),'--frames',str(self.cap()['frames']+18000),
              '--trial',trial,*extra]
        if new_episode:args+=['--new-assistance-episode']
        if exit_proof:args+=['--completed-exit-proof',exit_proof]
        self.invoke(tool,args,base.ROUTE,'sms-'+trial,lambda r:r['reached_entrance'])
    def service(self,suffix,module,extra):
        trial=self.label+'-'+suffix
        self.invoke('run_sms_dialogue_observed.py',[module,'--dialogue-core',
            str(ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_sms_dialogue03_libretro.dll'),
            '--sms','--assisted-prefix','--prefix',self.current,'--trial',trial,*extra],
            base.SERVICE,'sms-'+trial,lambda r:r['passed'])
    def stage(self,suffix,planner,rooms,target,extra=(),gate='room_cleared',coarse=False,budget=18000,tool=None):
        trial='sms-'+self.label+'-'+suffix
        common=[x for x in base.COMMON if x!='--equip-axe']
        args=['--boss-room',hex(self.boss),'--planner',planner,*common,
              '--prefix' if self.family==base.ROUTE else '--continuation',self.current,
              '--rooms',rooms,'--target-room',target,'--frames',str(self.cap()['frames']+budget),
              '--trial',trial,*extra]
        tool=tool or ('assisted_boss_coarse_route.py' if coarse else 'assisted_boss_route.py')
        self.invoke(tool,args,base.COMBAT,'sms-auto-'+trial,lambda r:r[gate])
    def resume(self,suffix,next_boss):
        trial='sms-'+self.label+'-'+suffix
        self.invoke('resume_after_intermediate.py',['--sms','--trace',self.family+'/'+self.current,
            '--boss-room',hex(self.boss),'--next-boss-room',hex(next_boss),'--trial',trial],
            base.COMBAT,'sms-auto-'+trial,lambda r:r['resumed_after_verified_intermediate'])
        self.boss=next_boss
