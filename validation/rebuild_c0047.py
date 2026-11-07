"""Reconstruct published c0047 from tracked sources and its patch, with explicitFF packaging."""
import argparse,hashlib,io,json,subprocess,sys,tarfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--work',type=Path,default=root/'validation/c0047-clean-rebuild02');a=p.parse_args()
work=a.work.resolve();assert work.is_relative_to(root/'validation') and not work.exists(),'Choose a fresh work directory under validation'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
base_commit='03f21f34069cec80827e257f820f1245f72ce6b8'
raw_tree=subprocess.check_output(['git','archive','--format=tar',base_commit,'megadrive/src'],cwd=root)
inputs={}
with tarfile.open(fileobj=io.BytesIO(raw_tree),mode='r:') as tree:
    for member in tree:
        if member.isdir():continue
        assert member.isfile(),'Source archive must contain regular files only'
        target=work/'src'/Path(member.name).relative_to('megadrive/src')
        assert target.resolve().is_relative_to(work/'src')
        raw=tree.extractfile(member).read();target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
        inputs[member.name]=hashlib.sha256(raw).hexdigest()
files=list(inputs);assert len(files)>200
patch=root/'versions/candidates/c0047-d3ea2a83/source.patch';packpath=patch.with_name('packaging.json');pack=json.loads(packpath.read_bytes())
assert pack['candidate']=='c0047' and pack['padding_byte']==255 and pack['bytes']==2097152
args=['git','apply','-p3','--directory='+(work/'src').relative_to(root).as_posix(),str(patch)]
subprocess.run(args[:2]+['--check']+args[2:],cwd=root,check=True);subprocess.run(args,cwd=root,check=True)
helper=root/'tools/build_private_candidate.ps1'
recipe=dict(base_commit=base_commit,tracked_base_sources=inputs,
            published_patch=patch.relative_to(root).as_posix(),patch_sha256=sha(patch),patched_main_sha256=sha(work/'src/main.c'),
            packaging_manifest_sha256=sha(packpath),padding_byte=255,build_helper_sha256=sha(helper),production_rom_sha256=sha(root/'gaw-megadrive.bin'))
(work/'inputs.json').write_text(json.dumps(recipe,indent=2)+'\n',encoding='utf-8')
print('Clean tracked source tree copied and published patch applied:',len(files),'files; explicitFF padding',flush=True)
subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(helper),'-Project',str(work),'-PaddingByte','255'],cwd=root,check=True)
actualpack=json.loads((work/'packaging-build.json').read_bytes())
assert actualpack==dict(compiledBytes=pack['previous_bytes'],finalBytes=pack['bytes'],paddingByte=pack['padding_byte'])
published=patch.with_name('gaw-megadrive-c0047.bin');built=work/'out/release/rom.bin'
assert built.read_bytes()==published.read_bytes(),'Clean build differs; retain outputs for diagnosis'
result=dict(passed=True,candidate='c0047',md_sha256=sha(built),rom_bytes=built.stat().st_size,clean_rebuild_identical=True,
            symbols_identical=sha(work/'out/release/symbol.txt')==sha(published.with_name('symbol.txt')),
            base_commit=recipe['base_commit'],tracked_source_files=len(files),published_patch_sha256=sha(patch),build_helper_sha256=sha(helper),padding=actualpack,
            archive_manifest='analysis/c0047-clean-rebuild/manifest.json',scope='Fresh SGDK compilation from tracked base sources plus published c0047 patch, original SGDK-aligned program span retained, external padding explicitlyFF and checksum finalized. Reproducibility only, not a new gameplay or SMS fidelity claim.')
(work/'report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
out=root/'analysis/c0047-clean-rebuild'
if not out.exists():
    sys.path.insert(0,str(root/'tools'));from archive_lossless_evidence import freeze
    paths=[Path(__file__).resolve(),patch,packpath,helper,root/'tools/finalize_md_rom.py']+[p for p in work.rglob('*') if p.is_file()]
    freeze(root,out,paths,result,[work],cleanup=True)
    (root/'analysis/c0047_clean_rebuild_report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
else:print('Existing reference archive preserved; fresh reconstruction retained in',work,flush=True)
print('Clean c0047 build is byte-identical to the published ROM',flush=True)
