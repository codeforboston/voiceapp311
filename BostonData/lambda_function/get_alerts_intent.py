"""
City services in alerts dict:
    Street Cleaning
    Trash and recycling
    City building hours
    Parking meters
    Tow lot

Alerts for day are fetched from dictionary with city service as key


Example:

service_alerts['Street Cleaning'] = "Today is the third Tuesday of the month \\
and street cleaning is running on a normal schedule."


"""


from alexa_utilities import build_response, build_speechlet_response
from streetaddress import StreetAddressParser
from bs4 import BeautifulSoup
import requests
import alexa_constants
import urllib
from enum import Enum
from enum import auto

class Services(Enum):
    STREET_CLEANING = 'Street Cleaning'
    TRASH = 'Trash and recycling'
    CITY_BUILDING_HOURS = 'City building hours'
    PARKING_METERS = 'Parking meters'
    TOW_LOT = 'Tow lot'
    PUBLIC_TRANSIT = 'Public Transit'
    SCHOOLS = 'Schools'
    ALERT_HEADER = 'Alert header'

# constants for scraping boston.gov
BOSTON_GOV = "https://www.boston.gov"
SERVICE_NAMES = "cds-t t--upper t--sans m-b300"
SEVICE_INFO = "cds-d t--subinfo"
HEADER_1 = "t--upper t--sans lh--000 t--cb"
HEADER_2 = "t--upper t--sans lh--000 t--cb"
HEADER_3 = "str str--r m-v300"
HEADER_4 = "t--sans t--cb lh--000 m-b500"
ALT_HEADER_1 = "t--sans t--ob lh--000 m-b500"


def get_alerts_intent(intent, session):
    """
    Generate response object with information about citywide alerts
    """
    reprompt_text=None
    print("IN GET_ALERTS_INFO, SESSION: " + str(session))
    alerts = get_alerts()
    print("DICTIONARY WITH ALERTS SCRAPED FROM BOSTON.GOV: " + str(alerts))
    alerts = prune_normal_responses(alerts)
    print("DICTIONARY AFTER PRUNING: " + str(alerts))
    speech_output = alerts_to_speech_output(alerts)
    session_attributes = session.get('attributes', {})
    should_end_session = True   # leave this as True for right now
    return build_response(session_attributes, build_speechlet_response(
            intent['name'], speech_output, reprompt_text, should_end_session))


def alerts_to_speech_output(alerts):
    """
    Return a string that contains all alerts or a message that city services are operating normally
    """
    if len(alerts) == 0:        # there are no alerts!
        return "There are no alerts. City services are operating on their normal schedule"
    else:
        all_alerts = ""
        all_alerts += alerts.pop(Services.ALERT_HEADER.value)
        for alert in alerts.values():
            all_alerts += alert + ' '
        return all_alerts
        

def prune_normal_responses(service_alerts):
    """
    Remove any text scraped from Boston.gov that aren't actually alerts.
    For example, parking meters, city building hours, and trash and 
    recycling are described "as on a normal schedule"
    """

    tow_lot_normal_message = "The tow lot is open from 7 a.m. - 11 p.m. "
    tow_lot_normal_message += "Automated kiosks are available 24 hours a day, "
    tow_lot_normal_message += "seven days a week for vehicle releases."

    # for any defined service, if its alert is that it's running normally, 
    # remove it from the dictionary
    for service in Services:
        if service.value in service_alerts and \
                str.find(service_alerts[service.value], "normal") != -1: # this is a leap of faith
            service_alerts.pop(service.value)                       # remove
    if service_alerts[Services.TOW_LOT.value].rstrip() == tow_lot_normal_message:
        service_alerts.pop(Services.TOW_LOT.value) # not sure comparison is working - 3.27.2018
    return service_alerts

def get_alerts():
    url = urllib.request.urlopen(BOSTON_GOV) # get page
    soup = BeautifulSoup(url, "html.parser")               # feed into BS
    url.close()
    # parse, sanitize returned strings, place in dictionary
    services = [s.text.strip() for s in soup.find_all(class_ = SERVICE_NAMES)]
    service_info = [s_info.text.strip().replace(u'\xA0', u' ') for s_info in soup.find_all(class_ = SERVICE_INFO)]
    alerts = {}
    for i in range(len(services)):
        alerts[services[i]] = service_info[i]
    # get alert header, if any (this is something like "Winter Storm warning")
    header = ""
    if soup.find(class_ = HEADER_1) != None: # no guarantee that this tag will always be the header
        header += soup.find(class_ = HEADER_2).text + '. '
        header += soup.find(class_ = HEADER_3).text + '. ' 
        header += soup.find(class_ = HEADER_4).text + ' '

    if soup.find(class_ = ALT_HEADER_1) != None: # another possible header tag, again this might change 
        header += soup.find(class_ = ALT_HEADER_1).text
    alerts[Services.ALERT_HEADER.value] = header.rstrip()
    return alerts
