"""Execute original SMS capture then damage with a simultaneous lethal hit.

This isolated fixture is separate from the playable campaign. It tests source
ordering only, not whether a particular natural SMS fight reaches the setup.
"""
import contextlib
import io
import json
from run_core import ROOT, run
from archive_lossless_evidence import sha


def main():
    original = (ROOT/'input/original.sms').read_bytes()
    image = bytearray(original)
    code = bytearray.fromhex('f331f0df2100c01101c001ff1f3600edb0')
    def store(address, value):
        code.extend(bytes([0x3e,value,0x32,address&255,address>>8]))
    store(0xfffc,0);store(0xfffd,0);store(0xfffe,1);store(0xffff,2)
    for address,value in [(0xc300,1),(0xc301,5),(0xc304,0),(0xc311,80),(0xc313,128),
                          (0xc318,56),(0xc0dd,8),(0xc600,0x5b),(0xc601,10),(0xc603,0x2b),
                          (0xc611,80),(0xc613,128),(0xc618,6),(0xc61a,2),(0xc61d,6),
                          (0xc61e,0),(0xc61f,0xc3),(0xc621,16)]:
        store(address,value)
    code.extend(bytes.fromhex('dd2100c6cd4350cd6827'))
    store(0xc080,0xa5)
    loop=0x3000+len(code)
    code.extend(bytes([0xc3,loop&255,loop>>8]))
    assert len(code)<512
    image[:3]=bytes.fromhex('c30030');image[0x3000:0x3000+len(code)]=code
    out=ROOT/'validation/thief-lethal-capture-source-v0304'
    assert not out.exists()
    out.mkdir(parents=True)
    fixture=out/'source.sms';fixture.write_bytes(image)
    with contextlib.redirect_stdout(io.StringIO()):
        run(fixture,10,out/'run',{10},[],skip_intro=False)
    ram=(out/'run/ram_00010.bin').read_bytes()
    assert ram[0x80]==0xa5
    result=dict(original_sha256=sha(original),fixture_sha256=sha(image),
                original_entry_calls=['5043 thief behavior','2768 queued damage'],
                injected_setup=True,playable_campaign_modified=False,
                hero_state=ram[0x301],hero_health=ram[0x318],
                actor_type=ram[0x600],actor_state=ram[0x601],actor_hp=ram[0x618],
                actor_previous_type=ram[0x607],
                source_retains_grab_after_lethal_capture=ram[0x301]==12 and ram[0x600]==1,
                natural_source_reproduction=False)
    assert result['source_retains_grab_after_lethal_capture'] and result['actor_previous_type']==0x5b
    (out/'source_report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
