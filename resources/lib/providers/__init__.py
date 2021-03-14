# -*- coding: utf-8 -*-
"""List all available providers and return the provider selected by the user"""
from .provider_interface import ProviderInterface
from .fr import OrangeFranceProvider

_PROVIDERS = {
    'France.Orange': OrangeFranceProvider
}

_KEY = 'France.Orange'

_PROVIDER = _PROVIDERS[_KEY]()

def get_provider() -> ProviderInterface:
    """Return the selected provider"""
    return _PROVIDER
