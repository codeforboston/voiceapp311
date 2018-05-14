import mycity.utilities.Finder.Finder as Finder 


class FinderGIS(Finder.Finder):


    default_query = "1=1"               # default query returns all records


    def __init__(self, req, resource_url, address_key, output_speech,
                 output_speech_prep_func, query = FinderGIS.default_query):
        """
        Call super constructor and save 
        """
        super().__init__(req, resource_url, address_key, output_speech,
                         output_speech_prep_func)
        self.query = query


    def get_features_from_feature_server():
        print("[method: FinderGIS.get_features_from_feature_server]")
        return gis_utils.get_features_from_feature_server(self.resource_url,
                                                          self.query)
