from nodnod import scalar_node
from telegrinder.node import UserSource

from telefluent.i18n import Translator


@scalar_node
class DefaultLocaleSource:
    @classmethod
    async def __compose__(cls) -> str:
        return Translator.config.default_locale


@scalar_node
class UserLanguageSource:
    @classmethod
    async def __compose__(cls, user: UserSource) -> str:
        return user.language_code.unwrap_or(Translator.config.default_locale)
