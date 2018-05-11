"""
Parent class for Finder objects. Finder subclasses are defined by the method
they use to find geographical info (GIS, from a CSV file, etc.). Common
attributes

"""
import csv
import requests

import mycity.utilities.google_maps_utils as g_maps_utils


class Finder:
    """
    @property: resource_url ::= string that Finder subclass will fetch data from
    @property: speech_output ::= string that will be passed to request object
    that instantiated the Finder object
    @property: location_type ::= string that represents the name of the location
    type Finder is searching for
    @property: origin_address ::= string that represents the address we will
    calculated driving distances from

    """

    resource_url = None
    output_speech = None
    address_key = None
    origin_address = None


    def __init__(self, resource_url, output_speech, address_key
                 origin_address):
        """
        :param: resource_url : String that Finder classes will 
        use to GET or query from
        :param: output_speech: String that will be formatted later
        with closest location to origin address. NOTE: this should
        be formatted using keywords as they are expected to appear
        as field in the CSV file or Feature fetched from ArcGIS
        FeatureServer
        :param: address_key: string that names the type of 
        location we are finding
        :param: origin_address: string that represents the address
        we are finding directions from
        """
        self.resource_url = resource_url
        self.output_speech = output_speech
        self.address_key = address_key
        self.origin_address = origin_address


    def set_speech_output(self, **format_keys):
        """
        Format speech output with values from dictionary kwargs
        """
        try:
            self.output_speech = self.output_speech.format(**format_keys)
        except KeyError:
            self.output_speech = "Uh oh. Something went wrong!"


    def get_driving_times_to_destinations(self, destinations):
        """
        Return a dictionary with address, distance, and driving time from
        self.origin_address
        """
        return g_maps_utils._get_driving_info(self.origin_address,
                                              self.address_key,
                                              destinations)

    def get_closest_destination(self, destination_dictionaries):
        """
        Return the dictionary with least driving distance value 
        """
        return min(destination_dictionaries, 
                   key = lambda destination : \
                       destination[g_maps_utils.DRIVING_DISTANCE_VALUE_KEY])


    def get_record_with_closest_destination(self, driving_info, records):
        """
        :param: driving_info: dictionary with address, time to drive to
        address, and distance to the address
        :param: records_address_key: key to get the address stored in record
        :param: records: a list of all records, records are stored as 
        dictionaries.
        :return: a dictionary with driving time, driving_distance and all 
        fields from the closest record
        """
        for record in records:
            if driving_info[self.address_key] == records[self.address_key]
                return {**record, **driving_info} # NOTE: this will overwrite any
                                                  # common fields (however
                                                  # unlikely) between the two
                                                  # dictionaries             


    def add_city_and_state_to_records(self, records, address_key, 
                                      city="Boston", state = "MA"):
        return csv_utils.add_city_and_state_to_records(records,
                                                       address_key)
                                 


class FinderCSV(Finder):
    """
    Finder subclass that uses csv files to find destination addresses

    """
    
    _filter = lambda x : x      # default filter returns all records


    def __init__(self, resource_url, output_speech, address_key,
                 origin_address, filter):
        """
         :param: resource_url : String that Finder classes will 
        use to GET or query from
        :param: output_speech: String that will be formatted later
        with closest location to origin address. NOTE: this should
        be formatted using keywords as they are expected to appear
        as field in the CSV file or Feature fetched from ArcGIS
        FeatureServer
        :param: location_type: string that names the type of 
        location we are finding
        :param: origin_address: string that represents the address
        we are finding directions from
        :param: filter that we can use to remove records from csv
        file before using google_maps to find distances and 
        driving_times
        """
        super().__init__(resource_url, output_speech,
                         address_key, origin_address)
        self._filter = filter


    def fetch_resource(self):
        r = requests.get(self.resource_url)
        if r.status_code == 200:
            file_contents = r.content.decode(r.apparent_encoding)
        else:
            file_contents = None
        r.close()
        return file_contents


    def file_to_filtered_records(self, file_contents):
        # since we don't care to examine results one at a time, just coerce them
        # into a list
        return list(filter(self._filter,
                           csv.DictReader(file_contents.splitlines(), 
                                          delimiter=',')))


class FinderGIS(Finder):


    query = "1=1"               # default query returns all records


    def __init__(self, resource_url, output_speech, address_key,
                 origin_address, query):
        super().__init__(resource_url, output_speech,
                         address_key, origin_address)
        self.query = query


    def get_features_from_feature_server():
        pass

    # this needs to return features as dictionaries


    
                                                       
