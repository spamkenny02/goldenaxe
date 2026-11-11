"""Overwrite a real slot after a genuine gold gift, then normally Continue it."""
import hashlib,json
from run_core import ROOT
from sms_campaign_runner import Campaign
from sms_campaign_navigation import enter
from continue_sms_npc_d4 import invoke,checked,SERVICE


def main():
    output=ROOT/'analysis/sms_save_overwrite_report.json'
    if output.exists() and json.loads(output.read_bytes()).get('passed'):return
    initial='natural-service-route/sms-npc-save-2e-slot0-01'
    old_sram=(ROOT/'validation'/initial/'game-written.srm').read_bytes();old_payload=old_sram[0x400:0x650]
    resume='natural-service-route/sms-npc-save-overwrite-fund01'
    c=Campaign(resume if (ROOT/'validation'/resume/'report.json').exists() else initial,0x15e,'npc-save-overwrite');closed=False
    try:
        c.verify(lambda r:r['passed'])
        if not c.raw()[0x15d]&2:
            n=enter(c,0x5d,0x3f,'fund')
            c.service(f'fund{n:02d}','natural_house_service',['--outside','0x5d','--kind','gold','--gold-gain','10'])
        n=enter(c,0x2e,0,'save')
        entry=c.current;c.close();closed=True
        trial=f'npc-save-overwrite-2e-slot0-{n:02d}';name='sms-'+trial;trace=SERVICE+'/'+name
        if not (ROOT/'validation'/trace).exists():
            invoke('run_sms_dialogue_observed.py',['sms_save_service','--dialogue-core',
                str(ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_sms_dialogue03_libretro.dll'),
                '--sms','--assisted-prefix','--prefix',entry,'--trial',trial,'--slot','0'],trial)
        checked(SERVICE,name,lambda r:r['passed'])
        new_sram=(ROOT/'validation'/trace/'game-written.srm').read_bytes();new_payload=new_sram[0x400:0x650]
        assert old_payload!=new_payload and new_payload[0x2d]>old_payload[0x2d]
        continuation='overwrite-2e-slot0-01';path=ROOT/'validation/sms-save-continue'/continuation/'report.json'
        if not path.exists():invoke('sms_continue_written_save.py',['--trace',trace,'--trial',continuation],'overwrite-continue')
        loaded=json.loads(path.read_bytes());assert loaded['passed']
        output.write_text(json.dumps(dict(passed=True,slot=0,first_save_trace=initial,second_save_trace=trace,
            original_payload_sha256=hashlib.sha256(old_payload).hexdigest(),replacement_payload_sha256=hashlib.sha256(new_payload).hexdigest(),
            old_gold=old_payload[0x2d],new_gold=new_payload[0x2d],continue_report=path.relative_to(ROOT).as_posix(),
            synthetic_fixtures=False,progression_changed_by_actual_gold_gift=True),indent=2)+'\n')
        print('ACTUAL SAVE OVERWRITE AND CONTINUE VERIFIED',flush=True)
    finally:
        if not closed:c.close()


if __name__=='__main__':main()
