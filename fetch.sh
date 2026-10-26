#!/bin/bash
# usage: fetch.sh RUN_ID DEST_DIR  -> downloads finished artifacts, writes DEST/part_NN.mp4 (overwrites). Prints job status.
cd /tmp; R=$1; D=$2; A="Authorization: Bearer $GITHUB_ACCESS_TOKEN"; B=https://api.github.com/repos/beyoudislam-oss/infinity-render
curl -s -H "$A" "$B/actions/runs/$R/jobs?per_page=50" | python3 -c "import sys,json;J=json.load(sys.stdin)['jobs'];print('jobs:',len(J),'done',sum(j['status']=='completed' for j in J),'failed',[j['name'] for j in J if j['conclusion'] not in (None,'success')])"
curl -s -H "$A" "$B/actions/runs/$R/artifacts?per_page=100" | python3 -c "import sys,json;[print(a['id'],a['name']) for a in json.load(sys.stdin)['artifacts']]" | while read id name; do
  mkdir -p /app/studio/tools/ghr/dl/$name; z=/app/studio/tools/ghr/dl/$name.zip
  [ -f $z ] || curl -sL -H "$A" "$B/actions/artifacts/$id/zip" -o $z
  python3 -c "import zipfile,sys;zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" $z /app/studio/tools/ghr/dl/$name && cp /app/studio/tools/ghr/dl/$name/part_*.mp4 $D/ && echo "got $name"
done
