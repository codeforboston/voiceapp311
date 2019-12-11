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
        If the recollect API returns multiple possibilities for a given address query,
        we need to ask the user which one they meant. As we find more cases for address
        similarity, we should add them as tests here so we avoid asking the user about
        similar addresses
        """
        fake_response_partial = [
            {"name": name}
            for name in [
                "123 Street Rd, Brookline 02445"
            ]
        ]
        expected_options = [
            "123 Street Rd, Brookline 02445"
        ]
        # for _ in range(3):
        # Ordering of the payload shouldn't matter
        # random.shuffle(fake_response_partial)
        found_addresses = find_unique_address(fake_response_partial)
        # We don't care about ordering really, so comparing sorted is easiest
        self.assertListEqual((expected_options), (found_addresses))

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
