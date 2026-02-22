import typing

from telegrinder.node import ABCTranslator, KeySeparator, Node

from telefluent.config import FluentConfig


class Translator(ABCTranslator):
    config: typing.ClassVar[FluentConfig]

    def __class_getitem__(cls, config: FluentConfig, /) -> typing.Any:
        return type(cls.__name__, (cls,), {"config": config})

    @classmethod
    def configure(cls, config: FluentConfig, /) -> None:
        cls.config = config

    @property
    def message_id(self) -> str:
        if self.config.replace_underscore:
            return self.separator.join(
                "-".join(key.split("_")) for key in self._keys
            )
        return self.separator.join(self._keys)

    @classmethod
    def get_subnodes(cls) -> dict[str, type[Node]]:
        return {"locale": cls.config.source, "separator": KeySeparator}

    def translate(self, message_id: str, **context: typing.Any) -> str:
        return (
            self.config.get_translator(self.locale).format_value(
                message_id,
                context,
            )
            or message_id
        )
