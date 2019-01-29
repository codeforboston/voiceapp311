# Dummy variables must be set in order to avoid KeyError being raised during testing

# see issue #187 to determine if GOOGLE_MAPS_API can be removed along with this comment.
export GOOGLE_MAPS_API_KEY=FAKEFAKEFAKE

export SLACK_WEBHOOKS_URL=FAKEFAKEFAKE

python -m unittest discover -v -s mycity/test
