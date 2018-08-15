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
from mycity.mycity_response_data_model import MyCityResponseDataModel
import mycity.logger
import logging


logger = logging.getLogger(__name__)

class Services(Enum):
    
    """
    Organizes and contains information about all possible alert types
    that are supported in a readable format.
    
    """
    
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
SERVICE_INFO = "cds-d t--subinfo"
HEADER_1 = "t--upper t--sans lh--000 t--cb"
HEADER_2 = "str str--r m-v300"
HEADER_3 = "t--sans t--cb lh--000 m-b500"


def get_alerts_intent(mycity_request):
    """
    Generate response object with information about citywide alerts

    :param mycity_request: MyCityRequestDataModel object
    :return: MyCityResponseDataModel object
    """
    logger.debug(
                 'MyCityRequestDataModel received:\n' +
                 str(mycity_request)
    )

    mycity_response = MyCityResponseDataModel()
    alerts = get_alerts()
    logger.debug("[dictionary with alerts scraped from boston.gov]:\n" + str(alerts))
    alerts = prune_normal_responses(alerts)
    logger.debug("[dictionary after pruning]:\n" + str(alerts))
    mycity_response.session_attributes = mycity_request.session_attributes
    mycity_response.card_title = "City Alerts"
    mycity_response.reprompt_text = None
    mycity_response.output_speech = alerts_to_speech_output(alerts)
    mycity_response.should_end_session = True   # leave this as True for right now
    return mycity_response


def alerts_to_speech_output(alerts):
    """
    Checks whether the alert dictionary contains any entries. Returns a string
    that contains all alerts or a message that city services are operating
    normally.
    
    :param alerts: pruned alert dictionary
    :return: a string containing all alerts, or if no alerts are
        found, a message indicating there are no alerts at this time
    """
    all_alerts = ""
    if Services.ALERT_HEADER.value in all_alerts:
        all_alerts += alerts.pop(Services.ALERT_HEADER.value)
    for alert in alerts.values():
        all_alerts += alert + ' '
    if all_alerts.strip() == "":        # this is a kludgy fix for the {'alert header': ''} bug 
        return "There are no alerts. City services are running on normal schedules."       
    else:
        return all_alerts
        

def prune_normal_responses(service_alerts):
    """
    Remove any text scraped from Boston.gov that aren't actually alerts.
    For example, parking meters, city building hours, and trash and 
    recycling are described "as on a normal schedule"
    
    :param service_alerts: raw alerts dictionary, potentially with unrelated
        non-alert data
    :return: pruned alert dictionary containing only the current
        alert information
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
    """
    Checks Boston.gov for alerts, and if present scrapes them and returns
    them as a dictionary
    
    :return: a dictionary that maps alert names to detailed alert message
    """
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
    # weird bug where a blank header was appended to dictionary. this should
    # prevent that
    if header != '':
        alerts[Services.ALERT_HEADER.value] = header.rstrip()
    return alerts
