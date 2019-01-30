
# see issue #187 to determine if GOOGLE_MAPS_API can be removed along with this comment.
if [ -z "${GOOGLE_MAPS_API_KEY}" ];then
    export GOOGLE_MAPS_API_KEY=FAKEFAKEFAKE
fi

if [ -z "${SLACK_WEBHOOKS_URL}" ]; then
    export SLACK_WEBHOOKS_URL=FAKEFAKEFAKE
fi

python -m unittest discover -v -s mycity/test

