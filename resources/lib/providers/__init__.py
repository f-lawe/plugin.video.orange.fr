# -*- coding: utf-8 -*-
"""List all available providers and return the provider selected by the user"""
from .provider_interface import ProviderInterface
from .fr import OrangeFranceProvider

PROVIDERS = {
    'France.Orange': OrangeFranceProvider
}

KEY = 'France.Orange'

Provider = PROVIDERS[KEY]
