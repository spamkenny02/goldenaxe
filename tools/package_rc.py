"""Stage a standalone RC source tree, then package it after a clean build check."""
import argparse,hashlib,json,shutil,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
STAGE=ROOT/'validation/rc1-portable/gaw-v0322-rc1'
SHA='1421abe47de95ac104a03e2fb1be7001f70aeca1fbb6a9b35669aa6e98b7d9a4'
def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def copy_sources():
    for folder in ('src','research','z80','overlays'):
        shutil.copytree(ROOT/'megadrive'/folder,STAGE/'megadrive'/folder,dirs_exist_ok=True)
    for name in ('build_rc_rom.py','build_private_candidate.ps1','build_credits_border_overlay.py','build_title_publication_overlay.py','build_dialogue_empty_width_candidate.py','finalize_md_rom.py'):
        (STAGE/'tools').mkdir(exist_ok=True);shutil.copyfile(ROOT/'tools'/name,STAGE/'tools'/name)
    shutil.copyfile(ROOT/'BUILD_RC.ps1',STAGE/'BUILD_RC.ps1')
def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',action='store_true');p.add_argument('--archive',action='store_true');a=p.parse_args()
    assert a.stage != a.archive
    if a.stage:
        assert not STAGE.exists();STAGE.mkdir(parents=True);copy_sources()
        with zipfile.ZipFile(ROOT/'handoff/gaw-v320-ready-to-build-windows.zip') as old:
            for item in old.infolist():
                name=item.filename.removeprefix('gaw-v320/')
                if not(name.startswith('toolchain/') or name=='LICENCES.txt'):continue
                target=STAGE/name;assert target.resolve().is_relative_to(STAGE)
                if item.is_dir():target.mkdir(parents=True,exist_ok=True);continue
                target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(old.read(item))
        print('Staged standalone tree:',STAGE,flush=True);return
    built=STAGE/'dist/gaw-megadrive-v0322-rc1.bin';assert sha(built)==SHA
    report=json.loads((STAGE/'dist/source-build-report.json').read_bytes());assert report['passed'] and report['md_sha256']==SHA
    # Do not update sources after the verified build.
    for name,digest in report['source_manifest'].items():assert sha(ROOT/name)==sha(STAGE/name)==digest,name
    shutil.copytree(ROOT/'reports/gaw-v0322-rc1-2026-11-12',STAGE/'release-notes',dirs_exist_ok=True)
    (STAGE/'LIRE_AVANT_COMPILATION.md').write_text('''# Golden Axe Warrior V322 RC1 — compilation Windows

Prérequis : Windows x64, PowerShell, Python 3.10+ disponible comme `python` (bibliothèque standard seulement). SGDK et Java sont inclus avec leurs licences. Extraire dans un chemin sans espaces.

Exécuter `powershell -ExecutionPolicy Bypass -File BUILD_RC.ps1`.
Résultat : `dist/gaw-megadrive-v0322-rc1.bin`, 2 Mio, SHA-256 `'''+SHA+'''`.
Le script compile les sources natives puis applique trois corrections 68000 auditées (générique, titre, dialogue Saylun). Chaque base et instruction remplacée est vérifiée. Aucun ancien binaire ni accès Git n'est nécessaire à la compilation. Le dossier `dist` fourni permet une comparaison ; il n'est pas utilisé comme entrée.

Les rapports de publication et les limites sont dans `release-notes`. Ce paquet compact de compilation ne contient pas les vidéos, l'historique Git ou l'ensemble des traces de recherche.
''',encoding='utf-8')
    (STAGE/'README.md').write_text('# Golden Axe Warrior V322 RC1\n\nPaquet autonome de compilation Windows. Lire [les instructions](LIRE_AVANT_COMPILATION.md), puis [les contrôles et limites de la RC](release-notes/RAPPORT.md).\n\nSources natives 68000/SGDK et trois corrections assembleur ; ROM de référence compilée dans `dist`. SGDK/Java inclus avec licences. Python 3.10+ et PowerShell requis. Le paquet est compact : vidéos, historique Git et recherches complètes restent dans le projet principal.\n',encoding='utf-8')
    target=ROOT/'handoff/gaw-v0322-rc1-ready-to-build-windows.zip';assert not target.exists()
    files=[p for p in STAGE.rglob('*') if p.is_file() and 'validation' not in p.relative_to(STAGE).parts and '__pycache__' not in p.parts]
    hashes={p.relative_to(STAGE).as_posix():sha(p) for p in files}
    with zipfile.ZipFile(target,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for path in files:z.write(path,'gaw-v0322-rc1/'+path.relative_to(STAGE).as_posix())
        z.writestr('gaw-v0322-rc1/CONTENTS_SHA256.json',json.dumps(hashes,indent=2)+'\n')
    with zipfile.ZipFile(target) as z:
        for name,digest in hashes.items():assert hashlib.sha256(z.read('gaw-v0322-rc1/'+name)).hexdigest()==digest,name
    result=dict(passed=True,md_sha256=SHA,archive=target.relative_to(ROOT).as_posix(),bytes=target.stat().st_size,sha256=sha(target),members_sha256_verified=len(hashes),standalone_source_build=True)
    (ROOT/'handoff/v0322-rc1-package-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    target.with_suffix('.zip.sha256').write_text(result['sha256']+'  '+target.name+'\n');print(json.dumps(result),flush=True)
    binary=ROOT/'handoff/gaw-v0322-rc1-ROM.zip';assert not binary.exists()
    with zipfile.ZipFile(binary,'x',zipfile.ZIP_DEFLATED) as z:
        z.write(built,'gaw-megadrive-v0322-rc1.bin')
        z.write(ROOT/'reports/gaw-v0322-rc1-2026-11-12/RAPPORT.md','RAPPORT.md')
        z.write(ROOT/'analysis/rc1_release_report.json','RELEASE.json')
        z.writestr('SHA256SUMS.txt',SHA+'  gaw-megadrive-v0322-rc1.bin\n')
    with zipfile.ZipFile(binary) as z:assert hashlib.sha256(z.read('gaw-megadrive-v0322-rc1.bin')).hexdigest()==SHA
    binary.with_suffix('.zip.sha256').write_text(sha(binary)+'  '+binary.name+'\n')
if __name__=='__main__':main()
