"""Original four teacher portraits, texts and service3 nodes (79DA..7B30)."""
import json
from run_core import ROOT
from extract_title import rle_planes,map_decode
from archive_lossless_evidence import sha
from extract_room_clear import z80

def main():
 r=(ROOT/'input/original.sms').read_bytes();arrays={};portraits=[];texts={};p=0x7a09
 while p<0x7b2a:
  ins=z80.decode(r[p:p+8],p);raw=r[p:p+ins.len]
  if raw[:1]==b'\x21' and 0x8000<=int.from_bytes(raw[1:3],'little')<0xc000:
   pc=int.from_bytes(raw[1:3],'little');off=pc+0x4000;texts[pc]=r[off:r.index(0,off)+1]
  p+=ins.len
 lines=['#include <genesis.h>']
 for n in range(4):
  start=0x1c000+(int.from_bytes(r[0x1eb31+n*2:0x1eb33+n*2],'little')&0x3fff);v=bytearray(0x4000);end,length=rle_planes(r,start,v,0,4);stop,tm,_=map_decode(r,end);assert 0<length<=2048
  arrays[f'spell_teacher_portrait{n}_rle']=r[start:end];arrays[f'spell_teacher_portrait{n}_map']=tm[:128];portraits.append(dict(start=start,rle_end=end,map_end=stop,decoded_pattern_bytes=length))
 text=bytearray();offsets=[]
 for pc,data in sorted(texts.items()):offsets.append([pc,len(text)]);text.extend(data)
 arrays['spell_teacher_text']=bytes(text)
 for name,data in arrays.items():lines+=['const u8 '+name+'[] = {']+[' '+','.join(f'0x{v:02x}' for v in data[i:i+16])+',' for i in range(0,len(data),16)]+['};']
 for kind in ['rle','map']:lines+=['const u8 *const spell_teacher_portraits_'+kind+'[] = {'+','.join(f'spell_teacher_portrait{n}_{kind}' for n in range(4))+'};']
 lines+=['const u16 spell_teacher_text_index[][2] = {']+[' {'+','.join(map(str,row))+'},' for row in offsets]+['};','const u16 spell_teacher_text_count='+str(len(offsets))+';']
 assert len(texts)==22
 (ROOT/'megadrive/src/spell_teacher_data.c').write_bytes(('\n'.join(lines)+'\n').encode())
 report=dict(source_sha256=sha(r),portraits=portraits,text_index=offsets,towns=list(r[0x79fd:0x7a01]),node=dict(room=0xbf,coordinate=0x1dc,x=136,y=56,service=3),source_policy=[0x7a09,0x7b30],source_dispatch=0x79da,native_implemented=True)
 (ROOT/'analysis/spell_teacher_assets.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print(report)
if __name__=='__main__':main()
