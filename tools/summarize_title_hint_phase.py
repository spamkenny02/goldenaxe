"""Release-scoped summary of unselected title HINT timing research."""
from pathlib import Path
from compression import zstd
import hashlib,json,struct
ROOT=Path(__file__).resolve().parents[1];v=ROOT/'validation'
correct=json.loads((v/'title-wait-phase-model07/report.json').read_text());before=json.loads((v/'title-wait-phase-model03/report.json').read_text());assert correct['passed'] and not before['passed'];summaries=[]
for r in correct['results']:
 region=r['region'];old=next(x for x in before['results'] if x['region']==region);cases=r['cases'];assert len(cases)==79 and all(x['deadline_exact'] and x['audio_state_exact'] and x['irq_ram_exact'] for x in cases)
 first=[x for x in cases if x['first_logo_outi_exact'] is not None];assert len(first)==1 and first[0]['first_logo_outi_exact']
 p=v/('title-irq-snapshots-'+region+'07');capture=json.loads((p/'report.json').read_text());assert capture['vdp_reg0']==0x16 and capture['vdp_reg10']==187
 raw=zstd.decompress((p/'snapshots.bin.zst').read_bytes());records=[(struct.unpack_from('<8Q',raw,n),raw[n+64:n+400]) for n in range(0,len(raw),800)];hints=[];dispatches=0
 for i,(h,ram) in enumerate(records):
  if h[0]!=0x25e:continue
  dispatches+=1;entry=records[i-1][0];assert entry[0]==0x38
  assert int.from_bytes(ram[0x2c:0x2e],'little')==0x280
  end=next((x[0] for x in records[i+1:] if x[0][0]==0x137),None)
  if end is None:continue
  work=(end[2]-entry[2])//15-72+13
  assert work==691;hints.append(work)
 assert len(hints)==79 and dispatches==80
 summaries.append(dict(region=region,wait_cases=len(cases),exact_deadlines=len(cases),exact_irq_ram_cases=len(cases),exact_audio_ram_cases=len(cases),ordinary_vint_only_model_exact_deadlines=sum(x['deadline_exact'] for x in old['cases']),ordinary_model_wait_master_tick_deltas=sorted({x['wait_master_delta'] for x in old['cases']}),observed_horizontal_irq_dispatches=dispatches,paired_horizontal_irq_work_cases=len(hints),horizontal_irq_tstates=691,callback='0280',line=187,vdp_reg0='16',vdp_reg10=187,first_logo_outi_predictions=[dict(raster=x['first_logo_outi_raster'],exact=x['first_logo_outi_exact']) for x in first],capture_sha256=hashlib.sha256((p/'snapshots.bin.zst').read_bytes()).hexdigest()))
module=ROOT/'megadrive/src/source_title_wait.c';native=json.loads((v/'title-wait-phase-native02/report.json').read_text());assert native['passed'] and native['source_sha256']==hashlib.sha256(module.read_bytes()).hexdigest()
report=dict(passed=True,public_version=321,public_md_sha256=hashlib.sha256((ROOT/'gaw-megadrive.bin').read_bytes()).hexdigest(),public_rom_unchanged=True,selected_in_game=False,module='megadrive/src/source_title_wait.c',module_sha256=hashlib.sha256(module.read_bytes()).hexdigest(),source_sha256=hashlib.sha256((ROOT/'input/original.sms').read_bytes()).hexdigest(),results=summaries,native_compile=native,model='Original B95 prefix and polling, semantic native full IRQ/audio, plus title HINT0280 at line187 (691T/84fetches). Stable polls batch only before both interrupt deadlines. No calibrated NOP delay.',logo_first_outi_continuation='BB3 restore149T + input check31T + map/address setup131T =311T before first038E instruction entry.',limits=['Host-native deadline/state equivalence on158 waits; m68000 compile verified, no physicalMD runtime scheduler selected.','Title HINT timing modeled but its CRAM16 write is not physically rendered by this helper.','Only mode4/192 title callback0280, line187, empty video queue/no pending tile request and readerDE4 in these captures.','Initial refresh register is0; no M1/R equivalence or gameplay/randomness certification.','Whole source clock composition cost on actual68k remains a separate performance constraint.','V321 still has262 differing pixels on the partial logo frame. Prior private raster trial has20. Neither is changed by this model-only commit.'],next_action='Use the validated native wait/continuation dates in a title-specific physicalVDP scheduler, including source byte writes and HINT palette effect; validate rendered PAL/NTSC title and sound before selecting a new ROM.')
assert report['public_md_sha256']=='89c5833351312ffaa591efb1939161910a298af06437080e2cf84fb3fb8ac86e'
(ROOT/'analysis/title_hint_phase_v0321_report.json').write_text(json.dumps(report,indent=2)+'\n')
print('158 complete waits and160 HINT dispatches summarized; public V321 unchanged.')
