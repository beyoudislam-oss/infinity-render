#!/bin/bash
# usage: dispatch.sh LOCAL_HTML JOBNAME DUR "52,53,54 55,56" [WxH]   (needs $GITHUB_ACCESS_TOKEN via get_connector_token github)
set -e; cd /app/studio/tools/ghr; mkdir -p jobs/$2; cp "$1" jobs/$2/film.html
git add -A; git -c user.email=bot@infinity -c user.name=infinity commit -qm "job $2 $(date +%H%M)" || true; git push -q
G=$(python3 -c "import json,sys;print(json.dumps(json.dumps(sys.argv[1].split())))" "$4")
curl -s -o /dev/null -w "dispatch %{http_code}\n" -X POST -H "Authorization: Bearer $GITHUB_ACCESS_TOKEN" https://api.github.com/repos/beyoudislam-oss/infinity-render/actions/workflows/render.yml/dispatches -d "{\"ref\":\"main\",\"inputs\":{\"html\":\"jobs/$2/film.html\",\"dur\":\"$3\",\"groups\":$G,\"size\":\"${5:-1920x1080}\"}}"
sleep 8; curl -s -H "Authorization: Bearer $GITHUB_ACCESS_TOKEN" "https://api.github.com/repos/beyoudislam-oss/infinity-render/actions/runs?per_page=1" | python3 -c "import sys,json;r=json.load(sys.stdin)['workflow_runs'][0];print('RUN',r['id'],r['status'])"
