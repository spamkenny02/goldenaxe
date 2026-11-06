"""Correct c0046 cartridge padding without changing its native program."""
import json
from pathlib import Path
import shutil
import sys
sys.path.insert(0,'tools')
from finalize_md_rom import md_checksum
from archive_lossless_evidence import sha

ROOT=Path(__file__).resolve().parents[1]
previous=ROOT/'versions/candidates/c0046-9e747d38'
original=(previous/'gaw-megadrive-c0046.bin').read_bytes()
assert len(original)==1179648 and int.from_bytes(original[0x1a4:0x1a8],'big')==2097151
raw=bytearray(original)+bytearray([255])*(2097152-len(original))
raw[0x18e:0x190]=md_checksum(raw).to_bytes(2,'big')
assert raw[:0x18e]==original[:0x18e] and raw[0x190:len(original)]==original[0x190:]
assert all(b==255 for b in raw[len(original):])
assert int.from_bytes(raw[0x1a4:0x1a8],'big')==len(raw)-1
digest=sha(raw);dest=ROOT/f'versions/candidates/c0047-{digest[:8]}'
assert not dest.exists();dest.mkdir(parents=True)
(dest/'gaw-megadrive-c0047.bin').write_bytes(raw)
for name in ['symbol.txt','source.patch']:shutil.copyfile(previous/name,dest/name)
metadata=dict(candidate='c0047',rom_sha256=digest,bytes=len(raw),
    checksum=f'{md_checksum(raw):04X}',previous_candidate='c0046',
    previous_sha256=sha(original),previous_bytes=len(original),
    same_program_and_assets_except_header_checksum=True,padding_byte=255,
    header_rom_end=len(raw)-1,full_candidate_campaign_verified=False)
(dest/'packaging.json').write_text(json.dumps(metadata,indent=2)+'\n')
(dest/'README.md').write_text(f'''# c0047 — ROM de 2 Mio correctement complétée

Cet aperçu contient le programme et les ressources de c0046. Seuls le
complément final à FF et le checksum changent. L’optimisation des motifs
du héros reste identique.

c0046 annonçait 2 Mio dans son en-tête mais son fichier ne faisait que
1152 Kio. c0047 complète le fichier à 2048 Kio et recalcule le checksum.
Les captures et parcours c0046 restent attachés au binaire c0046 ; les
rejeux sur cette image complétée sont indiqués séparément.

SHA-256 : `{digest}`. Checksum : {md_checksum(raw):04X}.

- [ROM c0047](gaw-megadrive-c0047.bin)
- [Programme source, patch par rapport à V318](source.patch)
- [Vérification du contenu et de l’en-tête](packaging.json)
- [Mesures de l’optimisation c0046](../c0046-9e747d38/README.md)

La V318 reste la référence. Le parcours complet de cet aperçu reste à valider.
''')
for name in ['c0045-415ba9e1','c0046-9e747d38']:
    path=ROOT/'versions/candidates'/name/'README.md'
    text=path.read_text().replace('Aperçu de développement de 2 Mio','Aperçu de développement de 1152 Kio')
    text+='\nCorrection de format : ce fichier annonce 2 Mio dans son en-tête mais ne\ncontient que 1152 Kio. Il est conservé pour reproduire ses essais.\nVoir c0047 pour le programme de c0046 complété à 2 Mio.\n'
    path.write_text(text)
print(json.dumps(metadata,indent=2),flush=True)
print(dest.relative_to(ROOT).as_posix(),flush=True)
