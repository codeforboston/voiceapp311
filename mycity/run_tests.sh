if [ -z "${SLACK_WEBHOOKS_URL}" ]; then
    export SLACK_WEBHOOKS_URL=FAKEFAKEFAKE
fi

python -m unittest discover -v -s mycity/test

