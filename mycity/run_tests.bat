@echo off
REM Dummy variables must be set in order to avoid key errors during testing.
REM Note:
REM   SLACK_WEBHOOKS_URL is required for AWS Lamba and is set up correctly

if not defined SLACK_WEBHOOKS_URL set SLACK_WEBHOOKS_URL=FAKEFAKEFAKE
python -m unittest discover -v -s mycity\test
