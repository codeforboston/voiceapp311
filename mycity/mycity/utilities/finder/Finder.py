"""
Abstract parent class upon which subclasses are built that find location
based information about city services

"""

import csv
import requests
import logging

import mycity.utilities.address_utils as address_utils
import mycity.utilities.csv_utils as csv_utils
import mycity.utilities.gis_utils as gis_utils
import mycity.utilities.google_maps_utils as g_maps_utils
import mycity.logger
import logging

logger = logging.getLogger(__name__)

class Finder(object):
    
    """
    Abstracts the logic for finding the closest location to the origin address.
    
    @property: resource_url ::= string that Finder subclass will fetch data from
    @property: address_key ::= string that names the type of location we are finding
    @property: output_speech ::= string that will be passed to request object
        that instantiated the Finder object
    @property: field_formatter ::= function that will access and modify
        fields in the returned record for output_speech formatted string
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
        :param req: MyCityRequestDataModel
        :param resource_url : String that Finder classes will 
            use to GET or query from
        :param address_key: string that names the type of 
            location we are finding
        :param output_speech: String that will be formatted later
            with closest location to origin address. NOTE: this should
            be formatted using keywords as they are expected to appear
            as field in the CSV file or Feature fetched from ArcGIS
            FeatureServer
        :param output_speech_prep_func: function that will access
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
        
        :return: None
        :raises: NotImplementedError
        """
        logger.debug('[method: Finder.get_records]')
        raise NotImplementedError


    def start(self):
        """
        Begins process of retrieving records
        
        All subclasses should provide a get_records for start
        
        :return: None
        """
        logger.debug('[method: Finder.start]')
        records = self.get_records()
        self._start(records)


    def _start(self, records):
        """
        Process list of records and set the output_speech field. output_speech
        will be queried by creator of a Finder object and used to 
        construct a MyCityResponseDataModel
        
        :param records: a list of all location records, records are stored as 
            dictionaries
        :return: None
        """
        logger.debug('[method: Finder._start]' +
              'records[:5]' +
              str(records[:5])
        )
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

        :return: string with speech output or error message
        """
        logger.debug('[method: Finder.get_output_speech]')
        return self.output_speech


    def set_output_speech(self, format_keys):
        """
        Format speech output with values from dictionary format_keys
        
        :param format_keys: dictionary representing the closest record
        :return: None
        """
        logger.debug('[method: Finder.set_output_speech]' +
              'format_keys:' +
              str(format_keys)
        )
        
        try:
            self.output_speech = self.output_speech.format(**format_keys)
        except KeyError:        # our formatted string asked for key we don't
                                # have
            self.output_speech = Finder.ERROR_MESSAGE


    def get_all_destinations(self, records):
        """
        Return a list of all destinations to pass to Google Maps API
        
        :param records: a list of all location records, records are stored as 
            dictionaries
        :return: list of destination address strings
        """
        logger.debug('[method: Finder.get_all_destinations]' +
              'records[:5]:' +
              str(records[:5])
        )
        
        return [record[self.address_key] for record in records]


    def get_driving_info_to_destinations(self, destinations):
        """
        Return a dictionary with address, distance, and driving time from
        self.origin_address for all destinations
        
        :param destinations: list of destination address strings
        :return: list of dictionaries representing driving data for
            each address
        """
        logger.debug('[method: Finder.get_driving_times_to_destinations]' +
              'destinations' +
              str(destinations)
        )
        
        return g_maps_utils._get_driving_info(self.origin_address,
                                              self.address_key,
                                              destinations)


    def get_closest_destination(self, destination_dictionaries):
        """
        Return the dictionary with least driving distance value 
        
        # TODO: review for deletion - function appears not to be used, and
        its logic is implemented in line 102 of this file (Finder.py)
        
        :param destination_dictionaries: 
        :return: 
        """
        logger.debug('[method: Finder.get_closest_destination]' +
              'destination_dictionaries:' +
              str(destination_dictionaries)
        )
        
        return min(destination_dictionaries, 
                   key = lambda destination : \
                       destination[g_maps_utils.DRIVING_DISTANCE_VALUE_KEY])


    def get_closest_record_with_driving_info(self, driving_info, records):
        """
        Find the record corresponding to the destination address
        (driving_info) - which was found to be closest to the origin address.
        Merge the record and destination dictionaries and return the
        resulting dictionary.
        
        :param driving_info: dictionary with address, time to drive to
            address, and distance to the address (representing the closest
            destination to the origin)
        :param records: a list of all location records, records are stored as 
            dictionaries
        :return: a merged dictionary with driving time, driving_distance and all 
            fields from the closest record
        """
        logger.debug('[method: Finder.get_closest_record_with_driving_info]' +
              'driving_info:' +
              str(driving_info) +
              'records:' +
              str(records)
        )
        for record in records:
            if driving_info[self.address_key] == record[self.address_key]:
                return {**record, **driving_info} # NOTE: this will overwrite any
                                                  # common fields (however
                                                  # unlikely) between the two
                                                  # dictionaries             


    def add_city_and_state_to_records(self, records):
        """
        Appends a city and state to the address value of each record
        
        :param records: a list of all location records, records are stored as 
            dictionaries
        :return: list of location dictionaries with updated address values
        """
        logger.debug('[method: Finder.add_city_and_state_to_records]' + 
              'records:' +
              str(records)
        )

        return csv_utils.add_city_and_state_to_records(records,
                                                       self.address_key,
                                                       city=Finder.CITY,
                                                       state=Finder.STATE)


