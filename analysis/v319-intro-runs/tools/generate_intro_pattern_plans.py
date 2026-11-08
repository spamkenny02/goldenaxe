"""Compile original intro RLE bytes and exact command work; no frame/phase data."""
import hashlib,json
from actor_reference import ROOT
from validate_native_patterns import Trace
from graphics_prefix_phase import pattern_rle
rom=(ROOT/'input/original.sms').read_bytes();lines=['#ifndef GAW_INTRO_PATTERN_PLANS_GENERATED_H','#define GAW_INTRO_PATTERN_PLANS_GENERATED_H','#include "source_pattern_clock.h"'];assets=[]
for header in (0x9d70,0xa655):
 offset=0x18000+header+4-0x8000;start_asset=offset;rows=[];tag=f'gaw_intro_{header:04x}'
 for plane in range(4):
  start=offset;cursor=0x4000+plane;ticks=fetches=0;decoded=bytearray();bounds=[[0,0,0,0]]
  while rom[offset]:
   command_start=offset;command=rom[offset];offset+=1;count=command&127 or 256;literal=command&128;carry=((cursor&255)+count*4)>>8
   ticks+=44+count*(135 if literal else 134)-carry-5+(16 if literal else 29)
   fetches+=9+count*(19 if literal else 18)+carry+(2 if literal else 4)
   for n in range(count):decoded.append(rom[offset]);offset+=bool(literal)
   if not literal:offset+=1
   isolated=Trace(rom[command_start:offset]+bytes(4));empty=Trace(bytes(4));pattern_rle(isolated,0,cursor);pattern_rle(empty,0,cursor)
   assert isolated.foreground_tstates-empty.foreground_tstates==ticks-bounds[-1][0]
   assert isolated.fetches-empty.fetches==fetches-bounds[-1][1]
   cursor=(cursor+count*4)&65535;bounds.append([ticks,fetches,offset-start,len(decoded)])
  offset+=1
  name=tag+'_'+str(plane)
  lines.append('static const SourcePatternBoundary '+name+'_bounds[]={'+','.join('{'+','.join(str(v)+'UL' if n<2 else str(v) for n,v in enumerate(b))+'}' for b in bounds)+'};')
  lines.append('static const u8 '+name+'_decoded[]={'+','.join(map(str,decoded))+'};')
  rows.append(dict(commands=len(bounds)-1,decoded=len(decoded),packed=offset-start,tstates=ticks,m1=fetches,decoded_sha256=hashlib.sha256(decoded).hexdigest()))
 lines.append('static const SourcePatternPlan '+tag+'_plan={{'+','.join('{'+tag+'_'+str(n)+'_bounds,'+tag+'_'+str(n)+'_decoded,'+str(rows[n]['commands'])+'}' for n in range(4))+'}};')
 assert offset==0x18000+({0x9d70:0xa598,0xa655:0xae6f}[header])-0x8000
 assets.append(dict(header=header,offset=start_asset,packed=offset-start_asset,end=offset,planes=rows))
lines.append('#endif');target=ROOT/'megadrive/src/source_intro_pattern_plans_generated.h';content=('\n'.join(lines)+'\n').encode()
if not target.exists() or target.read_bytes()!=content:target.write_bytes(content)
r=dict(passed=True,source_sha256=hashlib.sha256(rom).hexdigest(),assets=assets,header_sha256=hashlib.sha256(content).hexdigest(),limits=['Immutable decoded ROM bytes and exact032A command-boundary T/M1 prefixes only; no captured phases,frames or delays.'])
(ROOT/'analysis/intro_pattern_plan_assets_report.json').write_text(json.dumps(r,indent=2)+'\n')
print('Generated both intro plans; every command checked against instruction model.')
