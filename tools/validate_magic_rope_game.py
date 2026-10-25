"""Exercise production rope hooks in the playable ROM; controlled outdoor fixtures."""
import contextlib, io, json
from run_core import ROOT,run
from validate_playable_sprite_limit import symbols
from validate_actor_tick import PRESSES
from archive_lossless_evidence import sha

def main():
    sy=symbols(ROOT/'megadrive/out/release/symbol.txt');rom=ROOT/'gaw-megadrive.bin';results=[]
    for region in ['ntsc','pal']:
      for direction,y in [(0,104),(1,32)]:
        out=ROOT/f'validation/magic-rope-game/{region}-{direction}';pending=[];expected=[None];ticks=[];rows=[];published=[];previous=[None];last=[None]
        def data(r,name,n):
            a=sy[name];return bytes(r[(a+i)^1] for i in range(n))
        def observe(frame,r):
            if frame==3100:
                assert int.from_bytes(data(r,'game_state',2),'big')==12
                cells=bytearray(data(r,'scratch',4096)[0x800:0x900]);x=120
                if not direction:
                    cells[0x57]=2;cells[0x47]=12;cells[0x37]=12
                    after=bytearray(cells);after[0x57]=0x6d;after[0x47]=after[0x37]=0x6c;w=bytes([3,6,88,112])
                else:
                    cells[0x27]=12;cells[0x37]=7;cells[0x47]=2
                    after=bytearray(cells);after[0x27]=after[0x37]=0x6c;after[0x47]=0x6d;w=bytes([4,6,32,112])
                meta=data(r,'scratch',2048);expected[:]=[(bytes(after),w,meta)]
                values=[('hero_x',(x<<8).to_bytes(2,'big')),('hero_y',(y<<8).to_bytes(2,'big')),('hero_counter',b'\0\0'),('hero_dx',b'\0\0'),('hero_dy',b'\0\0'),('hero_state',b'\0\1'),('hero_pending',direction.to_bytes(2,'big')),('hero_direction',direction.to_bytes(2,'big')),('magic_rope_work',bytes(4)),('world_actor_state',bytes(0x300))]
                pending.extend((3101,sy[k],v) for k,v in values)
                pending.extend([(3101,sy['scratch']+0x800,bytes(cells)),(3101,sy['hero_items']+13,b'\1')])
            if frame<3101:return
            after,w,meta=expected[0];work=data(r,'magic_rope_work',4);cells=data(r,'scratch',4096)[0x800:0x900]
            if cells!=after:
                assert not ticks,('rope cells reverted',region,direction,frame)
                return
            if not ticks:
                assert work[0]==w[0],('start',region,direction,frame,work.hex())
                expected_work=bytearray(w)
            else:expected_work=bytearray(previous[0])
            if expected_work[0]:
                start_y=expected_work[2];offset=start_y*8+28;cell=after[(start_y&240)|7]
                row=meta[cell*8+((start_y&8)>>1):cell*8+((start_y&8)>>1)+4]
                assert data(r,'sms_vram',0x4000)[0x3800+offset:0x3804+offset]==row,('row',region,direction,frame)
                expected_work[2]=(expected_work[2]+(-8 if expected_work[0]==3 else 8))&255
                expected_work[1]=(expected_work[1]-1)&255
                if not expected_work[1]:expected_work[0]=0
                rows.append(dict(frame=frame,offset=offset,bytes=row.hex()))
            assert work==expected_work,('work',region,direction,frame,work.hex(),expected_work.hex())
            previous[0]=work;ticks.append(frame);last[0]=data(r,'sms_vram',0x4000)
        def video(frame,vram):
            # GPG serializes native VRAM in word-swapped byte order.
            if frame<3102:return
            raw=bytes(vram[i^1] for i in range(65536))
            # Plane A base E000, 64 cells per row; gameplay starts at row2.
            for record in rows:
                if record['frame']!=frame-1:continue
                offset=record['offset'];r=offset//64;col=(offset&63)//2
                source=bytes.fromhex(record['bytes']);words=[]
                for n in range(2):
                    word=int.from_bytes(source[n*2:n*2+2],'little')
                    words.append(((word&0x1ff)+16)|((word&0x1e00)<<2))
                address=0xe000+((r+2)*64+col)*2
                actual=[int.from_bytes(raw[address+n*2:address+n*2+2],'big') for n in range(2)]
                assert actual==words,('VDP publication',region,direction,frame,actual,words)
                published.append(frame)
        with contextlib.redirect_stdout(io.StringIO()):
            run(rom,3130,out,set(range(3100,3113)),PRESSES+[(3101,3101,4 if not direction else 5)],ram_writes=pending,skip_intro=True,ram_observer=observe,vram_observer=video,core_options={'genesis_plus_gx_region_detect':region})
        assert len(published)==6 and len(rows)==6 and ticks and previous[0][0]==0,(region,direction,rows,ticks)
        results.append(dict(region=region,direction=direction,rows=rows,animation_completed=True,cells_exact=True,work_exact=True,next_vblank_rows_exact=len(published)))
    report=dict(passed=True,rom_sha256=sha(rom.read_bytes()),results=results,controlled_ram_fixture=True,natural_campaign_proof=False,limits=['Real production movement and animation hooks with controlled outdoor cells, inventory and hero position.','Hardware output and natural campaign rope use remain to validate.'])
    (ROOT/'analysis/magic_rope_game_report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
