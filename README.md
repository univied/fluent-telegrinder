<div align="center">

<img src='https://github.com/Tarikul-Islam-Anik/Telegram-Animated-Emojis/blob/main/Animals%20and%20Nature/Owl.webp?raw=true' width='75' style='vertical-align:middle'>

# Fluent Telegrinder
[Fluent](https://projectfluent.org) i18n implementation for telegrinder

<p>
    <img alt="uv" src="https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fastral-sh%2Fuv%2Fmain%2Fassets%2Fbadge%2Fv0.json&style=flat-square&labelColor=232226&color=6341AC&link=https%3A%2F%2Fastral.sh%2Fuv">
    <img alt="Ruff" src="https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fastral-sh%2Fruff%2Fmain%2Fassets%2Fbadge%2Fv2.json&style=flat-square&labelColor=232226&color=6341AC&link=https%3A%2F%2Fastral.sh%2Fruff">
    <a href="https://github.com/univied/fluent-telegrinder/blob/master/pyproject.toml"><img alt="Python versions" src="https://img.shields.io/python/required-version-toml?tomlFilePath=https://raw.githubusercontent.com/univied/fluent-telegrinder/refs/heads/main/pyproject.toml&style=flat-square&logo=python&logoColor=fff&labelColor=black"></img></a>
    <a href="https://github.com/univied/fluent-telegrinder/blob/master/pyproject.toml">
    <img alt="Project version" src="https://img.shields.io/badge/version-v1.1.0-black?style=flat-square&logo=python&logoColor=fff"></img></a>
</p>

</div>

<h2><img src='https://github.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/blob/master/Emojis/Objects/Pencil.png?raw=true' width='20' style='vertical-align:middle'> Usage</h2>

```shell
pip install fluent-telegrinder
```

### CLI

```shell
# Pre-compile .ftl files into .ftlc (pickled AST) for faster startup:
ftg compile locales/

# Write compiled files to a separate directory:
ftg compile locales/ --output locales_compiled/

# Force overwrite existing .ftlc files:
ftg compile locales/ --force
```

Then enable compiled loading in your config:

```python
config = FluentConfig(
    folder="locales/",
    source=DefaultLocaleSource,
    use_compiled=True,  # loads .ftlc files, falls back to .ftl if absent
)
```

```python
from telegrinder import API, Message, Telegrinder, Token

from fluent_telegrinder import (
    DefaultLocaleSource,  # / UserLanguageSource 
    FluentConfig,
    Translator,
    TextEquals,
)

config = FluentConfig(
    folder="locales/",
    source=DefaultLocaleSource, # any node that returns str - source for locale
    default_locale="ru",
    replace_underscore=True, # i_love_telegrinder -> i-love-telegrinder
)
Translator.configure(config)

bot = Telegrinder(API(Token.from_env()))

@bot.on.message(TextEquals("hello", ignore_case=True)) # hello - i18n key (hello, привет)
async def on_hello(msg: Message, _: Translator):
    await msg.reply(_.hello_answer(user=msg.from_user.first_name))

bot.run_forever(skip_updates=True)
```

<h2><img src='https://github.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/blob/master/Emojis/Objects/Notebook.png?raw=true' width='20' style='vertical-align:middle'> License</h2>

Fluent Telegrinder is [MIT licensed](https://github.com/univied/fluent-telegrinder/blob/main/LICENSE).
