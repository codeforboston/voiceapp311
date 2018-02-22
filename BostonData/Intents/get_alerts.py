from bs4 import BeautifulSoup
import urllib.request

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

def get_alerts():
    url = urllib.request.urlopen("https://www.boston.gov") # get page
    soup = BeautifulSoup(url, "html.parser")               # feed into BS
    url.close()
    # parse, sanitize returned strings, place in dictionary
    service_alerts = {s.text.strip().replace(u'\xA0', u' ') : s_info.text.strip().replace(u'\xA0', u' ') \
                          for s in soup.find_all(class_ = "cds-t t--upper t--sans m-b300") \
                          for s_info in soup.find_all(class_ = "cds-d t--subinfo")}
    return service_alerts
