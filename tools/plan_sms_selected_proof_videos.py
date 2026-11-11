"""Deduplicate selected proof branches by exact boot inputs and RAM-write events.

This plans clips; it does not certify unseen NPCs or turn a branch into a video.
"""
import argparse,hashlib,json
import numpy as np
from run_core import ROOT,compile_fixed_inputs


def timeline(trace):
    folder=ROOT/'validation'/trace
    cap=json.loads((folder/'capture.json').read_bytes());end=cap['frames']
    assert cap['sram_input'] is None
    presses=list(map(tuple,cap['presses']))
    rows=json.loads((folder/'controls.json').read_bytes())
    for i,row in enumerate(rows):
        last=rows[i+1]['frame']-1 if i+1<len(rows) else end
        presses.extend((row['frame'],min(last,end),b) for b in row['buttons'] if row['frame']<=end)
    masks=np.asarray(compile_fixed_inputs(presses,end),dtype=np.uint32)
    name='controlled_economic_assistance.json' if (folder/'controlled_economic_assistance.json').exists() else 'assistance.json'
    aid=json.loads((folder/name).read_bytes())
    for row in aid['writes']:
        frame,addr,value=row['frame'],row['address'],int.from_bytes(bytes.fromhex(row['data_hex']),'little')
        if frame>end:continue
        assert addr in (0x305,0xdd)
        if addr==0x305:
            assert value in (0,129);masks[frame]|=np.uint32((value+1)<<16)
        else:
            assert value==255;masks[frame]|=np.uint32(1<<24)
    return masks,cap


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--verify-existing-metadata',action='store_true');args=parser.parse_args()
    closure=json.loads((ROOT/'analysis/sms_points_3_4_closure.json').read_bytes());assert closure['passed']
    movie=json.loads((ROOT/'analysis/sms_extended_campaign_video_report.json').read_bytes())
    main_trace=movie['source_capture_report']['route']
    traces=set(closure['selected_receipts'])|{main_trace}
    if args.verify_existing_metadata:
        def field(data,key):
            token=('"'+key+'":').encode();start=data.index(token)+len(token)
            return json.JSONDecoder().raw_decode(data[start:start+65536].decode().lstrip())[0]
        baseline=(ROOT/'validation'/main_trace/'capture.json').read_bytes()
        options=field(baseline,'core_options');fps=field(baseline,'fps');checked=[]
        for trace in sorted(traces):
            data=(ROOT/'validation'/trace/'capture.json').read_bytes()
            assert field(data,'rom_sha256')==closure['source_sha256']
            assert field(data,'core_options')==options and abs(field(data,'fps')-fps)<1e-9
            assert field(data,'sram_input') is None
            digest=hashlib.sha256(data).hexdigest()
            if trace in closure['selected_receipts']:
                assert digest==closure['selected_receipts'][trace]['input_evidence']['capture.json']
            checked.append(dict(trace=trace,capture_sha256=digest))
        result=dict(passed=True,source_sha256=closure['source_sha256'],core_options=options,
            fps=fps,all_cold_sram_inputs_none=True,recordings=checked,
            purpose='Exact input/write-prefix comparison is admissible only for the same ROM, region, core options and initial SRAM contract.')
        (ROOT/'analysis/sms_video_prefix_metadata_report.json').write_text(json.dumps(result,indent=2)+'\n')
        plan_path=ROOT/'analysis/sms_selected_proof_video_plan.json';plan=json.loads(plan_path.read_bytes())
        plan['prefix_metadata_contract_verified']=True;plan['prefix_metadata_report']='analysis/sms_video_prefix_metadata_report.json'
        plan_path.write_text(json.dumps(plan,indent=2)+'\n')
        print(json.dumps(dict(passed=True,compatible_recordings=len(checked),fps=fps,core_options=options)),flush=True)
        return
    arrays={};caps={}
    for n,trace in enumerate(sorted(traces)):
        arrays[trace],caps[trace]=timeline(trace)
        if n%20==0:print('TIMELINES',n+1,len(traces),flush=True)
    assert all(c['rom_sha256']==closure['source_sha256'] and c['core_options']==caps[main_trace]['core_options']
        and abs(c['fps']-caps[main_trace]['fps'])<1e-9 for c in caps.values())
    remaining=set(closure['selected_receipts']);selected=[main_trace];covered={}
    def accepts(longer,shorter):
        return len(arrays[longer])>=len(arrays[shorter]) and np.array_equal(arrays[longer][:len(arrays[shorter])],arrays[shorter])
    for trace in list(remaining):
        if accepts(main_trace,trace):covered[trace]=main_trace;remaining.remove(trace)
    while remaining:
        candidates={t:[r for r in remaining if accepts(t,r)] for t in remaining}
        best=max(candidates,key=lambda t:(len(candidates[t]),len(arrays[t])))
        selected.append(best)
        for trace in candidates[best]:covered[trace]=best;remaining.remove(trace)
    clips=[];prior=[main_trace]
    for trace in selected[1:]:
        common=0
        for other in prior:
            size=min(len(arrays[trace]),len(arrays[other]));diff=np.flatnonzero(arrays[trace][:size]!=arrays[other][:size])
            same=int(diff[0])-1 if len(diff) else size-1
            common=max(common,same)
        first=max(1,common-120)
        clips.append(dict(trace=trace,from_frame=first,end_frame=caps[trace]['frames'],
            duration_seconds=(caps[trace]['frames']-first+1)/movie['fps'],common_boot_prefix_frames=common,
            currency_assisted_component_test=closure['selected_receipts'][trace]['currency_assisted_component_test'],
            covered_receipts=[t for t in sorted(covered) if covered[t]==trace],recorded=False))
        prior.append(trace)
    result=dict(source_sha256=closure['source_sha256'],main_trace=main_trace,main_movie=movie['movie'],
        selected_receipts=len(covered),covered_by_main=[t for t in sorted(covered) if covered[t]==main_trace],
        clips=clips,total_annex_seconds=sum(c['duration_seconds'] for c in clips),
        method='Exact inclusive fixed input masks AND all guard/money write events from boot. Clips overlap the longest already selected prefix by 120 frames. Every clip must still cold-replay to its independently proved final RAM/pixels.',
        clips_recorded=False,all_npcs_complete=False,all_side_quests_complete=False)
    (ROOT/'analysis/sms_selected_proof_video_plan.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(receipts=len(covered),main_covers=len(result['covered_by_main']),clips=len(clips),annex_seconds=result['total_annex_seconds'])),flush=True)


if __name__=='__main__':main()
