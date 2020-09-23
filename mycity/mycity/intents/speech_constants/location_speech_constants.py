"""
Speech constants related to determining whether the user is in Boston or not.
"""

GENERIC_GEOLOCATION_PERMISSON_SPEECH = """
    Boston Info would like to use your location. 
    To turn on location sharing, please go to your Alexa app and 
    follow the instructions. Alternatively, you can provide an address when
    asking a question."""

GENERIC_DEVICE_PERMISSON_SPEECH = """
    Boston Info would like to use your device's address. 
    To turn on location sharing, please go to your Alexa app and 
    follow the instructions. Alternatively, you can provide an address when
    asking a question."""

NOT_IN_BOSTON_SPEECH = 'This address is not in Boston. ' \
                       'Please use this skill with a Boston address. '\
                       'See you later!'
