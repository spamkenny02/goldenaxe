"""Audit normal A5 combat opening and entry, separate from D7 completion."""
import json,sys
from pathlib import Path
sys.path.insert(0,'tools')
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols
work=Path(__file__).resolve().parent;project=work/'isolated/project'
digest=sha((project/'gaw-megadrive.bin').read_bytes());sy=symbols(project/'megadrive/out/release/symbol.txt')
paths={Path(__file__).resolve(),work/'prepare_a5_recovery.py'}
def read(p):paths.add(p);return p.read_bytes()
def load(p):return json.loads(read(p))
failed=load(project/'validation/natural-dungeon-route/md-c0046-d7-02-key-shop-route/route_report.json')
assert failed['failure']=='no_waypoint_progress' and not failed['reached_entrance']
source=read(ROOT/'input/original.sms')
entry=int.from_bytes(source[0xb762+0xa5*2:0xb764+0xa5*2],'little')
assert entry==45507 and source[entry+8:entry+11]==bytes.fromhex('cdb15f')
stages=[]
for family,name,kind in [('natural-dungeon-combat','md-auto-c0046-d7-02-a5-clear01','clear'),('natural-dungeon-route','md-c0046-d7-02-key-shop-route02','entry')]:
    p=project/'validation'/family/name;c=load(p/'capture.json');r=load(p/('report.json' if kind=='clear' else 'route_report.json'))
    assert c['rom_sha256']==digest and c['sram_input'] is None and r['failure'] is None
    a,w=recording(p,c);assert not a['primary_state_imports'] and not a['health_refills'] and not a['boss_assistance']
    assert all(addr==sy['hero_hurt'] for _,addr,_ in w)
    f=c['frames'];proof=p.with_name(name+f'-assisted-fixed-replay-{f}');q=load(proof/'replay_report.json')
    assert q['passed'] and q['rom_sha256']==digest and q['whole_ram_bytes']==65536 and q['final_png_exact'] and not q['feedback_reads']
    for n,h in q['evidence'].items():assert sha(read(p/n))==h
    raw=read(p/f'ram_{f:05d}.bin')
    for stem,ext in [('ram','bin'),('frame','png')]:assert read(p/f'{stem}_{f:05d}.{ext}')==read(proof/f'{stem}_{f:05d}.{ext}')
    word=lambda n:int.from_bytes(bytes(raw[(sy[n]+j)^1] for j in range(2)),'big')
    assert word('hero_health')==80 and not word('sound_unhandled_command')
    if kind=='clear':
        assert r['room_cleared'] and not r['deaths'] and not r['last_actors']
        assert word('room_id')==0xa5 and raw[(sy['scratch']+0x883)^1]==4
        assert raw[(sy['game_save_state']+0xf5)^1]&1
    else:assert r['reached_entrance'] and r['directional_probe_succeeded'] and word('room_id')==0x2f
    stages.append(dict(trace=p.relative_to(ROOT).as_posix(),frames=f,kind=kind,room=word('room_id'),health=80,gold=word('hero_gold'),whole_ram_png_exact=True))
snapshot=project/'validation/run-c0046-d7-recovered03-02'
for name,h in load(snapshot/'source_index.json').items():assert sha(read(snapshot/Path(name).name))==h
result=dict(passed=True,candidate='c0046',rom_sha256=digest,hidden_shop_opened_by_ordinary_combat=True,stages=stages,
    scope='Cold campaign with declared approach hurt writes only. Source A5 clear suffix opens its hidden shop; actual combat, persistent flag, cell transformation and real doorway entry verified. No D7 boss or crystal claim.')
freeze(ROOT,ROOT/'analysis/c0046-a5-hidden-shop',paths,result,[work])
(ROOT/'analysis/a5_hidden_shop_c0046_report.json').write_text(json.dumps(result,indent=2)+'\n')
print('A5 source-triggered opening and entry verified',flush=True)
