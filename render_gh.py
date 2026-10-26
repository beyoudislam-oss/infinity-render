#!/usr/bin/env python3
"""Flash-safe frame-accurate renderer for any HTML video page (any size / fps).
usage: render.py <page.html> <duration_s> [out_prefix=part] [fps=30] [WxH=1080x1920]
Page must expose window.render(t). Renders 150-frame chunks (resumable: finished
chunks are skipped, so re-run after any sandbox timeout). Each frame: render(t),
2 rAF + 25 ms wait, JPEG capture. Brightness jump >10 vs previous frame triggers
up to 3 re-captures (re-render t-1 then t, 3 rAF) and keeps the smoothest one."""
import subprocess,time,pathlib,sys,os,io
import numpy as np
from PIL import Image
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)));from spike import spikes
from playwright.sync_api import sync_playwright
html=sys.argv[1];DUR=float(sys.argv[2]);PRE=sys.argv[3] if len(sys.argv)>3 else 'part';FPS=int(sys.argv[4]) if len(sys.argv)>4 else 30
W,H=[int(v) for v in (sys.argv[5] if len(sys.argv)>5 else '1080x1920').split('x')]
import shutil
CHROME=os.environ.get('CHROME') or shutil.which('google-chrome') or shutil.which('chromium') or shutil.which('chromium-browser')
N=int(FPS*DUR);CH=150
ONLY=[int(x) for x in os.environ.get('CHUNKS','').split(',') if x.strip()]
def mb(j):return np.asarray(Image.open(io.BytesIO(j)).convert('L').resize((54,max(1,int(54*H/W)))),float).mean()
u=pathlib.Path(html).resolve().as_uri()
RAF2="new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))"
RAF3="new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(()=>requestAnimationFrame(r))))"
with sync_playwright() as p:
    b=p.chromium.launch(**({'executable_path':CHROME} if CHROME else {}),args=['--no-sandbox','--disable-gpu','--allow-file-access-from-files'])
    pg=b.new_page(viewport={'width':W,'height':H},device_scale_factor=1)
    pg.goto(u);pg.evaluate('document.fonts.ready');pg.wait_for_timeout(1500);t0=time.time()
    for c in range(0,N,CH):
        if ONLY and c//CH not in ONLY: continue
        out=f'{PRE}_{c//CH:02d}.mp4'
        if os.path.exists(out):continue
        tmp=out+'.tmp.mp4'
        ff=subprocess.Popen(['ffmpeg','-y','-v','error','-f','image2pipe','-framerate',str(FPS),'-vcodec','mjpeg','-i','-','-c:v','libx264','-preset','ultrafast','-crf','15','-pix_fmt','yuv420p',tmp],stdin=subprocess.PIPE)
        prev=None
        # warm-up: play the 15 frames before the chunk so animations/state are settled
        for k in range(max(0,c-15),c):pg.evaluate(f'render({k/FPS})')
        for i in range(c,min(N,c+CH)):
            pg.evaluate(f'render({i/FPS})');pg.evaluate(RAF2);pg.wait_for_timeout(25);j=pg.screenshot(type='jpeg',quality=94);m=mb(j)
            if prev is not None and abs(m-prev)>10:
                best=(abs(m-prev),j,m)
                for _ in range(3):
                    pg.evaluate(f'render({(i-1)/FPS})');pg.evaluate(f'render({i/FPS})');pg.evaluate(RAF3);j2=pg.screenshot(type='jpeg',quality=94);m2=mb(j2)
                    if abs(m2-prev)<best[0]:best=(abs(m2-prev),j2,m2)
                print(f'frame {i} jump {abs(m-prev):.1f} -> kept {best[0]:.1f}',flush=True);j,m=best[1],best[2]
            prev=m;ff.stdin.write(j)
        ff.stdin.close();ff.wait()
        sp=spikes(tmp)
        if sp>0:print(f'chunk {c//CH} spikes {sp} (kept)',flush=True)
        os.rename(tmp,out);print(f'chunk {c//CH} done {min(N,c+CH)}/{N} {time.time()-t0:.0f}s',flush=True)
    b.close()
print('done',flush=True)
