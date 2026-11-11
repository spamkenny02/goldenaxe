"""Record the selected genuine gambling branches as visibly separate clips."""
import json,subprocess,sys
from run_core import ROOT


def main():
    specs=[('5c','play',440645),('13','play',479202),('a7','play',479202),
           ('de','play',479202),('5c','refuse',440645)]
    for outside,variant,first in specs:
        data=json.loads((ROOT/f'analysis/sms_minigame_{outside}_{variant}_campaign.json').read_bytes())
        assert data['passed'];name=f'jeu-{outside}-{variant}';source=f'sms-video-{name}-2026-11-11'
        if not (ROOT/'validation'/source/'report.json').exists():
            with (ROOT/'validation'/(source+'.log')).open('w',encoding='utf-8') as log:
                subprocess.run([sys.executable,str(ROOT/'tools/record_sms_gameplay.py'),
                    '--trace',data['last_verified_prefix'],'--from-frame',str(first),'--out',source],
                    cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        with (ROOT/'validation'/('archive-'+source+'.log')).open('w',encoding='utf-8') as log:
            subprocess.run([sys.executable,str(ROOT/'tools/archive_sms_video_annex.py'),
                '--source',source,'--name',name,'--description',f'Branche de jeu SMS {outside.upper()} : {variant}. Tirages du jeu original, sans modification du hasard ni de l argent.'],
                cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        print('GAMBLING VIDEO VERIFIED',name,flush=True)


if __name__=='__main__':main()
