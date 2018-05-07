"""
Utility functions for manipulating csv files

"""
import collections


def create_record_model(model_name='Record', fields=[]):
    """
    Spin up a namedtuple class to represent a record from a csv 
    file

    :param: model_name: a string represent whatever we want to call
    this class

    :param: fields: a list of strings representing the attributes
    of this container

    :ret: a constructor for this namedtuple subclass
    """
    attributes = [field.strip() for field in fields] # remove newline/tabs 
    Model = collections.namedtuple(model_name, attributes)
    return Model
                                   

def csv_to_namedtuples(Model, csv):
    """
    Return a list of namedtuples representing a record from the 
    csv. Records fields in fields to select.
    
    :param: Model: namedtuple subclass to convert each line in csv
    file to
    :param: csv: csv file
    :param: fields_to_select: list of strings to select. If None,
      all fields are selected 

    :return: records: a list of namedtuples representing
   
    """
    records = []
    for line in csv:
        print(line)
        records.append(Model._make(line))
    return records


def add_city_and_state_to_records(records, city, state):
    """
    Append '{city}, {state}' to the Address fields of each record 
    in records.

    :param: records: a list of namedtuples created from a 
    csv file

    :ret: a copy of records with Address fields modified
    """
    suffix = " " + city + ", " + state
    return [record._replace(Address = record.Address + suffix) for record in records]


def map_addresses_to_records(records):
    """
    Create and return a dictionary mapping a records address field
    to the record itself. This allows us to access the whole record
    once we know the closest address to some origin

    :param: records: a list of namedtuples representing records 
    from a csv file

    :ret: dictionary mapping an string Address to namedtuple record

    """
    return {record.Address : record for record in records}
    
