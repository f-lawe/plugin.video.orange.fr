# -*- coding: utf-8 -*-
"""List all available providers and return the provider selected by the user"""
from .provider_interface import ProviderInterface

from .fr import OrangeFranceProvider

class _ProviderWrapper: # pylint: disable=too-few-public-methods
    """PROVIDER WRAPPER"""

    def __init__(self):
        self.__provider = OrangeFranceProvider()

    def get_instance(self):
        """GETTER"""
        return self.__provider

_WRAPPER = _ProviderWrapper()

def provider():
    """Return the current provider """
    return _WRAPPER.get_instance()
