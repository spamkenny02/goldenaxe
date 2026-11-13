"""Actual MD branch orchestration with a separate cold replay witness.

sms_view is a read-only conversion for the existing ROM-map planner. It is
never written to the emulator and does not initialize any game state.
"""
import json,subprocess,sys,os
from pathlib import Path
from run_core import ROOT
from cold_replay_stream import ReplayStream
from validate_playable_sprite_limit import symbols

class Campaign:
    def __init__(self,prefix,rom,label,attach=None):
        self.family,self.current=prefix.split('/');self.rom=(ROOT/rom).resolve();self.label=label;self.sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
        self.stream_options=None
        if attach:
            self.stream=ReplayStream.attach(ROOT/'validation'/attach[0],attach[1],self.rom);self.stream_options=self.cap()['core_options']
        else:self.new_stream()
    def new_stream(self):
        n=1
        while (ROOT/f'validation/{self.label}-cold-stream{n:02d}').exists():n+=1
        self.stream=ReplayStream(ROOT/f'validation/{self.label}-cold-stream{n:02d}',rom=self.rom)
    @property
    def trace(self):return self.family+'/'+self.current
    def cap(self):return json.loads((ROOT/'validation'/self.trace/'capture.json').read_bytes())
    def raw(self):return (ROOT/'validation'/self.trace/f'ram_{self.cap()["frames"]:05d}.bin').read_bytes()
    def sms_view(self):
        from md_readonly_view import md_to_sms_view
        return md_to_sms_view(self.raw(),self.sy)
    def verify(self,predicate,record_from=None):
        folder=ROOT/'validation'/self.trace
        r=json.loads((folder/('route_report.json' if self.family=='natural-dungeon-route' else 'report.json')).read_bytes())
        assert not r['failure'] and predicate(r),(self.trace,r)
        cap=self.cap();assert cap['rom_sha256']==__import__('hashlib').sha256(self.rom.read_bytes()).hexdigest()
        proof=folder.with_name(folder.name+f'-assisted-fixed-replay-{cap["frames"]}')/'replay_report.json'
        if not proof.exists():
            if self.stream_options is not None and self.stream_options!=cap['core_options']:
                self.stream.close();self.new_stream()
            self.stream_options=cap['core_options']
            self.stream.prove(self.trace,record_from=record_from if os.environ.get('GAW_STREAM_VIDEO')=='1' else None)
        else:assert json.loads(proof.read_bytes())['passed']
        print('MD VERIFIED',self.trace,cap['frames'],flush=True)
    def invoke(self,tool,args,family,name,predicate):
        first=self.cap()['frames']+1
        folder=ROOT/'validation'/family/name
        if not folder.exists():
            with (ROOT/'validation'/(name+'.log')).open('w') as log:subprocess.run([sys.executable,str(ROOT/'tools'/tool),*args],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        self.family,self.current=family,name;self.verify(predicate,record_from=first)
    def route(self,suffix,extra,tool='natural_bell_world_route.py'):
        trial=self.label+'-'+suffix
        view=self.sms_view();cap=self.cap();boss=0x14c
        if cap['test_ram_writes']:
            from assisted_prefix import recording
            boss=recording(ROOT/'validation'/self.trace,cap)[0]['boss_room']
        args=['--world-route','--boss-room',hex(boss),'--assisted-prefix','--rom',str(self.rom),
            '--prefix-combat' if self.family=='natural-dungeon-combat' else '--prefix-service',self.current,
            *(['--axe-terrain','--live-room-replan'] if view[0xe1] else []),*(['--rope-terrain'] if view[0xed] else []),
            '--frames',str(self.cap()['frames']+18000),'--trial',trial,*extra]
        self.invoke(tool,args,'natural-dungeon-route','md-'+trial,lambda r:r['reached_entrance'])
    def equip(self,slot,suffix):
        if self.sms_view()[0xdf]==slot:return
        trial=self.label+'-'+suffix;n=1
        while (ROOT/f'validation/natural-service-route/md-{trial}-{n:02d}').exists():n+=1
        trial+=f'-{n:02d}'
        self.invoke('natural_weapon_selection.py',['--rom',str(self.rom),'--assisted-prefix','--trace',self.trace,'--slot',str(slot),'--trial',trial],
                    'natural-service-route','md-'+trial,lambda r:r['passed'])
    def service(self,suffix,tool,extra):
        trial=self.label+'-'+suffix
        if not tool.endswith('.py'):tool+='.py'
        self.invoke(tool,['--rom',str(self.rom),'--assisted-prefix','--prefix',self.current,'--trial',trial,*extra],
                    'natural-service-route','md-'+trial,lambda r:r['passed'])
    def stage(self,suffix,rooms,target,extra=(),gate='room_cleared',planner='ordinary',boss=0x14c):
        # The native combat driver uses the published alias. Require exact bytes.
        assert self.rom.read_bytes()==(ROOT/'gaw-megadrive.bin').read_bytes()
        trial=self.label+'-'+suffix
        args=['--boss-room',hex(boss),'--planner',planner,'--assisted-prefix','--max-deaths','0','--collision-aim','--settle-attacks','--doorway-ranges','--ignore-inactive-actors','--retry-isolated-foes','--prefix' if self.family=='natural-dungeon-route' else '--continuation',self.current,'--rooms',rooms,'--target-room',target,'--frames',str(self.cap()['frames']+18000),'--trial',trial,*extra]
        self.invoke('assisted_boss_route.py',args,'natural-dungeon-combat','md-auto-'+trial,lambda r:r[gate])
    def npc(self,suffix,reference,quest_hint=False):
        name='md-'+self.label+'-'+suffix
        self.invoke('md_npc_visit.py',['--prefix',self.trace,'--sms-reference',reference,'--assisted-prefix','--candidate',str(self.rom),'--out','natural-service-route/'+name,*(['--quest-hint'] if quest_hint else [])],
            'natural-service-route',name,lambda r:r['passed'])
    def close(self):self.stream.close()
