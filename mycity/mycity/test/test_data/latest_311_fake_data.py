"""
Data used for testing latest 311 intent
"""

FAKE_SUBJECT_1 = "Public Health Department"
FAKE_TYPE_1 = "Eating Plain M and Ms"
FAKE_LOCATION_1 = "Jamie's House"
FAKE_JSON_DATA_1 = {
    "subject": FAKE_SUBJECT_1,
    "type": FAKE_TYPE_1,
    "location_street_name": FAKE_LOCATION_1,
}

FAKE_SUBJECT_2 = "Police Issues"
FAKE_TYPE_2 = "Loud Metal Music"
FAKE_LOCATION_2 = "Jason's House"
FAKE_JSON_DATA_2 = {
    "subject": FAKE_SUBJECT_2,
    "type": FAKE_TYPE_2,
    "location_street_name": FAKE_LOCATION_2,
}

FAKE_SUBJECT_3 = "Parks and Recreation"
FAKE_TYPE_3 = "Streaming Movies Since The Downfall Of MoviePass"
FAKE_LOCATION_3 = "Josh's House"
FAKE_JSON_DATA_3 = {
    "subject": FAKE_SUBJECT_3,
    "type": FAKE_TYPE_3,
    "location_street_name": FAKE_LOCATION_3,
}

FAKE_JSON_RESPONSE_1 =\
    {
        "result": {
            "records": [
              FAKE_JSON_DATA_1
            ]
        }
    }

FAKE_JSON_RESPONSE_3 = \
    {
        "result": {
            "records": [
                FAKE_JSON_DATA_1,
                FAKE_JSON_DATA_2,
                FAKE_JSON_DATA_3
            ]
        }
    }
