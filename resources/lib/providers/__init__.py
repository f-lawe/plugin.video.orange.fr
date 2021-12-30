# -*- coding: utf-8 -*-
"""List all available providers and return the provider selected by the user"""
from lib.utils import get_addon_setting, log, LogLevel

from .provider_interface import ProviderInterface
from .provider_wrapper import ProviderWrapper

from . import fr

_PROVIDERS = {
    'France.Free (beta)': fr.FreeProvider,
    'France.Orange': fr.OrangeFranceProvider,
    'France.Orange Caraïbe': fr.OrangeCaraibeProvider,
    'France.Orange Réunion': fr.OrangeReunionProvider,
    'France.SFR (beta)': fr.SFRProvider
}

name: str = get_addon_setting('provider.name')
country: str = get_addon_setting('provider.country')

_KEY = f'{country}.{name}'

_PROVIDER = _PROVIDERS[_KEY]() if _PROVIDERS.get(_KEY) is not None else None

if not _PROVIDER:
    log(f'Cannot instanciate provider: {_KEY}', LogLevel.ERROR)
else:
    log(f'Using {_KEY}', LogLevel.INFO)

def get_provider() -> ProviderInterface:
    """Return the selected provider"""
    return ProviderWrapper(_PROVIDER)
