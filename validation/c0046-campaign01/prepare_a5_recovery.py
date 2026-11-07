"""Reach the source A5 shop by clearing its enemies before approaching its door."""
from pathlib import Path
root=Path(__file__).resolve().parents[2]
project=root/'validation/c0046-campaign01/isolated/project'
tools=project/'tools'
def save(name,text):
    p=tools/name;assert not p.exists(),p;p.write_text(text,encoding='utf-8')

game=(root/'tools/natural_dungeon_combat.py').read_text()
assert game.count("'validation/natural-dungeon-route'")==1
game=game.replace("'validation/natural-dungeon-route'","'validation/natural-service-route'")
game=game.replace('assert itinerary and 256<=itinerary[0]<512','assert itinerary and itinerary==[0xb5,0xa5], "This exterior adapter is restricted to the A5 source shop approach"')
save('natural_combat_from_service_c0046.py',game)
approach=(root/'tools/assisted_boss_route.py').read_text()
before="family = 'natural-dungeon-combat' if flag == '--continuation' else 'natural-dungeon-route'"
assert approach.count(before)==1
approach=approach.replace(before,before.replace("else 'natural-dungeon-route'","else 'natural-service-route'"))
assert approach.count('game = beam.generic.base.game')==1
approach=approach.replace('game = beam.generic.base.game','import natural_combat_from_service_c0046 as game')
save('assisted_combat_from_service_c0046.py',approach)

text=(tools/'continue_d7_funded_c0046.py').read_text()
begin=text.index("    prefix = 'natural-dungeon-combat/'+prior['stages'][-1]['trace'].split('/')[-1]")
end=text.index("    trial = 'c0046-d7-'",begin)
text=text[:begin]+"""    prefix='md-c0046-d7-02-gold10'
    origin=ROOT/'validation/natural-service-route'/prefix
    cap=json.loads((origin/'capture.json').read_bytes());frame=cap['frames']
    proof=origin.with_name(prefix+f'-assisted-fixed-replay-{frame}')
    proof_report=json.loads((proof/'replay_report.json').read_bytes())
    assert proof_report['passed'] and proof_report['whole_ram_bytes']==65536 and proof_report['final_png_exact']
    raw=evidence(origin/f'ram_{frame:05d}.bin')
    assert raw==evidence(proof/f'ram_{frame:05d}.bin')
    assert cap['rom_sha256']==digest and cap['sram_input'] is None
    sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
    def word(name):return int.from_bytes(bytes(raw[(sy[name]+i)^1] for i in range(2)),'big')
    end={name:word(symbol) for name,symbol in [('health','hero_health'),('max_health','hero_max_health'),('gold','hero_gold'),('keys','hero_keys')]}
    assert word('room_id')==0xb5 and end['gold']==48 and not end['keys']
"""+text[end:]
text=text.replace("('run-' + trial)","('run-c0046-d7-recovered03-' + args.trial)")
text=text.replace("'continue_d7_funded_c0046.py',","'resume_d7_funded_c0046.py','natural_combat_from_service_c0046.py','assisted_combat_from_service_c0046.py',")
text=text.replace("episode = ['--new-assistance-episode']","episode = []")
text=text.replace("load(ROOT/'validation/natural-dungeon-combat'/prefix/'capture.json')","load(ROOT/'validation/natural-service-route'/prefix/'capture.json')")
text=text.replace("route_prefix = ['--prefix-combat',prefix]","route_prefix = ['--prefix-service',prefix]")
begin=text.index("        if end['keys']<1 and end['gold']<60:")
end=text.index("        if end['keys'] < 1:",begin)
text=text[:begin]+"""        run('assisted_combat_from_service_c0046.py',['--boss-room','0x1b8','--planner','ordinary',
            '--preserve-floor-hurt','--assisted-prefix','--prefix',prefix,'--rooms','0xb5,0xa5',
            '--target-room','0xa5','--frames',str(cap['frames']+18000),'--trial',trial+'-a5-clear01',
            '--max-deaths','0','--collision-aim','--settle-attacks','--equip-axe','--wake-sentinels',
            '--doorway-ranges','--ignore-inactive-actors','--retry-isolated-foes','--isolated-retry-limit','12'])
        name='md-auto-'+trial+'-a5-clear01';cap=canonical('natural-dungeon-combat',name,'room_cleared')
        cleared=load(ROOT/'validation/natural-dungeon-combat'/name/'report.json')
        assert cleared['last_state']['room']==0xa5 and cleared['last_state']['room_flags']&1
        raw=evidence(ROOT/'validation/natural-dungeon-combat'/name/f"ram_{cap['frames']:05d}.bin")
        assert raw[(sy['scratch']+0x800+0x83)^1]==4
        end['gold']=word('hero_gold');health=word('hero_health');maximum=word('hero_max_health')
        route_prefix=['--prefix-combat',name]
"""+text[end:]
before="outside, house = ('0x94','0') if end['gold'] >= 60 else ('0xa5','0x2f')"
assert text.count(before)==1
text=text.replace(before,"outside, house = '0xa5','0x2f'")
text=text.replace("'-key-shop-route'","'-key-shop-route02'")
save('resume_d7_funded_c0046.py',text)
print('A5 recovery prepared: ordinary combat opens the source shop; no ROM or terrain edits')
