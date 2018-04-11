""" Custom error types for My City app"""


class InvalidAddressError(Exception):
    """Error raised for issues with provided address"""
    pass


class BadAPIResponse(Exception):
    """Error for bad responses from external APIs"""
    pass
