import mycity.intents.intent_constants as intent_constants
import mycity.test.unit_tests.base as base
import mycity.utilities.address_utils as address_utils



class AddressUtilitiesTestCase(base.BaseTestCase):

    def change_address(self, new_address):
        self.request.session_attributes[intent_constants.CURRENT_ADDRESS_KEY] = \
            new_address

    def compare_built_address(self, expected_result):
        origin_addr = address_utils.build_origin_address(self.request)
        self.assertEqual(origin_addr, expected_result)
 
    def test_build_origin_address_with_normal_address(self):
        self.change_address("46 Everdean St.")
        self.compare_built_address("46 Everdean St Boston MA")
