"""Bind the tested first-crystal controls to the published v314 cartridge."""
import json
from run_core import ROOT
from archive_lossless_evidence import sha
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols


def main():
    refs={}
    def read(p):
        raw=p.read_bytes();refs[p.relative_to(ROOT).as_posix()]=sha(raw);return raw
    def load(p):return json.loads(read(p))
    digest=sha(read(ROOT/'gaw-megadrive.bin'))
    candidate=load(ROOT/'analysis/intro_audio_candidate11_game_v0313_report.json')
    assert candidate['passed'] and candidate['first_crystal_and_exterior_return_verified']
    assert candidate['md_sha256']==digest
    p=ROOT/'validation/natural-dungeon-combat/md-auto-v0314-d1-cold01'
    c=load(p/'capture.json');r=load(p/'report.json');f=c['frames'];a,w=recording(p,c)
    sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
    assert r['passed'] and r['failure'] is None and not r['deaths']
    assert c['rom_sha256']==r['md_sha256']==digest and c['sram_input'] is None
    assert r['terminal_png_exact'] and not r['terminal_field_mismatches']
    assert r['full_dungeon_cleared'] and r['dungeon_exit_verified']
    assert len(a['episodes'])==1 and not a['primary_state_imports'] and not a['health_refills'] and not a['boss_assistance']
    release=a['release_write_frame'];first=a['first_boss_combat']
    assert first['hurt']==0 and release<first['frame']
    assert all(addr==sy['hero_hurt'] and value in (b'\0\0',b'\0\x81') and t<=release for t,addr,value in w)
    proof=p.with_name(p.name+'-assisted-fixed-replay-'+str(f));q=load(proof/'replay_report.json')
    assert q['passed'] and q['whole_ram_bytes']==65536 and q['final_png_exact'] and not q['feedback_reads']
    assert q['rom_sha256']==digest and q['first_boss_combat']==first
    for name,h in q['evidence'].items():assert sha(read(p/name))==h
    for stem,ext in [('ram','bin'),('frame','png')]:
        assert read(p/f'{stem}_{f:05d}.{ext}')==read(proof/f'{stem}_{f:05d}.{ext}')
    raw=read(p/f'ram_{f:05d}.bin')
    data=lambda n,k:bytes(raw[(sy[n]+i)^1]for i in range(k))
    word=lambda n:int.from_bytes(data(n,2),'big')
    assert word('room_id')==0xb9 and word('world_dungeon_number')==0 and word('game_state')==12
    assert 0<word('hero_health')<=word('hero_max_health')==32 and not word('sound_unhandled_command')
    assert data('game_save_state',592)[0x1f:0x28]==bytes([128]+[0]*8)
    assert data('hero_items',17)==bytes(17)
    born=read(p/f'ram_{first["frame"]+1:05d}.bin')
    actors=bytes(born[(sy['world_actor_state']+i)^1]for i in range(768))
    source=read(ROOT/'input/original.sms');kind=source[0x3234e+0x175*8]
    assert kind==0x68 and actors[0]==kind and actors[24]==source[0x320ea+(kind-0x20)*4]
    result=dict(passed=True,version=314,md_sha256=digest,first_crystal_and_exit_verified=True,
        current_campaign_trace=p.relative_to(ROOT).as_posix(),campaign_frames=f,
        release_frame=release,first_boss_combat=first,primary_state_imports=0,
        resource_writes=0,whole_ram_bytes=65536,final_png_exact=True,evidence=refs,
        full_game_validated=False,limits=['Fixed controller recording from the byte-identical tested candidate, replayed from boot on the public cartridge. Only logged approach hurt guards; no new writes in the boss or return.',
        'This checkpoint has the first crystal; axe, oil, later dungeons and global source fidelity are outside this report.'])
    (ROOT/'analysis/d1_campaign_v0314_report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('Published v314 first crystal, source boss birth and exterior return audited')


if __name__=='__main__':main()
