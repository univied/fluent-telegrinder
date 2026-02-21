from nodnod import scalar_node
from telegrinder.node import UserSource

from fluent_telegrinder.i18n import Translator


@scalar_node
class DefaultLocaleSource:
    @classmethod
    async def compose(cls) -> str:
        return Translator.config.default_locale


@scalar_node
class UserLanguageSource:
    @classmethod
    async def compose(cls, user: UserSource) -> str:
        return user.language_code.unwrap_or(Translator.config.default_locale)
