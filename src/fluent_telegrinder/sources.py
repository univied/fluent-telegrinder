from nodnod import scalar_node
from telegrinder.node import UserSource

from fluent_telegrinder.i18n import FluentTranslator


@scalar_node
class DefaultLocaleSource:
    @classmethod
    async def compose(cls) -> str:
        return FluentTranslator.config.default_locale


@scalar_node
class UserLanguageSource:
    @classmethod
    async def compose(cls, user: UserSource) -> str:
        return (
            user.language_code
            .unwrap_or(FluentTranslator.config.default_locale)
        )
