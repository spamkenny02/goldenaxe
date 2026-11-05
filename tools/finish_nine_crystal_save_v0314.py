"""Resume only the missing save phase after the completed v314 palace pipeline."""
import json
import shutil
import subprocess
import sys

from archive_lossless_evidence import sha
from continue_d8_entry_v0314 import assert_canonical
from run_core import ROOT


def main():
    digest='c53381c459a1e6254a8c9f1cfad1b8cda482cc0614697ad566133b28335e07a7'
    assert sha((ROOT/'gaw-megadrive.bin').read_bytes())==digest
    assert_canonical('natural-dungeon-route','md-v0314-real-save-route02')
    final=json.loads((ROOT/'analysis/cold_palace_final_v0314_report.json').read_bytes())
    assert final['passed'] and final['ending_complete'] and final['md_sha256']==digest
    snapshot=ROOT/'validation/v0314-after-d9-sources/save-resume'
    snapshot.mkdir(exist_ok=False)
    names=['natural_save_service.py','validate_game_written_save.py',
           'finish_nine_crystal_save_v0314.py']
    index={}
    for name in names:
        shutil.copyfile(ROOT/'tools'/name,snapshot/name)
        index[name]=sha((snapshot/name).read_bytes())
    (snapshot/'source_index.json').write_text(json.dumps(index,indent=2)+'\n')
    commands=[['natural_save_service.py','--prefix','md-v0314-real-save-route02',
               '--assisted-prefix','--trial','v0314-nine-crystals-save01'],
              ['validate_game_written_save.py','--trace',
               'natural-service-route/md-v0314-nine-crystals-save01',
               '--trial','v0314-nine-crystals-01','--release-report-name',
               'game_written_save_v0314_nine_crystals_report.json']]
    (snapshot/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
    for command in commands:
        print('SAVE RESUME',*command,flush=True)
        subprocess.run([sys.executable,'-u',str(ROOT/'tools'/command[0]),*command[1:]],cwd=ROOT,check=True)
    print('Nine-crystal real save and Continue verified',flush=True)


if __name__=='__main__':
    main()
