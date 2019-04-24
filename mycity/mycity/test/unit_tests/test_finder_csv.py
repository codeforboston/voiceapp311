from mycity.test.unit_tests.base import BaseTestCase
from mycity.utilities.finder.finder_csv import FinderCSV


class FinderCSVTestCase(BaseTestCase):

    def setUp(self):
        def test_prep_func(keys):
            if keys["Address"] == "123 Fake St Boston, MA":
                keys["Address"] = "123 Real St Boston, MA"
        super().setUp()
        fake_url = "www.fake.com"
        address_key = "Address"
        output_speech = "Trying to get {name}, {" + address_key + "}, " \
            + "{Driving distance text}."
        self.request.session_attributes['currentAddress'] = \
            '1000 Dorchester Ave'
        self.finder = FinderCSV(self.request, fake_url, address_key,
                                output_speech, test_prep_func)

    def tearDown(self):
        self.finder = None
        super().tearDown()

    def test_get_output_speech_with_success(self):
        self.finder.set_output_speech({
            'Address': '123 Fake St Boston, MA',
            'name': 'The Place',
            'Driving distance text': '100 miles away'
        })
        self.assertEqual(
            "Trying to get The Place, 123 Fake St Boston, MA, 100 miles away.",
            self.finder.output_speech
        )

    def test_get_output_speech_after_error(self):
        self.finder.set_output_speech(
            {'MissingKeys': 'Address, name, distance'}
        )
        self.assertEqual(self.finder.ERROR_MESSAGE, self.finder.output_speech)
