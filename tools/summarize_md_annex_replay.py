"""Account for retained SMS cases and their actually played/filmed MD counterparts."""
import hashlib,json
from pathlib import Path
from validate_playable_sprite_limit import symbols
from write_atomic_report import write_bytes
ROOT=Path(__file__).resolve().parents[1]
SHA='1421abe47de95ac104a03e2fb1be7001f70aeca1fbb6a9b35669aa6e98b7d9a4'
def load(p):return json.loads(p.read_bytes())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    cases={}
    def add(trace,origin):
        trace=trace.removeprefix('validation/')
        if not trace.startswith(('natural-service-route/sms-','natural-dungeon-combat/sms-','natural-dungeon-route/sms-')):return
        row=cases.setdefault(trace,dict(sms_trace=trace,source_registers=[],md_passed=False,fixed_replay_passed=False,video_verified=False,md_evidence=[]))
        if origin not in row['source_registers']:row['source_registers'].append(origin)
    def walk(x,origin):
        if isinstance(x,dict):
            for k,v in x.items():
                if k=='trace' and isinstance(v,str):add(v,origin)
                if k=='stage' and isinstance(v,str) and v.startswith('sms-'):add('natural-service-route/'+v,origin)
                walk(v,origin)
        elif isinstance(x,list):
            for v in x:walk(v,origin)
    names=['sms_points_3_4_closure.json','sms_plain_house_census_campaign.json','sms_npc_coverage_report.json','sms_npc_campaign_progress_report.json','sms_six_points_progress.json',
           'sms_teacher_returns_campaign.json','sms_remaining_magic_campaign.json','sms_magic_refill_campaign.json','sms_gold_house_census_campaign.json','sms_gold_funding_campaign.json','sms_fairy_census_campaign.json','sms_equipment_returns_campaign.json','sms_guide_text_investigation.json']
    sources={}
    for name in names:
        path=ROOT/'analysis'/name
        if not path.exists():continue
        value=load(path);sources[name]=sha(path);walk(value,name)
        if name=='sms_points_3_4_closure.json':
            for trace in value['selected_receipts']:add(trace,name)
    # Only exact referenced SMS cases may receive credit. A main MD ending is
    # not a substitute for an unplayed NPC/reward/condition branch.
    filmed={}
    for path in (ROOT/'videos/md-annexes-2026-11-12').glob('*/report.json'):
        r=load(path)
        if not r.get('passed') or r['rom_sha256']!=SHA:continue
        assert r['full_audio_video_decoded'] and r['final_ram_and_pixels_exact'] and not r['boss_assistance']
        assert sha(ROOT/r['movie'])==r['movie_sha256'];filmed[r['trace']]=(path,r)
    partial_exits=[];sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
    for trace,(video_path,video) in filmed.items():
        folder=ROOT/'validation'/trace;r=load(folder/'report.json');cap=load(folder/'capture.json')
        reference=r.get('sms_reference')
        if reference not in cases:continue
        assert r['passed'] and r['rom_sha256']==SHA and not r.get('sram_checkpoint_injection',False)
        raw=(folder/f'ram_{cap["frames"]:05d}.bin').read_bytes();word=lambda n:raw[sy[n]]|(raw[sy[n]+1]<<8)
        if word('resume_phase') or word('world_graphics_class') or raw[sy['door_transition_loading']^1] or (r.get('variant')=='refusal' and not (r.get('actual_exterior_movement_verified') or r.get('actual_exterior_movement_frame') or r.get('actual_exterior_menu_roundtrip_verified'))):
            partial_exits.append(dict(trace=trace,reason='Endpoint still in house exit/reveal; dialogue evidence retained but not a completed exit',resume_phase=word('resume_phase'),graphics_class=word('world_graphics_class')));continue
        if 'visited' in r:assert all(v['bitmap_exact_bytes']==1040 for v in r['visited'])
        elif r.get('variant')=='refusal':
            assert r['resources_unchanged'] and r['complete_frame'] is not None
            if r['kind']!='merchant':assert r['confirm_no_frame'] and r['sms_decline_bitmap_exact_frame']
            else:assert r['cancel_frame']
        elif r.get('variant')=='post_reward_silent_return':
            assert r['resources_and_flags_unchanged'] and r['complete_frame'] is not None and not r['text_entries']
        elif r.get('variant')=='quest_hint_contact':
            assert r['resources_and_flags_unchanged'] and r['complete_frame'] is not None
            assert all(v['bitmap_exact_bytes']==1040 for v in r['completed'] if 'text_pc' in v)
        elif 'choices' in r and 'completed' in r and r.get('sms_reference'):
            assert len(r['completed'])==len(r['choices']) and r['complete_frame'] is not None
            assert not r.get('currency_assisted_component_test') and not r['new_assistance_writes']
            assert all(v['bitmap_exact_bytes']==1040 and v['expect']==choice['expect'] and v['selection']==choice['selection'] for v,choice in zip(r['completed'],r['choices']))
        elif r.get('variant')=='gold_house_and_return':
            assert r['return_contact_end']-r['return_contact_start']>=80 and r['complete_frame'] is not None
            assert r['last_state']['gold']==r['expected_final_gold'] and r['last_state']['outside_flags']&2
            if not r['previously_collected']:assert r['first_exterior_exit_frame'] and r['reentered_frame'] and r['first_text_pc']
        else:continue
        end=cap['frames'];proof=folder.with_name(folder.name+(f'-assisted-fixed-replay-{end}' if cap['test_ram_writes'] else '-fixed-replay'))/'replay_report.json';w=load(proof)
        assert w['passed'] and w['final_png_exact'] and w['rom_sha256']==SHA and sha(proof)==video['proof_sha256']
        region='pal' if cap['core_options'].get('genesis_plus_gx_region_detect')=='pal' else 'ntsc'
        row=cases[reference];row['md_evidence'].append(dict(trace=trace,region=region,report=video_path.relative_to(ROOT).as_posix(),report_sha256=sha(video_path),conversations=len(r.get('visited',[])),scope=r['scope']))
        if region=='ntsc':row.update(md_passed=True,fixed_replay_passed=True,video_verified=True)
    rows=[cases[k] for k in sorted(cases)];done=sum(r['md_passed'] and r['fixed_replay_passed'] and r['video_verified'] for r in rows)
    report=dict(date='2026-11-12',md_sha256=SHA,md_version=322,rom_status='development_not_qualified_as_release_candidate',
        all_selected_sms_cases_verified_on_md=bool(rows) and done==len(rows),retained_sms_recording_cases=len(rows),md_ntsc_played_replayed_and_filmed_cases=done,
        all_npcs_complete=False,all_items_or_monsters_globally_certified=False,point6_status='open_until_md_counterparts_and_video_complete',
        scope='Inventory of selected SMS recordings, not a count of NPCs or a global completion percentage. Each trace can contain multiple interactions. Coverage is credited only to its exact SMS reference, actual MD result, fixed replay and decoded video. PAL counterpart evidence is recorded separately.',
        sources=sources,cases=rows)
    report['partial_exits_not_credited']=partial_exits
    report['partial_exit_recordings_not_credited']=len(partial_exits)
    write_bytes(ROOT/'analysis/md_annex_replay_coverage.json',(json.dumps(report,indent=2,ensure_ascii=False)+'\n').encode())
    movie_rows=[]
    for path in sorted((ROOT/'videos/md-annexes-2026-11-12').glob('*/report.json')):
        r=load(path)
        if r.get('passed'):
            movie_rows.append(f'| [{path.parent.name}]({path.parent.name}/{Path(r["movie"]).name}) | {r["duration_seconds"]:.2f} s | [Rapport]({path.parent.name}/report.json) |')
    text='# Annexes MD — relecture en cours\n\nChaque MP4 est une branche réellement rejouée, avec son du jeu. Les chargements Continuer utilisent seulement une SRAM écrite par le jeu et restent séparés des campagnes depuis Nouvelle partie. Aucune couverture globale tous PNJ/tous objets/toutes quêtes n’est déduite de cette liste.\n\n| Extrait | Durée | Preuve |\n| --- | --- | --- |\n'+'\n'.join(movie_rows)+'\n\nLes MP4 restent locaux. Les rapports réussis vérifient le décodage audio/vidéo intégral, la synchronisation, la RAM et les pixels finaux identiques au rejeu. [Suivi des cas](../../analysis/md_annex_replay_coverage.json).\n'
    write_bytes(ROOT/'videos/md-annexes-2026-11-12/README.md',text.encode())
    print(json.dumps({k:v for k,v in report.items() if k not in ('sources','cases','partial_exits_not_credited')},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
