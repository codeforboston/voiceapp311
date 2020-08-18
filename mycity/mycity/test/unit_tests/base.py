import unittest
import unittest.mock as mock
import mycity.mycity_controller as my_controller
import mycity.mycity_request_data_model as my_req


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.controller = my_controller
        self.request = my_req.MyCityRequestDataModel()
        
    def tearDown(self):
        self.controller = None
        self.request = None

    def _mock_response(
            self,
            status=200,
            content="CONTENT",
            json_data=None,
            raise_for_status=None):
        """
        since we typically test a bunch of different
        requests calls for a service, we are going to do
        a lot of mock responses, so its usually a good idea
        to have a helper function that builds these things
        """
        mock_resp = mock.Mock()
        # mock raise_for_status call w/optional error
        mock_resp.raise_for_status = mock.Mock()
        if raise_for_status:
            mock_resp.raise_for_status.side_effect = raise_for_status
        # set status code and content
        mock_resp.status_code = status
        mock_resp.content = content
        # add json data if provided
        if json_data:
            mock_resp.json = mock.MagicMock(spec=dict,
                return_value=json_data
            )
        return mock_resp
