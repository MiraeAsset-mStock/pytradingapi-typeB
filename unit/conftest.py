import os
import sys
import pytest

parent_dir=os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from tradingapi_b.mconnect import *
from tradingapi_b import __config__

@pytest.fixture()
def mconnect():
    '''Initialize MConnect Object'''
    mconnectB=MConnectB(api_key=__config__.API_KEY,access_Token="<ACCESS_TOKEN>")
    return mconnectB


