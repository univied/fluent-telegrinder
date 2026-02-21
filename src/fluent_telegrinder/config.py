import pickle
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from fluent.runtime import (
    FluentBundle,
    FluentLocalization,
    FluentResourceLoader,
)
from telegrinder.node import Node


@runtime_checkable
class _Translator(Protocol):
    """Minimal interface shared by FluentLocalization and
    _CompiledLocalization."""

    def format_value(
        self,
        message_id: str,
        args: dict[str, Any] | None = None,
    ) -> str | None: ...


class _CompiledLocalization:
    """Wraps a *pre-built* FluentBundle loaded from pickled .ftlc files.

    Exposes the same ``format_value`` interface as ``FluentLocalization`` so
    that ``FluentConfig.get_translator`` can return either type transparently.

    How the speed-up works
    ~~~~~~~~~~~~~~~~~~~~~~
    ``FluentLocalization`` lazily opens .ftl files and hands the raw text to
    ``FluentBundle``, which calls ``fluent.syntax.FluentParser.parse()`` for
    every resource at first use.  By pre-parsing and pickling the resulting
    ``fluent.syntax.ast.Resource`` objects (via
    ``fluent-telegrinder compile``), we load the already-parsed AST directly,
    skipping the text-parsing step.
    The internal ``Compiler`` (``fluent.runtime.prepare``) still runs once per
    bundle to turn AST nodes into resolver callables — that part cannot be
    cached across processes — but it is already very fast.

    Bottom line: this removes FTL text-parsing overhead from startup time.
    Per-message ``format_value`` speed is identical to the normal path.
    """

    def __init__(self, bundle: FluentBundle) -> None:
        self._bundle = bundle

    def format_value(
        self,
        message_id: str,
        args: dict[str, Any] | None = None,
    ) -> str | None:
        if not self._bundle.has_message(message_id):
            return None
        message = self._bundle.get_message(message_id)
        if message.value is None:
            return None
        value, _errors = self._bundle.format_pattern(message.value, args)
        return value


@dataclass
class FluentConfig:
    folder: Path | str
    source: Node
    default_locale: str = "en"
    replace_underscore: bool = True
    functions: dict[str, Callable] = field(default_factory=dict)
    use_compiled: bool = False
    """When *True*, load pre-compiled .ftlc files (pickled AST) instead of
    parsing .ftl text at runtime.  Run ``fluent-telegrinder compile <folder>``
    first to generate the .ftlc files.  Falls back to .ftl if no .ftlc files
    are found for a locale."""

    def __post_init__(self) -> None:
        if not isinstance(self.folder, Path):
            self.folder = Path(self.folder)

    def _load_compiled(self, locale_dir: Path) -> _CompiledLocalization | None:
        """Build a ``_CompiledLocalization`` from pickled .ftlc files, or
        return *None* if no .ftlc files exist under *locale_dir*."""
        ftlc_files = list(locale_dir.rglob("*.ftlc"))
        if not ftlc_files:
            return None

        bundle = FluentBundle(
            locales=[locale_dir.name],
            functions=self.functions,
        )
        for ftlc_file in ftlc_files:
            with ftlc_file.open("rb") as fh:
                resource = pickle.load(fh)  # noqa: S301
            bundle.add_resource(resource)

        return _CompiledLocalization(bundle)

    @cached_property
    def loaders(self) -> dict[str, _Translator]:
        result: dict[str, _Translator] = {}

        for locale_dir in self.folder.iterdir():  # type: ignore[union-attr]
            if not locale_dir.is_dir():
                continue

            if self.use_compiled:
                compiled = self._load_compiled(locale_dir)
                if compiled is not None:
                    result[locale_dir.name] = compiled
                    continue

            ftl_files = [
                str(p.relative_to(locale_dir))
                for p in locale_dir.rglob("*.ftl")
            ]
            if not ftl_files:
                continue

            loader = FluentResourceLoader(str(self.folder / "{locale}"))  # type: ignore[arg-type]
            localization = FluentLocalization(
                locales=[locale_dir.name],
                resource_ids=ftl_files,
                resource_loader=loader,
                functions=self.functions,
            )

            result[locale_dir.name] = localization

        return result

    def get_translator(self, locale: str) -> _Translator:
        return self.loaders.get(locale, self.loaders[self.default_locale])
