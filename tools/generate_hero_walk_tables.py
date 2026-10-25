"""Export all six 3295 movement contexts, normal/boots, directly from the ROM."""
from run_core import ROOT
from archive_lossless_evidence import sha

def main():
 rom=(ROOT/'input/original.sms').read_bytes();assert sha(rom)=='852e068e331dbfb01b9c38a62eecf81ce5b9f0f1bd10fff497117bd885c716c9'
 data=rom[0x33db:0x34a7];assert len(data)==2*6*17
 out='/* Original3295: C041*17 + (C0EE ?3441:33DB). Generated from original.sms. */\n#include <types.h>\nconst u8 world_walk_tables[204] = {\n'
 for n in range(12):out+='    '+','.join(f'0x{x:02x}' for x in data[n*17:n*17+17])+',\n'
 out+='};\n';(ROOT/'megadrive/src/hero_walk_tables.c').write_bytes(out.encode())
 print('12 original terrain/boots movement rows exported')
if __name__=='__main__':main()
