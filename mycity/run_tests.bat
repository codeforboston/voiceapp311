@echo off
REM Dummy variables must be set in order to avoid key errors during testing.
REM Note:
REM   See issue #187 for removing GOOGLE_MAPS_API_KEY can be removed along with this comment
REM   SLACK_WEBHOOKS_URL is required for AWS Lamba and is set up correctly

if not defined SLACK_WEBHOOKS_URL set SLACK_WEBHOOKS_URL=FAKEFAKEFAKE
if not defined GOOGLE_MAPS_API_KEY set GOOGLE_MAPS_API_KEY=FAKEFAKEFAKE
python -m unittest discover -v -s mycity\test
