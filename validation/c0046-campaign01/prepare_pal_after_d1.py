"""Continue the existing cold PAL candidate campaign after its first crystal."""
import ast
from pathlib import Path
root=Path(__file__).resolve().parents[2];project=root/'validation/c0046-campaign01/isolated/project'
text=(project/'tools/continue_after_d1_c0046.py').read_text()
text=text.replace('c0046','palc0046').replace('v317','PAL c0046').replace('V317','PAL c0046')
text=text.replace("prior = 'md-auto-c46-d1-exit02'", "prior = 'md-pal-c46-d1-exit02'")
text=text.replace("COMMON = ['--assisted-prefix'", "COMMON = ['--pal','--assisted-prefix'")
text=text.replace("'md-auto-' if family == COMBAT else 'md-'", "'md-pal-' if family in (COMBAT,ROUTE) else 'md-'")
text=text.replace("'md-auto-'+trial", "'md-pal-'+trial")
text=text.replace("'md-palc0046-", "'md-pal-palc0046-")
text=text.replace("current='md-pal-palc0046-fairy-service01'", "current='md-palc0046-fairy-service01'")
text=text.replace("['--boss-room','0x144','--world-route'", "['--pal','--boss-room','0x144','--world-route'")
assert text.count("prior = 'md-pal-c46-d1-exit02'")==1
assert "'md-auto-'" not in text
text=text.replace("if __name__=='__main__': main()", """if __name__=='__main__':
    from campaign_stream_replay import streamed_replays
    with streamed_replays(helper,ROOT/'validation/palc0046-after-d1-cold-stream'):
        main()
""")
text=text.replace("names = ('continue_after_d1_palc0046.py'", "names = ('campaign_stream_replay.py','cold_replay_stream.py','run_core.py','continue_after_d1_palc0046.py'")
ast.parse(text)
target=project/'tools/continue_after_d1_palc0046.py';assert not target.exists();target.write_text(text,encoding='utf-8')
print('PAL axe, fairy and D2 entry controller prepared; real source prices/resources and cold replay retained')
