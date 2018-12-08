"""
Functions for voting information including polling location information
"""

from . import intent_constants
from mycity.mycity_response_data_model import MyCityResponseDataModel
import mycity.utilities.arcgis_utils as arcgis_utils
import requests
import logging

logger = logging.getLogger(__name__)

