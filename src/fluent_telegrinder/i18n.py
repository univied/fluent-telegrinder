import typing

from telegrinder.node import ABCTranslator, Locale, Node

from fluent_telegrinder.config import FluentConfig

_NODE_CACHES: typing.Final = (
    "__dependencies__",
    "__injections__",
    "__compose_names_by_type__",
    "__initialize__",
)
_NOT_CONFIGURED: typing.Final = (
    "Translator is not configured: call `Translator.configure(config)` "
    "or use `Translator[config]` before resolving it as a node."
)


def _rewire(node: type[Node], config: FluentConfig, /) -> None:
    """Point the inherited ``ABCTranslator.__compose__`` at
    ``config.source`` instead of telegrinder's built-in ``Locale`` node.

    Upstream declares ``__compose__(locale: Locale, separator:
    KeySeparator)``, so the locale node cannot be swapped by overriding a
    method -- nodnod reads the dependency straight off the annotation.
    ``__map__`` is the supported substitution hook for exactly this (see
    ``telegrinder.node.nodes.file``); it is consulted while the node graph
    is built, so the caches below must be dropped to force a rebuild.
    """
    node.__map__ = {Locale: config.source}
    for cache in _NODE_CACHES:
        setattr(node, cache, None)
    node.__init_subclass__()


class Translator(ABCTranslator):
    config: typing.ClassVar[FluentConfig]

    def __class_getitem__(cls, config: FluentConfig, /) -> typing.Any:
        subclass = type(
            cls.__name__,
            (cls,),
            {"config": config, "__module__": cls.__module__},
        )
        _rewire(subclass, config)

        # `DefaultLocaleSource` / `UserLanguageSource` and handlers
        # annotated with the plain `Translator` read the config off this
        # class, so keep it usable instead of failing on an unset ClassVar.
        if "config" not in vars(Translator):
            Translator.configure(config)

        return subclass

    @classmethod
    def configure(cls, config: FluentConfig, /) -> None:
        cls.config = config
        _rewire(cls, config)

    def __getattr__(self, key: str) -> typing.Self:
        # An unset `config` ClassVar would otherwise fall through to
        # `ABCTranslator.__getattr__`, which returns `self` and turns the
        # next attribute access into unbounded recursion.
        if key == "config":
            raise RuntimeError(_NOT_CONFIGURED)
        return super().__getattr__(key)

    @property
    def message_id(self) -> str:
        if self.config.replace_underscore:
            return self.separator.join(
                "-".join(key.split("_")) for key in self._keys
            )
        return self.separator.join(self._keys)

    def translate(self, message_id: str, **context: typing.Any) -> str:
        return (
            self.config.get_translator(self.locale).format_value(
                message_id,
                context,
            )
            or message_id
        )
