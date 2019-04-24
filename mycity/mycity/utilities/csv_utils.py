"""
Utility functions for manipulating csv files

"""

import collections
import logging

logger = logging.getLogger(__name__)


def create_record_model(model_name, attributes):
    """
    Spin up a namedtuple class to represent a record from a csv file

    :param model_name: a string representing whatever we want to call
        this class
    :param attributes: a list of strings representing the attributes
        of this container
    :return: a constructor for this namedtuple subclass
    """
    logger.debug(
        'model_name: ' + model_name +
        ', attributes: ' + str(attributes)
    )
    Model = collections.namedtuple(model_name, attributes)
    return Model


def csv_to_namedtuples(model, csv_reader):
    """
    Create and return a list of namedtuples representing all records from the
    csv.

    :param model: namedtuple subclass to convert each line in csv
        file to
    :param csv_reader: csv reader object
    :return: a list of namedtuples representing all csv records
    """
    logger.debug('model: ' + str(model) + ', csv_reader: ' + str(csv_reader))
    records = []
    for line in csv_reader:
        records.append(model._make(line))
    return records


def add_city_and_state_to_records(records, address_key, city, state):
    """
    Append '{city}, {state}' to the Address fields of each record
    in records.

    :param records: filtered CSV.DictReader
    :param address_key: key to access address field in a record
    :param city: name of city stored as a string
    :param state: name of state stored as a string
    :return: a copy of records with Address fields modified
    """
    logger.debug('records: ' + str(records) +
                 ', address_key: ' + str(address_key) +
                 ', city: ' + str(city) +
                 ', state: ' + str(state))
    suffix = " " + city + ", " + state
    ret = []
    for record in records:
        record[address_key] = record[address_key] + suffix
        ret.append(record)
    return ret


def map_attribute_to_records(attribute, records):
    """
    Create and return a dictionary mapping a records address field
    to the record itself. This allows us to access the whole record
    once we know the closest address to some origin

    # TODO: review for deletion - function not used. This logic appears
    to be implemented in "get_closest_record_with_driving_info"
    function in finder.py on Line 193

    :param records: a list of namedtuples representing records
        from a csv file
    :return: dictionary mapping an string Address to namedtuple record
    """
    return {getattr(record, attribute) : record for record in records}
