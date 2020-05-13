"""
Speech utterances for get_alerts_intent.py

"""

NO_ALERTS = "There are no alerts. City services are running on normal schedules."
NO_INCLEMENT_WEATHER_ALERTS = "There are no weather related alerts"

LAUNCH_REPROMPT_SPEECH = "You can also ask about the locations of " \
    "food trucks and farmer's markets, or info about snow emergencies. " \
    "If you have feedback for the skill say 'I have a suggestion'."
ALERT_LISTING_SCRIPT = "There are {} current alerts affecting the following " \
    "services: {}. Which one would you like to hear about? Or pick 'all'."
INVALID_DECISION_SCRIPT = "Sorry, I didn't understand that. "