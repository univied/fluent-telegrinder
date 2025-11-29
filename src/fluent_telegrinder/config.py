from collections.abc import Callable
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path

from fluent.runtime import (
    FluentLocalization,
    FluentResourceLoader,
)
from telegrinder.node import IsNode


@dataclass
class FluentConfig:
    folder: Path | str
    source: IsNode
    default_locale: str = "en"
    replace_underscore: bool = True
    functions: dict[str, Callable] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.folder, Path):
            self.folder = Path(self.folder)

    @cached_property
    def loaders(self) -> dict[str, FluentLocalization]:
        result: dict[str, FluentLocalization] = {}

        for locale_dir in self.folder.iterdir(): # type: ignore
            if not locale_dir.is_dir():
                continue

            ftl_files = [
                str(p.relative_to(locale_dir))
                for p in locale_dir.rglob("*.ftl")
            ]
            if not ftl_files:
                continue

            loader = FluentResourceLoader(str(self.folder / "{locale}")) # type: ignore
            localization = FluentLocalization(
                locales=[locale_dir.name],
                resource_ids=ftl_files,
                resource_loader=loader,
                functions=self.functions,
            )

            result[locale_dir.name] = localization

        return result

    def get_translator(self, locale: str) -> FluentLocalization:
        return self.loaders.get(locale, self.loaders[self.default_locale])
