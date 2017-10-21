from lambda_function.lambda_function import *
import requests

def get_trash_day_info(intent, session):
    """
    Generates response object for a trash day inquiry.
    """
    reprompt_text = None
    print("IN GET_TRASH_DAY_INFO, SESSION: " + str(session))

    if "currentAddress" in session.get('attributes', {}):
        current_address = session['attributes']['currentAddress']

        # grab relevant information from session address
        addr_parser = StreetAddressParser()
        a = addr_parser.parse(current_address)
        # currently assumes that trash day is the same for all units at
        # the same street address
        address = str(a['house']) + " " + str(a['street_name'])

        # rest call to data.boston.gov for trash/recycle information
        url = 'https://data.boston.gov/api/action/datastore_search?' + \
              'resource_id=fee8ee07-b8b5-4ee5-b540-5162590ba5c1&q=' + \
              '{{"Address":"{}"}}'.format(address)
        resp = requests.get(url).json()
        print("RESPONSE FROM DATA.BOSTON.GOV: " + str(resp))

        # format script of response
        record = resp['result']['records'][0]
        speech_output = "Trash is picked up on the following days, " + \
                ", ".join(parseDays(record['Trash'])) + \
                ". Recycling is picked up on the following days, " + \
                " ,".join(parseDays(record['Recycling']))

        session_attributes = session.get('attributes', {})
        should_end_session = False
    else:
        session_attributes = session.get('attributes', {})
        speech_output = "I'm not sure what your address is. " \
                        "You can tell me your address by saying, " \
                        "my address is 123 Main St., apartment 3."
        should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))
