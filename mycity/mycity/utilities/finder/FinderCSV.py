import csv
import requests

from mycity.utilities.finder.Finder import Finder


class FinderCSV(Finder):
    """
    Finder subclass that uses csv files to find destination addresses

    """

    default_filter = lambda record : record  # filter that filters nothing


    def __init__(self, req, resource_url, address_key, output_speech,
                 output_speech_prep_func, filter = default_filter):
        """
        :param: req: MyCityRequestDataModel
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

        super().__init__(req, resource_url, address_key, output_speech,
                         output_speech_prep_func)
        self._filter = filter


    def get_records(self):
        """
        Subclasses must provide a get_records method. Base class will
        handle all processing

        """
        return self.file_to_filtered_records(self.fetch_resource())
        
        
    def fetch_resource(self):
        print('[method: FinderCSV.fetch_resource]')
        r = requests.get(self.resource_url)
        if r.status_code == 200:
            file_contents = r.content.decode(r.apparent_encoding)
        else:
            file_contents = None
        r.close()
        return file_contents


    def file_to_filtered_records(self, file_contents):
        """
        we don't care to examine results one at a time, just coerce them
        into a list
         
        :param: file_contents: contents from successful GET on resource_url
        """
        print('[method: FinderCSV.file_to_filtered_records]',
              'file_contents:',
              file_contents)
        return list(filter(self._filter,
                           csv.DictReader(file_contents.splitlines(), 
                                          delimiter=',')))
 
