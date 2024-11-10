"""Custom exceptions for the unesco_reader package"""

class NoDataError(Exception):
    """This is a custom exception that is raised when no UIS data exists"""

    pass

class TooManyRecordsError(Exception):
    """This is a custom exception that is raised when too many records are requested"""

    pass