#!/bin/bash

export FRONTEND_BASE_URL="https://mindwarrior-dev.netlify.app/miniapp-frontend/index.html"
export TOKEN="<INSERT_YOUR_TOKEN>"
export ENV="test"
#export ENV="prod"

cd /home/ec2-user/mindwarrior
while echo 1; do
python mindwarrior_bot.py
echo "'mindwarrior_bot.py' crashed with exit code $?. Restarting..." >&2
sleep 1
done

echo "$? - legit stop?"
goto restart
