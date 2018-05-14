"""
Utility functions for manipulating csv files

"""
import collections


def create_record_model(model_name, attributes):
    """
    Spin up a namedtuple class to represent a record from a csv 
    file

    :param model_name: a string representing whatever we want to call
        this class
    :param attributes: a list of strings representing the attributes
        of this container
    :return: a constructor for this namedtuple subclass
    """
    Model = collections.namedtuple(model_name, attributes)
    return Model
                                   

def csv_to_namedtuples(Model, csv_reader):
    """
    Create and return a list of namedtuples representing all records from the 
    csv.
    
    :param Model: namedtuple subclass to convert each line in csv
        file to
    :param csv_reader: csv reader object
    :return: a list of namedtuples representing all csv records
    """
    records = []
    for line in csv_reader:
        records.append(Model._make(line))
    return records


def add_city_and_state_to_records(records, address_key, 
                                  city, state):
    """
    Append '{city}, {state}' to the Address fields of each record 
    in records.

    :param records: filtered CSV.DictReader
    :param address_key: key to access address field in a record
    :param city: name of city stored as a string
    :param state: name of state stored as a string
    :return: a copy of records with Address fields modified
    """
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

    :param records: a list of namedtuples representing records 
        from a csv file
    :return: dictionary mapping an string Address to namedtuple record
    """
    return {getattr(record, attribute) : record for record in records}
