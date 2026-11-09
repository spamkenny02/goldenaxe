"""Build a separate read-only timing GX DLL using the installed Windows GCC.
Use native subprocess argv; MSYS bash cannot create its signal pipe here.
"""
import argparse,os,shlex,subprocess
from pathlib import Path
from actor_reference import ROOT

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--target',default='genesis_plus_gx_timing_libretro.dll');parser.add_argument('--log',type=Path,default=ROOT/'validation/timing-core-build-python.log');parser.add_argument('--force-source',action='append',default=[]);args=parser.parse_args()
 workspace=ROOT.parents[1];cwd=workspace/'work/genesis-plus-gx'
 gcc=next((p for p in [Path('C:/msys64/ucrt64/bin/gcc.exe'),Path('D:/mingw64/bin/gcc.exe')] if p.is_file()),None);assert gcc,'Windows GCC not found'
 gcc=gcc.as_posix();compiler_bin=Path(gcc).parent.as_posix()
 env=dict(os.environ);env['PATH']=compiler_bin+';'+env['PATH']
 command=[str(workspace/'work/sgdk/bin/make.exe'),'-n','-f','Makefile.libretro','platform=win',f'TARGET={args.target}',f'CC={gcc}',f'CXX={compiler_bin}/g++.exe','GIT_VERSION=','SHELL=C:/Windows/System32/cmd.exe']
 for source in args.force_source:
  candidate=(cwd/source).resolve();assert candidate.is_relative_to(cwd.resolve()) and candidate.is_file()
  command+=['-W',source]
 plan=subprocess.run(command,cwd=cwd,capture_output=True,text=True);assert plan.returncode==0,plan.stderr
 logs=[]
 for line in plan.stdout.splitlines():
  if not line.startswith(gcc):continue
  result=subprocess.run(shlex.split(line),cwd=cwd,capture_output=True,text=True,env=env)
  logs.append(line+'\n'+result.stdout+result.stderr);assert result.returncode==0,logs[-1]
 args.log.write_text('\n'.join(logs))
 print(cwd/args.target)
if __name__=='__main__':main()
