"""Prepare PAL D9 from real eight-crystal resources, paid exit and Bell crossing."""
import ast
from pathlib import Path
root=Path(__file__).resolve().parents[2];project=root/'validation/c0046-campaign01/isolated/project'
s=(root/'validation/pal318-d9-entry02/run.py').read_text().replace('pal318','palc0046').replace('continue_d8_entry_v0317','continue_d8_entry_palc0046').replace('continue_d9_entry_v0317','continue_d9_entry_palc0046').replace('pal_d8_campaign_v0318_report.json','palc0046_d8_report.json').replace("receipt['eighth_crystal_and_exterior_return']","receipt['actual_eighth_crystal_and_exterior']").replace("receipt['md_sha256']","receipt['rom_sha256']")
s=s.replace('helper.EVIDENCE=Path(__file__).resolve().parent',"helper.EVIDENCE=helper.ROOT/'validation/palc0046-d9-entry-sources'")
s=s.replace('    snapshot.mkdir()', '    snapshot.mkdir(parents=True,exist_ok=False)',1)
s=s.replace("helper.STREAM=ReplayStream(helper.EVIDENCE/'cold-stream')", "helper.EVIDENCE.mkdir(exist_ok=False)\n    helper.STREAM=ReplayStream(ROOT/'validation/palc0046-d9-entry-cold-stream01')")
s=s.replace('helper.COMMON=["--pal",*helper.COMMON]','helper.COMMON=["--wake-sentinels","--retry-isolated-foes","--isolated-retry-limit","12",*helper.COMMON]')
marker="    route='palc0046-d9-paid1a-route01'"
extra="""    # A real B5 gift funds the ten-piece return passage only when needed.
    if receipt['stages'][-1].get('gold',0)<10:
        from validate_playable_sprite_limit import symbols
        sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
        raw=evidence(ROOT/'validation'/COMBAT/source/f'ram_{cap["frames"]:05d}.bin')
        assert not raw[(sy['game_save_state']+0x50+0xb5)^1]&2,'B5 gift must be unclaimed'
        gift_route='palc0046-d9-goldb5-route01'
        run('assisted_boss_route.py',[*world,*origin,'--house-outside','0xb5','--house-target','0x3f','--frames',budget(family,source,18000),'--trial',gift_route])
        replay(ROUTE,'md-pal-'+gift_route,lambda r:r['reached_entrance'])
        gift='palc0046-d9-goldb5-service01'
        run('natural_house_service.py',['--assisted-prefix','--prefix','md-pal-'+gift_route,'--outside','0xb5','--kind','gold','--gold-gain','10','--trial',gift])
        replay(SERVICE,'md-'+gift,lambda r:r['passed'] and r['last_state']['gold']-r['first_state']['gold']==10 and not r['new_assistance_writes'])
        family,source=SERVICE,'md-'+gift;origin=['--prefix-service',source]
"""
assert marker in s;s=s.replace(marker,extra+marker)
p=project/'tools/continue_d9_entry_palc0046.py';assert not p.exists();ast.parse(s);p.write_text(s)
print('PAL D9 prepared: actual funds and unclaimed gift checked; execution requires audited D8 return')
