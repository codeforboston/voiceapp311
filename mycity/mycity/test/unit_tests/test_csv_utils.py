import csv
import collections
import unittest.mock as mock

import mycity.test.test_constants as test_constants
import mycity.test.unit_tests.base as base
import mycity.utilities.csv_utils as csv_utils



class CSVUtilitiesTestCase(base.BaseTestCase):

    def test_create_record_model(self):
        Record = collections.namedtuple('TestRecord', ['field_1', 'field_2'])
        to_test = csv_utils.create_record_model(model_name = 'TestRecord',
                                                     fields=['\tfield_1', 'field_2\n\n'])
        self.assertEqual(Record, to_test)

    def test_csv_to_namedtuples(self):
        csv = test_constants.PARKING_LOTS_TEST_CSV
        fields = ['X','Y','FID','OBJECTID','Spaces','Fee','Comments','Phone','Name','Address',
                  'Neighborho','Maxspaces','Hours','GlobalID','CreationDate','Creator',
                  'EditDate','Editor']
        Record = collections.namedtuple('Record', fields)
        with open(csv, 'r') as csv_file:
            csv_file.readline()        # remove header
            to_test= csv_utils.csv_to_namedtuples(Record, csv_file)
        self.assertIsInstance(collections.namedtuple, to_test[0])

    def test_csv_to_namedtuples_address_field_not_null(self):
        csv = test_constants.PARKING_LOTS_TEST_CSV
        fields = ['X','Y','FID','OBJECTID','Spaces','Fee','Comments','Phone','Name','Address',
                  'Neighborho','Maxspaces','Hours','GlobalID','CreationDate','Creator',
                  'EditDate','Editor']
        Record = collections.namedtuple('Record', fields)
        with open(csv, 'r') as csv_file:
            csv_file.readline()        # remove header
            csv_reader = csv.reader(csv_file, delimiter = ",")
            records = csv_utils.csv_to_namedtuples(Record, csv_reader)
        record_to_test = records[0]
        self.assertIsNotNone(record_to_test.Address)

    def test_add_city_and_state_to_records(self):
        Record = collections.namedtuple('Record', ['test_field', 'Address'])
        records = []
        records.append(Record(test_field='wes', Address = '1000 Dorchester Ave'))
        records.append(Record(test_field='drew', Address = '123 Fake St'))
        to_test = csv_utils.add_city_and_state_to_records(records, 'Boston', 'MA')
        for record in to_test:
            self.assertIn("Boston, MA", record.Address)

    def test_map_addresses_to_record(self):
        Record = collections.namedtuple('Record', ['test_field', 'Address'])
        records = []
        records.append(Record._make('wes', '1000 Dorchester Ave'))
        records.append(Record._make('drew', '123 Fake St'))
        to_test = csv_utils.map_addresses_to_records(records)
        self.assertEqual(records[0].Address, to_test['1000 Dorchester Ave'])


