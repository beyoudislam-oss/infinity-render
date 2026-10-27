import os,sys,json,base64,urllib.request
img,prompt,model=sys.argv[1],open(sys.argv[2]).read(),sys.argv[3]
b=base64.b64encode(open(img,'rb').read()).decode()
body={"model":model,"messages":[{"role":"user","content":[{"type":"text","text":prompt},{"type":"image_url","image_url":{"url":"data:image/jpeg;base64,"+b}}]}]}
r=urllib.request.Request("https://models.github.ai/inference/chat/completions",json.dumps(body).encode(),{"Authorization":"Bearer "+os.environ["GITHUB_TOKEN"],"Content-Type":"application/json"})
try:
  resp=urllib.request.urlopen(r,timeout=120);raw=resp.read().decode()
  print("STATUS",resp.status,"RAW",raw[:300])
  out=json.loads(raw)["choices"][0]["message"]["content"]
except urllib.error.HTTPError as e: out="HTTPERR %s %s"%(e.code,e.read().decode()[:500])
except Exception as e0: out="ERR %r"%e0
print("=====ANSWER=====");print(out);open("answer.txt","w").write(out)
