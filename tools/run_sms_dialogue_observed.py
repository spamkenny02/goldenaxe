"""Run an existing SMS controller tool with a read-only dialogue observer.

Every primary input/RAM-write still comes from the selected controller tool.
This wrapper records original formatter entries/returns and quest state.
"""
import ctypes as c,hashlib,importlib,json,struct,sys
from pathlib import Path
from run_core import ROOT
assert len(sys.argv)>2
core_override=None
if '--dialogue-core' in sys.argv:
 n=sys.argv.index('--dialogue-core');core_override=Path(sys.argv[n+1]).resolve();del sys.argv[n:n+2]
entry_module=importlib.import_module(sys.argv[1]);assert '--sms' in sys.argv[2:]
module=entry_module if hasattr(entry_module,'run') else importlib.import_module('natural_dungeon_route' if '--world-route' in sys.argv else 'natural_dungeon_combat')
core=core_override or ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_sms_dialogue02_libretro.dll'
dll=c.CDLL(str(core));dll.gaw_dialogue_size.restype=c.c_uint;dll.gaw_dialogue_data.restype=c.POINTER(c.c_uint8)
original=module.run;rom=(ROOT/'input/original.sms').read_bytes();events=[]
module.dialogue_events=events
def run(*args,**kwargs):
 assert Path(args[0]).read_bytes()==rom
 observer=kwargs.get('ram_observer');previous=0
 def observe(frame,raw):
  nonlocal previous
  if observer:observer(frame,raw)
  count=dll.gaw_dialogue_size();assert count<4096;data=dll.gaw_dialogue_data()
  for n in range(previous,count):
   record=c.string_at(c.cast(data,c.c_void_p).value+n*656,656);h=struct.unpack_from('<16I',record);pc=h[1];offset=0xc000+(pc&0x3fff) if 0x8000<=pc<0xc000 else None
   text=rom[offset:rom.index(0,offset)+1] if offset is not None else b''
   events.append(dict(event_pc=h[0],frame=frame,text_pc=pc,sms_file_offset=offset,room=h[2],outside=h[3],x=h[4]>>8,y=h[5]>>8,health=h[6],selected=h[7],gold=h[8],keys=h[9],logic_clock=h[10],caller=h[13],stack_pointer=h[12],dungeon=h[15],save_bytes_hex=record[64:].hex(),text_bytes_hex=text.hex(),text_rom_latin1=text[:-1].decode('latin-1'),post_frame_bitmap_sha256=hashlib.sha256(raw[0x1100:0x1510]).hexdigest()))
  previous=count
 kwargs.update(core=core,ram_observer=observe)
 result=original(*args,**kwargs);folder=Path(args[2]);report=dict(source_sha256=hashlib.sha256(rom).hexdigest(),core_sha256=hashlib.sha256(core.read_bytes()).hexdigest(),read_only=True,events=events,unique_text_pcs=sorted({e['text_pc'] for e in events if e['event_pc'] in (0x50c,0x524)}),scope='050C house entry, optional0524 common/service entry and06E3 formatter return, and627A standard wrapper return. Unique IDs count entry events only; return HL may point to the next, NOT displayed, string. Bitmap hashes sample the end of the event frame, not exact PC. Neither event alone proves all NPC variants visited.')
 (folder/'dialogue_observations.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n');return result
module.run=run
sys.argv=[entry_module.__file__]+sys.argv[2:]
entry_module.main()
