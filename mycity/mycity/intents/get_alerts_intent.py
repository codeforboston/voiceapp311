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

from bs4 import BeautifulSoup
from urllib import request
from enum import Enum


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
HEADER_2 = "str str--r m-v300"
HEADER_3 = "t--sans t--cb lh--000 m-b500"


def get_alerts_intent(mcd):
    """
    Generate response object with information about citywide alerts
    """
    print(
        '[method: get_alerts_intent]',
        'MyCityDataModel received:\n',
        str(mcd)
    )

    alerts = get_alerts()
    print("[dictionary with alerts scraped from boston.gov]:\n" + str(alerts))
    alerts = prune_normal_responses(alerts)
    print("[dictionary after pruning]:\n" + str(alerts))

    mcd.reprompt_text = None
    mcd.output_speech = alerts_to_speech_output(alerts)
    if has_no_alerts(mcd.output_speech):
        mcd.output_speech = get_no_alerts_response()
    mcd.should_end_session = True   # leave this as True for right now
    return mcd


def alerts_to_speech_output(alerts):
    """
    Return a string that contains all alerts or a message that city services
    are operating normally.
    """
    if len(alerts) == 0:        # there are no alerts!
        return "There are no alerts. City services are operating on their normal schedule."
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
        if service.value in service_alerts and str.find(service_alerts[service.value], "normal") != -1: # this is a leap of faith
            service_alerts.pop(service.value)                       # remove
    if service_alerts[Services.TOW_LOT.value] == tow_lot_normal_message:
        service_alerts.pop(Services.TOW_LOT.value)
    return service_alerts


def get_alerts():
    # get boston.gov as an httpResponse object
    url = request.urlopen(BOSTON_GOV)
    # feed the url object into beautiful soup
    soup = BeautifulSoup(url, "html.parser")
    url.close()

    # parse, sanitize returned strings, place in dictionary
    services = [s.text.strip() for s in soup.find_all(class_= SERVICE_NAMES)]
    service_info = [s_info.text.strip().replace(u'\xA0', u' ') for s_info in soup.find_all(class_= SERVICE_INFO)]
    alerts = {}
    for i in range(len(services)):
        alerts[services[i]] = service_info[i]
    # get alert header, if any (this is something like "Winter Storm warning")
    header = ""
    if soup.find(class_= HEADER_1) is not None:
        header += soup.find(class_= HEADER_1).text + '. '
        header += soup.find(class_= HEADER_2).text + '. '
        header += soup.find(class_= HEADER_3).text + ' '
    alerts[Services.ALERT_HEADER.value] = header.rstrip()
    return alerts


###########################################################
# functions to generate a response if there are no alerts #
###########################################################

def has_no_alerts(speech_output):
    return speech_output == ""

def get_no_alerts_response():
    return "There are no alerts!"
