"""Check copied decoded frames at every montage segment's two boundaries."""
import hashlib,json
from pathlib import Path
import cv2,numpy as np
from run_core import ROOT


def main():
    report=json.loads((ROOT/'analysis/sms_proof_montage_report.json').read_bytes());assert report['passed']
    work=ROOT/'validation/sms-proof-montage-2026-11-12';segments=[]
    for line in (work/'segments.ffconcat').read_text(encoding='utf-8').splitlines():
        if line.startswith("file '"):segments.append(dict(path=Path(line[6:-1])))
        elif line.startswith('duration '):segments[-1]['frames']=round(float(line.split()[1])*report['fps'])
    movie=cv2.VideoCapture(report['movie']);assert movie.isOpened();cursor=0;checks=[]
    for n,segment in enumerate(segments):
        source=segment['path'].resolve();assert source.is_relative_to(ROOT)
        cap=cv2.VideoCapture(str(source));assert cap.isOpened()
        assert int(cap.get(cv2.CAP_PROP_FRAME_COUNT))==segment['frames']
        for local in (0,segment['frames']-1):
            cap.set(cv2.CAP_PROP_POS_FRAMES,local);ok,expected=cap.read();assert ok
            movie.set(cv2.CAP_PROP_POS_FRAMES,cursor+local);ok,actual=movie.read();assert ok
            if not np.array_equal(expected,actual):
                cv2.imwrite(str(work/f'boundary-{n:03d}-{local}-expected.png'),expected)
                cv2.imwrite(str(work/f'boundary-{n:03d}-{local}-actual.png'),actual)
                raise AssertionError(('Montage boundary mismatch',n,cursor+local,str(source)))
            checks.append(dict(segment=n,source=str(source),source_frame=local,montage_frame=cursor+local,
                decoded_bgr_sha256=hashlib.sha256(actual.tobytes()).hexdigest()))
        cap.release();cursor+=segment['frames']
        if n%25==0:print('EXACT BOUNDARIES',n+1,len(segments),flush=True)
    movie.release();assert cursor==report['frames']
    result=dict(passed=True,segments=len(segments),exact_decoded_boundary_frames=len(checks),
        movie_sha256=report['movie_sha256'],frames=cursor,checks=checks,
        scope='First and last decoded frame of every gameplay segment and branch title card; identical to the corresponding source MP4 frame.')
    (ROOT/'analysis/sms_montage_boundary_pixels_report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,segments=len(segments),exact_boundary_frames=len(checks))))


if __name__=='__main__':main()
