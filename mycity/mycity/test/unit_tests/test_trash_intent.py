import random
import unittest
import unittest.mock as mock

from mycity.intents.trash_intent import find_unique_address, get_trash_day_info
import mycity.intents.intent_constants as intent_constants
from mycity.mycity_request_data_model import MyCityRequestDataModel
from mycity.test.unit_tests import base


class TrashIntentTestCase(base.BaseTestCase):
    def test_multiple_address_options(self):
        """
        If a user gives address query that is in multiple neighborhood,
        we return only first address since recollect API returns the first address.
        """
        fake_response_partial = {'area_id': 311, 'parcel_id': 50750030, 'area_name': 'Boston', 'name': '30 Beach St, Boston 02111', 'place_id': 'EF0C71EA-76B9-11E9-A82C-1A7E437A767B', 'service_id': 310}, {'area_id': 311, 'parcel_id': 50710552, 'place_id': '55909586-849D-11E9-BA56-31A8A53F0116', 'service_id': 310, 'name': '30 Beach St, Dorchester 02122', 'area_name': 'Boston'}, {'place_id': '760AC626-80B3-11E9-9DDD-61FE786D1E41', 'service_id': 310, 'name': '1 - 30 Beach St, Dorchester 02122', 'area_name': 'Boston', 'area_id': 311, 'parcel_id': 50408592}, {'parcel_id': 50409108, 'area_id': 311, 'area_name': 'Boston', 'name': '30-1 - 30 Beach St, Dorchester 02122', 'service_id': 310, 'place_id': '7B3F0B5C-80B3-11E9-9FC3-61FE786D1E41'}, {'parcel_id': 50409106, 'area_id': 311, 'name': '30-3 - 30 Beach St, Dorchester 02122', 'area_name': 'Boston', 'service_id': 310, 'place_id': '7B3B3E00-80B3-11E9-9FC3-61FE786D1E41'}, {'service_id': 310, 'place_id': '7B3D3CB4-80B3-11E9-9FC3-61FE786D1E41', 'name': '30-2 - 30 Beach St, Dorchester 02122', 'area_name': 'Boston', 'parcel_id': 50409107, 'area_id': 311}
        expected_options = [
            "30 Beach St, Boston 02111"
        ] # ["30 Beach St, Boston 02111"]
        found_addresses = find_unique_address(fake_response_partial)
        self.assertListEqual(expected_options, found_addresses)

        fake_response_partial2 = {'area_id': 311, 'area_name': 'Boston', 'service_id': 310, 'parcel_id': 50773210, 'place_id': 'C326E9FE-849F-11E9-9A9D-509DA9D9E44A', 'name': '10 Main St, Charlestown 02129'}, {'area_id': 311, 'place_id': '42A400A2-849D-11E9-BA56-31A8A53F0116', 'name': '10 W Main St, Dorchester 02126', 'parcel_id': 50708112, 'service_id': 310, 'area_name': 'Boston'}, {'area_id': 311, 'place_id': 'CF6E847C-80B4-11E9-8F6A-6DFE786D1E41', 'name': '407 - 10 W Main St, Dorchester 02124', 'parcel_id': 50398721, 'service_id': 310, 'area_name': 'Boston'}
        expected_options = [
            "10 Main St, Charlestown 02129"
        ]# ["10 Main St, Charlestown 02129"]
        found_addresses2 = find_unique_address(fake_response_partial2)
        self.assertListEqual(expected_options, found_addresses2)



    @mock.patch('mycity.intents.trash_intent.get_address_from_user_device')
    def test_requests_device_address_permission(self, mock_get_address):
        mock_get_address.return_value = (MyCityRequestDataModel(), False)
        request = MyCityRequestDataModel()
        response = get_trash_day_info(request)
        self.assertTrue("read::alexa:device:all:address" in response.card_permissions)

    @mock.patch('mycity.intents.trash_intent.get_address_from_user_device')
    def test_requests_user_supplied_address_when_no_device_address_set(self, mock_get_address):
        mock_get_address.return_value = (MyCityRequestDataModel(), True)
        request = MyCityRequestDataModel()
        response = get_trash_day_info(request)
        self.assertEqual("Address", response.card_title)

    @mock.patch('mycity.intents.trash_intent.get_address_from_user_device')
    @mock.patch('mycity.intents.trash_intent.get_trash_and_recycling_days')
    def test_does_not_get_device_address_if_desired_address_provided(self, mock_get_days, mock_get_address):
        mock_get_days.return_value = ["Monday"]
        request = MyCityRequestDataModel()
        request.session_attributes[intent_constants.CURRENT_ADDRESS_KEY] = "10 Main Street Boston MA"
        get_trash_day_info(request)
        mock_get_address.assert_not_called()

    @mock.patch('mycity.intents.trash_intent.get_address_from_user_device')
    @mock.patch('mycity.intents.trash_intent.get_trash_and_recycling_days')
    def test_does_not_require_boston_address_if_desired_address_provided(self, mock_get_days, mock_get_address):
        device_address_request = MyCityRequestDataModel()
        device_address_request.session_attributes[
            intent_constants.CURRENT_ADDRESS_KEY] \
            = "10 Main Street New York NY"
        mock_get_address.return_value = device_address_request, True

        mock_get_days.return_value = ["Monday"]
        request = MyCityRequestDataModel()
        request.session_attributes[intent_constants.CURRENT_ADDRESS_KEY] = "10 Main Street Boston MA"
        result = get_trash_day_info(request)
        self.assertTrue("Monday" in result.output_speech)

    @mock.patch('mycity.intents.trash_intent.get_trash_and_recycling_days')
    def test_provided_address_must_be_in_city(self, mock_get_days):
        mock_get_days.return_value = ["Monday"]
        request = MyCityRequestDataModel()
        request.session_attributes[intent_constants.CURRENT_ADDRESS_KEY] = "10 Main Street New York, NY"
        result = get_trash_day_info(request)
        self.assertFalse("Monday" in result.output_speech)


if __name__ == '__main__':
    unittest.main()
