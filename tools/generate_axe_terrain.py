"""Export original exterior axe mutation records at3620..3634."""
from run_core import ROOT
from archive_lossless_evidence import sha

def main():
 r=(ROOT/'input/original.sms').read_bytes();assert sha(r)=='852e068e331dbfb01b9c38a62eecf81ce5b9f0f1bd10fff497117bd885c716c9'
 data=r[0x3620:0x3635];assert len(data)==21 and data[-1]==0
 out='/* Original358D table: before,after,paired below before,after. */\n#include <types.h>\nconst u8 world_axe_terrain[21] = {'+','.join(f'0x{x:02x}' for x in data)+'};\n'
 (ROOT/'megadrive/src/axe_terrain_data.c').write_bytes(out.encode())
if __name__=='__main__':main()
