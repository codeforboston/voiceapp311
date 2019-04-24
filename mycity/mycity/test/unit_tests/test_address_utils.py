from streetaddress import StreetAddressParser

from mycity.intents import intent_constants
from mycity.test.unit_tests.base import BaseTestCase
from mycity.utilities import address_utils


class AddressUtilitiesTestCase(BaseTestCase):

    def change_address(self, new_address):
        self.request.session_attributes[intent_constants.CURRENT_ADDRESS_KEY] = \
            new_address

    def compare_built_address(self, expected_result):
        origin_addr = address_utils.build_origin_address(self.request)
        self.assertEqual(origin_addr, expected_result)

    def test_build_origin_address_with_normal_address(self):
        self.change_address("46 Everdean St.")
        self.compare_built_address("46 Everdean St Boston MA")

    def test_valid_address_is_validated(self):
        address = StreetAddressParser().parse("46 Everdean St")
        self.assertTrue(address_utils.is_address_valid(address))

    def test_missing_street_name_is_not_validated(self):
        address = StreetAddressParser().parse("46")
        self.assertFalse(address_utils.is_address_valid(address))

    def test_missing_street_number_is_not_validated(self):
        address = StreetAddressParser().parse("Everdean St")
        self.assertFalse(address_utils.is_address_valid(address))
