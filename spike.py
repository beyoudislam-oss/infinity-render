"""spikes(video): count single-frame brightness flashes (frame differs >12 from both neighbours, which agree)."""
import subprocess,numpy as np
def spikes(path,w=48,h=27):
    raw=subprocess.run(['ffmpeg','-v','error','-i',path,'-vf',f'scale={w}:{h},format=gray','-f','rawvideo','-'],capture_output=True).stdout
    a=np.frombuffer(raw,np.uint8).reshape(-1,h*w).astype(float).mean(1) if raw else np.zeros(0)
    n=0
    for i in range(1,len(a)-1):
        if abs(a[i]-a[i-1])>12 and abs(a[i]-a[i+1])>12 and abs(a[i-1]-a[i+1])<4:n+=1
    return n
