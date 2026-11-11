"""Save and Continue at reached service locations, in separate cold branches.

Each branch starts from the selected real entrance in the refusal tour. It
does not turn a saved-game reload into part of the uninterrupted campaign.
"""
import json
from run_core import ROOT
from continue_sms_npc_d4 import invoke,checked,SERVICE


def main():
    output=ROOT/'analysis/sms_save_locations_campaign.json'
    previous=json.loads(output.read_bytes()) if output.exists() else {}
    completed=previous.get('completed_locations',[])
    tour=json.loads((ROOT/'analysis/sms_service_refusal_campaign.json').read_bytes())
    visits=[r for r in tour['completed_visits'] if r['kind']=='save']
    def save():
        output.write_text(json.dumps(dict(
            status='all_fourteen_save_locations_written_replayed_and_loaded' if len(completed)==14 else 'partial_locations_verified',
            completed_locations=completed,expected_locations=14,separate_persistence_branches=True,
            synthetic_fixtures=False,all_npcs_complete=False),indent=2)+'\n')
    for visit in visits:
        outside=visit['outside']
        if any(r['outside']==outside for r in completed):continue
        if outside==0x2e:
            trace=SERVICE+'/sms-npc-save-2e-slot0-01'
            continued='sms-save-continue/2e-slot0-01'
        else:
            refusal=json.loads((ROOT/'validation'/visit['trace']/'report.json').read_bytes())
            entry=refusal['source_prefix'];trial=f'npc-save-location-{outside:02x}-slot0-01'
            name='sms-'+trial;trace=SERVICE+'/'+name
            if not (ROOT/'validation'/trace).exists():
                invoke('run_sms_dialogue_observed.py',['sms_save_service','--dialogue-core',
                    str(ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_sms_dialogue03_libretro.dll'),
                    '--sms','--assisted-prefix','--prefix',entry,'--trial',trial,'--slot','0'],trial)
            continued=f'sms-save-continue/location-{outside:02x}-slot0-01'
        checked(SERVICE,trace.split('/')[1],lambda r:r['passed'])
        attempt=1;base=continued
        while (ROOT/'validation'/continued/'report.json').exists() and not json.loads((ROOT/'validation'/continued/'report.json').read_bytes())['passed']:
            attempt+=1;continued=base+f'-retry{attempt:02d}'
        if not (ROOT/'validation'/continued/'report.json').exists():
            invoke('sms_continue_written_save.py',['--trace',trace,'--trial',continued.split('/')[1]],f'save-continue-{outside:02x}')
        loaded=json.loads((ROOT/'validation'/continued/'report.json').read_bytes())
        assert loaded['passed'] and loaded['source_save_fixed_replayed'] and not loaded['synthetic_sram_fixture']
        completed.append(dict(outside=outside,save_trace=trace,continue_report='validation/'+continued+'/report.json',
            slot=0,all_reload_checks=loaded['checks'],sram_sha256=loaded['source_sram_sha256']))
        save();print('ACTUAL SAVE AND CONTINUE VERIFIED',hex(outside),flush=True)
    save()


if __name__=='__main__':main()
