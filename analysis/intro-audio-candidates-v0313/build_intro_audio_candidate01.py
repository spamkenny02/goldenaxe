import json,os,shutil,subprocess,sys
from pathlib import Path
sys.path.insert(0,'tools')
from run_core import ROOT
from archive_lossless_evidence import sha

project=ROOT/'validation/intro-audio-v0313/candidate01'
project.mkdir(parents=True,exist_ok=False)
build=project/'megadrive';build.mkdir()
shutil.copytree(ROOT/'megadrive/src',build/'src')
source=build/'src/intro.inc';before=source.read_bytes()
old=b'    sound_music(0x85);\r\n'
assert before.count(old)==1
updated=before.replace(old,b'')
anchor=b'    intro_scene=intro_abort=intro_timer=intro_counter=intro_line=0;intro_running=1;\r\n'
assert updated.count(anchor)==1
updated=updated.replace(anchor,anchor+b'    sound_music(0x85); /* Source dispatch precedes the initial font upload. */\r\n')
source.write_bytes(updated)
(project/'input').mkdir();shutil.copyfile(ROOT/'input/original.sms',project/'input/original.sms')
sdk=ROOT.parents[1]/'work/sgdk';sdkpath=sdk.as_posix();sdkunix='/'+sdkpath[0].lower()+sdkpath[2:]
env=dict(os.environ);env['PATH']=str(sdk/'bin')+';'+env['PATH']
command=[str(sdk/'bin/sh.exe'),'-c','export PATH="$2/bin:$PATH"; make -f "$1/makefile.gen" "GDK=$1" "JAVA=$3" -j2','build',sdkpath,sdkunix,'D:/jdk-25.0.1/bin/java.exe']
result=subprocess.run(command,cwd=build,env=env,capture_output=True)
(project/'build.log').write_bytes(result.stdout+result.stderr)
assert result.returncode==0,(result.stdout+result.stderr)[-5000:]
rom=build/'out/release/rom.bin'
subprocess.run(['D:/jdk-25.0.1/bin/java.exe','-jar',str(sdk/'bin/sizebnd.jar'),str(rom),'-sizealign','2097152'],check=True)
subprocess.run([sys.executable,str(ROOT/'tools/finalize_md_rom.py'),str(rom)],check=True)
shutil.copyfile(rom,project/'gaw-megadrive.bin')
record=dict(candidate_rom_sha256=sha(rom.read_bytes()),production_rom_sha256=sha((ROOT/'gaw-megadrive.bin').read_bytes()),
            production_source_unchanged=sha((ROOT/'megadrive/src/intro.inc').read_bytes())==sha(before),
            source_before_sha256=sha(before),source_after_sha256=sha(source.read_bytes()),
            scope='Private intro-music dispatch prototype only; no public ROM replacement or version assignment.')
(project/'build_report.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record),flush=True)
