import requests
from mycity.mycity_response_data_model import MyCityResponseDataModel
from mycity.intents.custom_errors import BadAPIResponse
from mycity.intents.speech_constants.latest_311_constants import *

DEFAULT_NUMBER_OF_REPORTS = 3

BOSTON_311_URL = "https://data.boston.gov/api/3/action/datastore_search"
BOSTON_RESOURCE_ID = "2968e2c0-d479-49ba-a884-4ef523ada3c0"


def get_311_requests(mycity_request):
    """
    Generates response object for a 311 request inquiry.

    :param mycity_request: MyCityRequestDataModel object
    :return: MyCityResponseDataModel object
    """
    mycity_response = MyCityResponseDataModel()

    try:
        number_reports = number_of_reports(mycity_request)

        request_entries = \
            get_311_requests_from_server(number_reports)
        mycity_response.output_speech = \
            REQUEST_311_INTRO_SCRIPT.format(number_reports)
        for request_entry in request_entries:
            mycity_response.output_speech += \
                build_speech_from_311_report(request_entry)

        mycity_response.card_title = REQUEST_311_CARD_TITLE

    except BadAPIResponse:
        mycity_response.output_speech = BAD_API_RESPONSE

    return mycity_response


def number_of_reports(mycity_request):
    """
    Returns number of reports from the request if available or a default value
    :param mycity_request: MyCityRequestDataModel object
    :return: Number of 311 requests to return from this intent
    """
    if REQUEST_311_NUMBER_REPORTS_SLOT_NAME in \
            mycity_request.intent_variables and \
            "value" in mycity_request.intent_variables[
                REQUEST_311_NUMBER_REPORTS_SLOT_NAME]:
        return mycity_request.intent_variables[
                REQUEST_311_NUMBER_REPORTS_SLOT_NAME]["value"]

    return DEFAULT_NUMBER_OF_REPORTS


def get_311_requests_from_server(number_entries):
    """
    Returns the 311 data of the latest number_entries of requests to Boston's
    311

    :param number_entries: Number of entries to return
    :return: JSON object containing array of 311 requests.
    """

    response_json = get_raw_311_reports_json(number_entries)
    return response_json["result"]["records"]


def get_raw_311_reports_json(number_entries):
    """
    Returns the JSON object from the 311 API

    :param number_entries: Number of entries to return
    :return: JSON object containing 311 data
    """
    data_url = BOSTON_311_URL
    parameters = {
        "resource_id": BOSTON_RESOURCE_ID,
        "limit": number_entries
    }

    response = requests.get(data_url, parameters)
    if response.status_code != requests.codes.ok:
        raise BadAPIResponse

    if "result" not in response.json() or \
            "records" not in response.json()["result"]:
        # Unexpected JSON format. Missing expected keys
        raise BadAPIResponse

    return response.json()


def build_speech_from_311_report(report):
    """
    Builds a speech string from a given 311 report
    :param report: JSON object of a single 311 report
    :return: Speech string representing this report
    """

    try:
        subject = report["SUBJECT"]
        report_type = report["TYPE"]
        location = report["LOCATION_STREET_NAME"]
    except KeyError:
        raise BadAPIResponse

    return REQUEST_311_REPORT_SCRIPT.format(location, subject, report_type)
