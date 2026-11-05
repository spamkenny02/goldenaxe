"""Inspect original full-pool fan writes in an isolated SMS routine fixture."""
import contextlib,io,json
from pathlib import Path
from run_core import ROOT,run
from archive_lossless_evidence import sha

def main():
    original=(ROOT/'input/original.sms').read_bytes();rom_hash=sha((ROOT/'gaw-megadrive.bin').read_bytes())
    out=ROOT/'validation/full-pool-iy-v0314-source02';out.mkdir(exist_ok=False);cases=[]
    for iy in (0x8000,0xc6f0,0xc8d0,0xc900):
        image=bytearray(original);code=bytearray.fromhex('f331f0df2100c01101c001ff1f3600edb02100c61101c601ff0236a7edb0')
        def store(value,address):code.extend(bytes((0x3e,value,0x32,address&255,address>>8)))
        for value,address in ((0,0xfffc),(0,0xfffd),(1,0xfffe),(2,0xffff),(0x64,0xc600),(10,0xc601),(0,0xc604),(1,0xc60a),(96,0xc611),(128,0xc613),(60,0xc618),(0x5a,0xc90a)):
            store(value,address)
        code.extend(bytes((0xfd,0x21,iy&255,iy>>8,0xdd,0x21,0,0xc6,0xcd,0x6b,0x50)))
        store(0xa5,0xc002);end=0x3000+len(code);code.extend(bytes((0xc3,end&255,end>>8)))
        image[:3]=bytes((0xc3,0,0x30));image[0x3000:0x3000+len(code)]=code
        f=out/f'iy-{iy:04x}';f.mkdir();rom=f/'controlled-original-routine.sms';rom.write_bytes(image)
        with contextlib.redirect_stdout(io.StringIO()):run(rom,20,f,{20},[],skip_intro=False)
        raw=(f/'ram_00020.bin').read_bytes();assert len(raw)==8192 and raw[2]==0xa5,'Source routine did not return'
        cases.append(dict(incoming_iy=iy,fixture_sha256=sha(image),ram_sha256=sha(raw),actor5_direction=raw[0x6fa],last_projectile_direction=raw[0x8da],after_pool_byte=raw[0x90a],boss_state=raw[0x601],pool_types=[raw[0x780+i*48]for i in range(8)]))
    assert sha((ROOT/'gaw-megadrive.bin').read_bytes())==rom_hash
    report=dict(passed=True,version=314,md_sha256=rom_hash,original_sms_sha256=sha(original),original_routine=0x506b,original_instructions_changed=False,cases=cases,native_comparison_performed=False,natural_gameplay_proof=False,scope='Controlled SMS unit fixture only. Program initializes RAM and calls the unmodified original routine with a full projectile pool. No campaign state is imported and the production MD ROM is unchanged.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
