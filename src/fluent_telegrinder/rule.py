from telegrinder import ABCRule
from telegrinder.node import Text
from telegrinder.rules import HasText

from .i18n import Translator


class TextEquals(ABCRule, requires=[HasText()]):
    def __init__(self, key: str, ignore_case: bool = False) -> None:
        self.key = key
        self.ignore_case = ignore_case

    async def check(self, _text: Text, _: Translator) -> bool:
        text = _text.lower() if self.ignore_case else _text
        _msg = getattr(_, self.key)()
        msg = _msg.lower() if self.ignore_case else _msg
        return text == msg
