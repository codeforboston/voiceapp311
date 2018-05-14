import csv
import requests

import mycity.utilities.address_utils as address_utils
import mycity.utilities.csv_utils as csv_utils
import mycity.utilities.gis_utils as gis_utils
import mycity.utilities.google_maps_utils as g_maps_utils


class Finder(object):
    """
    @property: resource_url ::= string that Finder subclass will fetch data from
    @property: speech_output ::= string that will be passed to request object
    that instantiated the Finder object
    @property: location_type ::= string that represents the name of the location
    type Finder is searching for
    @property: origin_address ::= string that represents the address we will
    calculated driving distances from

    """

    address_builder = address_utils.build_origin_address
    CITY = "Boston"
    STATE = "MA"
    ERROR_MESSAGE = "Uh oh. Something went wrong!"


    def __init__(self, req, resource_url, address_key, output_speech, 
                 output_speech_prep_func):
        """
        :param: req: MyCityRequestDataModel
        :param: resource_url : String that Finder classes will 
        use to GET or query from
        :param: address_key: string that names the type of 
        location we are finding
        :param: output_speech: String that will be formatted later
        with closest location to origin address. NOTE: this should
        be formatted using keywords as they are expected to appear
        as field in the CSV file or Feature fetched from ArcGIS
        FeatureServer
        :param: output_speech_prep_func: function that will access
        and modify fields in the returned record for output_speech
        formatted string
        """
        self.resource_url = resource_url
        self.address_key = address_key
        self.output_speech = output_speech
        self.field_formatter = output_speech_prep_func
        self.origin_address = Finder.address_builder(req) # pull the origin
                                                          # address from request
                                                          # data model


    def get_records(self):
        """
        Raise a not implemented error if python tries to call this on the base
        class. Subclasses should implement this themselves
        """
        print('[method: Finder.get_records]')
        raise NotImplementedError


    def start(self):
        """
        All subclasses should provide a get_records for start 
        """
        print('[method: Finder.start]')
        records = self.get_records()
        self._start(records)


    def _start(self, records):
        """
        Process list of records and 
        :param: records - information about locations with each location's
        info stored as a dictionary
        :ret: None
        """
        print('[method: Finder._start]',
              'records[:5]',
              records[:5])
        records = self.add_city_and_state_to_records(records)
        destinations = self.get_all_destinations(records)
        driving_info = self.get_driving_info_to_destinations(destinations)
        closest_dest = \
            min(driving_info, 
                key = lambda destination : \
                    destination[g_maps_utils.DRIVING_DISTANCE_VALUE_KEY])

        closest_record = \
            self.get_closest_record_with_driving_info(closest_dest,
                                                      records)
        formatted_record = self.field_formatter(closest_record)
        self.set_output_speech(closest_record)    

        
    def get_output_speech(self):
        """
        Return formatted speech output or the standard error message

        """
        print('[method: Finder.get_output_speech]')
        return self.output_speech


    def set_output_speech(self, format_keys):
        """
        Format speech output with values from dictionary format_keys
        
        """
        print('[method: Finder.set_output_speech]',
              'format_keys:',
              format_keys)
        try:
            self.output_speech = self.output_speech.format(**format_keys)
        except KeyError:        # our formatted string asked for key we don't
                                # have
            self.output_speech = ERROR_MESSAGE


    def get_all_destinations(self, records):
        """
        Return a list of all destinations to pass to Google Maps API
        
        """
        print('[method: Finder.get_all_destinations]',
              'records[:5]:',
              records[:5])
        return [record[self.address_key] for record in records]


    def get_driving_info_to_destinations(self, destinations):
        """
        Return a dictionary with address, distance, and driving time from
        self.origin_address for all destinations
        
        """
        print('[method: Finder.get_driving_times_to_destinations]',
              'destinations',
              destinations)
        return g_maps_utils._get_driving_info(self.origin_address,
                                              self.address_key,
                                              destinations)


    def get_closest_destination(self, destination_dictionaries):
        """
        Return the dictionary with least driving distance value 
        """
        print('[method: Finder.get_closest_destination]',
              'destination_dictionaries:',
              destination_dictionaries)
        return min(destination_dictionaries, 
                   key = lambda destination : \
                       destination[g_maps_utils.DRIVING_DISTANCE_VALUE_KEY])


    def get_closest_record_with_driving_info(self, driving_info, records):
        """
        :param: driving_info: dictionary with address, time to drive to
        address, and distance to the address
        :param: records_address_key: key to get the address stored in record
        :param: records: a list of all records, records are stored as 
        dictionaries.
        :return: a dictionary with driving time, driving_distance and all 
        fields from the closest record
        """
        print('[method: Finder.get_closest_record_with_driving_info]',
              'driving_info:',
              driving_info,
              'records:',
              records)
        for record in records:
            if driving_info[self.address_key] == record[self.address_key]:
                return {**record, **driving_info} # NOTE: this will overwrite any
                                                  # common fields (however
                                                  # unlikely) between the two
                                                  # dictionaries             


    def add_city_and_state_to_records(self, records):
        print('[method: Finder.add_city_and_state_to_records]',
              'records:',
              records)
        return csv_utils.add_city_and_state_to_records(records,
                                                       self.address_key,
                                                       city=Finder.CITY,
                                                       state=Finder.STATE)


