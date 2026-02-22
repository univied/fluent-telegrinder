"""[Fluent](https://projectfluent.org) i18n implementation for telegrinder"""

from .config import FluentConfig
from .i18n import Translator
from .rule import TextEquals
from .sources import DefaultLocaleSource, UserLanguageSource
