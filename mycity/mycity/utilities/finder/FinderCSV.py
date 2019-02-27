"""
Uses csv files to find location based information about Boston city services
"""

import csv
import requests
from mycity.utilities.finder.Finder import Finder
import logging

logger = logging.getLogger(__name__)


class FinderCSV(Finder):
    
    """
    Finder subclass that uses csv files to find destination addresses

    @property: filter ::= filter function to conditionally remove records
    
    """
    default_filter = lambda record : record  # filter that filters nothing

    def __init__(
            self,
            req,
            resource_url,
            address_key,
            output_speech,
            output_speech_prep_func,
            filter = default_filter
    ):
        """
        Call super constructor and save filter

        :param req: MyCityRequestDataModel
        :param resource_url: String that Finder classes will 
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
        :param filter: filter that we can use to remove records from csv
            file before using a service to find distances and 
            driving_times
        """

        super().__init__(
            req,
            resource_url,
            address_key,
            output_speech,
            output_speech_prep_func
        )
        self._filter = filter

    def get_records(self):
        """
        Get web csv resource and format its information
        
        Subclasses must provide a get_records method. Base class will
        handle all processing

        :return: list of dictionaries representing the resource csv file
        """
        logger.debug('')
        return self.file_to_filtered_records(self.fetch_resource())

    def fetch_resource(self):
        """
        Make api call to get csv resource and return it as a string
        
        :return: a string representation of the csv file
        """
        logger.debug('')

        r = requests.get(self.resource_url)
        if r.status_code == 200:
            file_contents = r.content.decode(r.apparent_encoding)
        else:
            file_contents = None
        r.close()
        return file_contents

    def file_to_filtered_records(self, file_contents):
        """
        Convert the string representation of the csv file into a list of
        dictionaries, each representing one record
        
        :param file_contents: contents from successful GET on resource_url,
            a string representation of the csv file
        :return: a list of dictionaries (OrderedDict) each representing one
            row from the csv
        """
        logger.debug('file_contents:' + str(file_contents).replace('\n', '\r'))
        return list(
            filter(
                self._filter,
                csv.DictReader(
                   file_contents.splitlines(),
                   delimiter=','
                )
            )
        )
