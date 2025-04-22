"""
This file contains classes for making cached calls to EZ Office API endpoints.
The parent class EzoCache contains basic caching functionality.
Child classes extend EzoCache and add endpoint specific methods.
"""

from pprint import pprint
import pickle

import ezoff
from .exceptions import *
from .data_model import *
