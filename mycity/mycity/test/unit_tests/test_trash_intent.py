import random

from mycity.intents.trash_intent import find_unique_addresses
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
                "123 Street Rd, Brookline 02445",
                "123 Street Rd, Brookline 02445 Unit 1",
                "123 Street Rd, Brookline 02445 Unit 2",
                "456 Road St, South Boston 02127",
                "456 Road St, South Boston 02127 #1",
                "456 Road St, South Boston 02127 #2",
                "789 Lane Ave, Allston 02134",
                "1 - 789 Lane Ave, Allston 02134",
                "2 - 789 Lane Ave, Allston 02134",
                "I am all alone, no substrings or superstrings",
            ]
        ]
        expected_options = [
            "123 Street Rd, Brookline 02445",
            "456 Road St, South Boston 02127",
            "789 Lane Ave, Allston 02134",
            "I am all alone, no substrings or superstrings",
        ]
        for _ in range(3):
            # Ordering of the payload shouldn't matter
            random.shuffle(fake_response_partial)
            found_addresses = find_unique_addresses(fake_response_partial)
            # We don't care about ordering really, so comparing sorted is easiest
            self.assertListEqual(sorted(expected_options), sorted(found_addresses))
