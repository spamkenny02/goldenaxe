"""Continue the verified current cold campaign into D7 with ordinary resources."""
import argparse,shutil
from cold_replay_stream import ReplayStream
import json
import subprocess
import sys
from pathlib import Path

from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from run_core import ROOT
from validate_playable_sprite_limit import symbols


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--trial', default='02')
    args = parser.parse_args()
    assert args.trial.isalnum()
    prior = json.loads(evidence(ROOT/'analysis/d6_campaign_v0317_report.json'))
    assert prior['passed'] and prior['sixth_crystal_and_exterior_return']
    digest = sha((ROOT/'gaw-megadrive.bin').read_bytes())
    assert prior['md_sha256'] == digest
    prefix = prior['stages'][-1]['trace'].removeprefix('validation/')
    assert prefix.startswith('natural-dungeon-combat/')
    prefix = prefix.split('/')[-1]
    end = dict(prior['stages'][-1])
    endpoint = end['trace'] + f'/ram_{end["frames"]:05d}.bin'
    raw = evidence(ROOT/endpoint)
    assert sha(raw) == prior['evidence'][endpoint]
    sy = symbols(ROOT/'megadrive/out/release/symbol.txt')
    def word(name):
        return int.from_bytes(bytes(raw[(sy[name]+i)^1] for i in range(2)), 'big')
    for key, symbol in [('health','hero_health'),('max_health','hero_max_health'),('keys','hero_keys')]:
        assert end[key] == word(symbol)
    end['gold'] = word('hero_gold')
    assert end['room'] == 0x8b and end['health'] > 0
    trial = 'v0317-d7-' + args.trial
    out = ROOT/'validation'/('run-' + trial)
    out.mkdir(exist_ok=False)
    source_index={}
    for name in ('continue_d7_funded_v0317.py','natural_house_service.py','recipes/d7-preparation-v0310.jsonl','assisted_boss_route.py','assisted_prefix.py','natural_dungeon_route.py','natural_dungeon_combat.py','natural_earth_passage.py','natural_merchant_purchase.py','natural_free_healer.py','cold_replay_stream.py','run_core.py'):
        target=out/name.split('/')[-1];shutil.copyfile(ROOT/'tools'/name,target);source_index['tools/'+name]=sha(target.read_bytes())
    (out/'source_index.json').write_text(json.dumps(source_index,indent=2)+'\n')
    stream=ReplayStream(out/'cold-stream')
    try:
        points = []

        def load(path):
            return json.loads(evidence(path))

        def run(tool, arguments):
            command = [sys.executable, '-u', str(ROOT/'tools'/tool), *arguments]
            print('START', tool, *arguments, flush=True)
            with (out/'commands.jsonl').open('ab') as journal:
                journal.write((json.dumps(dict(tool=tool, sha256=sha((ROOT/'tools'/tool).read_bytes()),
                                              arguments=arguments))+'\n').encode())
            subprocess.run(command, cwd=ROOT, check=True)

        def canonical(family, name, gate):
            folder = ROOT/'validation'/family/name
            cap = load(folder/'capture.json')
            report = load(folder/('route_report.json' if family == 'natural-dungeon-route' else 'report.json'))
            assert cap['rom_sha256'] == digest and cap['sram_input'] is None
            assert report['failure'] is None and report[gate] and not report.get('deaths', 0)
            stream.prove(family+'/'+name)
            proof_folder = folder.with_name(name+f'-assisted-fixed-replay-{cap["frames"]}')
            proof = load(proof_folder/'replay_report.json')
            assert proof['passed'] and proof['rom_sha256'] == digest
            assert proof['whole_ram_bytes'] == 65536 and proof['final_png_exact']
            for stem, ext in (('ram','bin'), ('frame','png')):
                filename = f'{stem}_{cap["frames"]:05d}.{ext}'
                assert evidence(folder/filename) == evidence(proof_folder/filename)
            points.append(dict(trace=folder.relative_to(ROOT).as_posix(), frames=cap['frames'], gate=gate))
            (out/'verified_endpoints.json').write_text(json.dumps(points, indent=2)+'\n')
            return cap

        common = ['--boss-room','0x1b8','--planner','ordinary','--world-route',
                  '--assisted-prefix','--live-room-replan','--live-prefix-terrain','--rope-terrain','--axe-terrain']
        episode = ['--new-assistance-episode']
        cap = load(ROOT/'validation/natural-dungeon-combat'/prefix/'capture.json')
        route_prefix = ['--prefix-combat',prefix]
        health, maximum = end['health'], end['max_health']
        if end['keys']<1 and end['gold']<60:
            assert 50<=end['gold']<60
            name='md-'+trial+'-gold-route'
            run('assisted_boss_route.py',common+episode+route_prefix+['--house-outside','0xb5','--house-target','0x3f','--frames',str(cap['frames']+12000),'--trial',trial+'-gold-route'])
            cap=canonical('natural-dungeon-route',name,'reached_entrance')
            run('natural_house_service.py',['--prefix',name,'--assisted-prefix','--outside','0xb5','--kind','gold','--gold-gain','10','--trial',trial+'-gold10'])
            name='md-'+trial+'-gold10';cap=canonical('natural-service-route',name,'passed')
            gift=load(ROOT/'validation/natural-service-route'/name/'report.json')
            assert gift['last_state']['gold']-gift['first_state']['gold']==10 and not gift['new_assistance_writes']
            end['gold']=gift['last_state']['gold'];health=gift['last_state']['health']
            route_prefix=['--prefix-service',name];episode=[]
        if end['keys'] < 1:
            # The first D7 key room consumes a key before returning one. Buy an
            # actual key first; prices and available money come from the game.
            assert end['gold'] >= 40, 'Earn ordinary funds before buying the required D7 entry key'
            outside, house = ('0x94','0') if end['gold'] >= 60 else ('0xa5','0x2f')
            name = 'md-' + trial + '-key-shop-route'
            run('assisted_boss_route.py', common+episode+route_prefix+[
                '--house-outside',outside,'--house-target',house,'--frames',str(cap['frames']+12000),
                '--trial',trial+'-key-shop-route'])
            canonical('natural-dungeon-route', name, 'reached_entrance')
            extra = ['--heal-after'] if outside == '0x94' else []
            run('natural_merchant_purchase.py', ['--prefix',name,'--outside',outside,'--count','1',
                '--trial',trial+'-buy-key','--assisted-prefix',*extra])
            name = 'md-' + trial + '-buy-key'
            cap = canonical('natural-service-route', name, 'passed')
            service = load(ROOT/'validation/natural-service-route'/name/'report.json')
            assert service['last_state']['keys'] == service['first_state']['keys']+1
            assert not service['new_assistance_writes'] and not service['currency_or_inventory_fixtures']
            health, maximum = service['last_state']['health'], service['last_state']['max_health']
            route_prefix = ['--prefix-service',name]
            episode = []
        if health < maximum:
            name = 'md-' + trial + '-healer-route'
            run('assisted_boss_route.py', common+episode+route_prefix+[
                '--house-outside','0x94','--house-target','0','--frames',str(cap['frames']+12000),
                '--trial',trial+'-healer-route'])
            canonical('natural-dungeon-route', name, 'reached_entrance')
            run('natural_free_healer.py', ['--prefix',name,'--trial',trial+'-heal','--assisted-prefix'])
            name = 'md-' + trial + '-heal'
            cap = canonical('natural-service-route', name, 'passed')
            route_prefix = ['--prefix-service',name]
            episode = []
        name = 'md-' + trial + '-entry'
        run('assisted_boss_route.py', common+episode+route_prefix+['--door-index','7',
            '--frames',str(cap['frames']+12000),'--trial',trial+'-entry'])
        cap = canonical('natural-dungeon-route', name, 'reached_entrance')
        proposal = ROOT/'tools/recipes/d7-preparation-v0310.jsonl'
        raw = evidence(proposal)
        commands = [json.loads(line) for line in raw.splitlines() if line.strip()]
        wanted = ['v0310-d7-healed-'+suffix for suffix in ('key01','key03','earth01','earth02')]
        route_commands = []
        for old_trial in wanted:
            matches = [row for row in commands if 'tools/assisted_boss_route.py' in row
                       and '--trial' in row and row[row.index('--trial')+1] == old_trial]
            assert len(matches) == 1, (old_trial, len(matches))
            route_commands.append(matches[0])
        (out/'historical_proposal.json').write_text(json.dumps(dict(path=proposal.relative_to(ROOT).as_posix(),
            sha256=sha(raw), scope='Input itinerary proposal only; never old primary state or resources.'),indent=2)+'\n')
        for index, command in enumerate(route_commands):
            old = command[command.index('tools/assisted_boss_route.py')+1:]
            current = [token.replace('v0310-d7-healed-',trial+'-') for token in old]
            if index == 0:
                current[current.index('--prefix')+1] = name
            current[current.index('--frames')+1] = str(cap['frames']+12000)
            run('assisted_boss_route.py', current)
            selected_trial = current[current.index('--trial')+1]
            gate = 'earth_route_passed' if '--earth-action-only' in current else 'new_key_verified'
            cap = canonical('natural-dungeon-combat', 'md-auto-'+selected_trial, gate)
        print('D7 preparation endpoints verified:', len(points), flush=True)
    finally:stream.close()


if __name__ == '__main__':
    main()
