import os
from typing import Optional
import json

from aiofiles import open as async_open
import orjson
from discord import Locale

from sys import path
path.append("..")
from config import data


class I18n:
    __slots__ = ("path_to_langs", "path_to_translations", "langs", "translations", "guild_id", "cog_name", "command_name", "accepted_langs", "default_lang")

    def __init__(self, default_lang) -> None:
        self.path_to_langs = "./i18n/langs.json"
        self.path_to_translations = "./config/translations/"
        self.translations = {}

        self.guild_id = None
        self.cog_name = None
        self.command_name = None

        self.accepted_langs = {
            "pt": ("portuguese", "português", "portugues"),
            "en": ("english", "inglês", "ingles")
        }
        self.default_lang = default_lang

        #load the file that contains the guilds and their languages
        with open(self.path_to_langs, "r") as f:
            self.langs = orjson.loads(f.read())
            

        #load all translations
        for dir_name in [dir for dir in os.listdir(self.path_to_translations)]:
            if dir_name not in self.accepted_langs:
                continue
            for file_name in [file for file in os.listdir(os.path.join(self.path_to_translations, dir_name)) if file.endswith('.json')]:
                with open(os.path.join(self.path_to_translations, dir_name, file_name)) as json_file:
                    self.translations[dir_name + "." + file_name[:-5]] = orjson.loads(json_file.read())


    def check_lang(self, lang: str) -> bool:
        return lang in self.accepted_langs or any(lang in sublist for sublist in self.accepted_langs.values())

    def t(self, mode: str, *args, mcommand_name: Optional[str] = None, mcog_name: Optional[str] = None, ctx = None, **kwargs) -> str:
        """Searches in the translations for the correct translation

        Args:
            mode (str): The mode (most commun are "cmd" and "err" but it can be anything)
            mcommand_name (str | None, optional): Manually define the command name to use a translation from another command. Defaults to None.
            mcog_name (str | None, optional): Manually define the cog name to use translations of another cog. Defaults to None.
            ctx (commands.Context): The context of the command, used to get the guild id, command name and cog name when the global check doesn't work. Mostly used for app_commands.

        Returns:
            str: The translated string
        """
        if ctx:
            self.guild_id = ctx.guild.id
            self.cog_name = ctx.command.cog_name
            self.command_name = ctx.command.name
        return self.get_key_string(
            self.get_lang(self.guild_id),
            self.cog_name,
            mode,
            mcommand_name, # if needed to use another command's text Manually change the command name
            mcog_name, # if needed to use another cog's text Manually change the cog name
            *args
        ).format(**kwargs)

    async def reload_translations(self) -> None:
        for dir_name in [dir for dir in os.listdir(self.path_to_translations)]:
            if dir_name not in self.accepted_langs:
                continue
            for file_name in [file for file in os.listdir(os.path.join(self.path_to_translations, dir_name)) if file.endswith('.json')]:
                async with async_open(os.path.join(self.path_to_translations, dir_name, file_name), mode="r") as f:
                    self.translations[dir_name + "." + file_name[:-5]] = orjson.loads(await f.read())


    def get_key_string(self, lang: str, cog: str, mode: str, mcommand_name: Optional[str] = None, mcog_name: Optional[str] = None, *args) -> str:
        command_name = mcommand_name or self.command_name
        cog_name = mcog_name or self.cog_name
        try:
            translated_string = self.get_keys_string(lang, cog_name)[command_name][mode]
            return translated_string["-".join(args)] if args else translated_string
        except KeyError:
            # if not implemented in the language, return the default language version
            translated_string = self.get_keys_string(self.default_lang, cog)[self.command_name][mode]
            return translated_string["-".join(args)] if args else translated_string

    def get_keys_string(self, lang: str, cog: str) -> dict:
        return self.translations[lang + "." + cog]

    def get_lang(self, guild_id: int) -> str:
        return self.langs[str(guild_id)]
    

    def get_command_name(self, command_name: str, cog: str, lang: str) -> str:
        return self.get_keys_string(lang, cog)[command_name]["command_name"]

    def get_command_description(self, command_description: str, cog: str, lang: str) -> str:
        return self.get_keys_string(lang, cog)[command_description]["command_description"]

    def get_group_name(self, group_name: str, cog: str, lang: str) -> str:
        return self.get_keys_string(lang, cog)[group_name]["group_name"]

    def get_group_description(self, group_description: str, cog: str, lang: str) -> str:
        return self.get_keys_string(lang, cog)[group_description]["group_description"]


    def get_locale_lang(self, locale: str) -> str | Locale:
        """Helper function to get the proper Locale from a string E.g. "pt" -> Locale.brazil_portuguese

        Args:
            locale (str): The string

        Returns:
            str | Locale: Return the proper Locale
        """
        if locale == "pt":
            return Locale.brazil_portuguese
        
        if locale == "en":
            return Locale.american_english

        return None






    async def update_langs(self, guild_id: int, lang: str) -> None:
        try:
            if self.langs[str(guild_id)] == lang:
                raise ValueError("The language is the same as the current one")
        except KeyError:
            pass

        self.langs[str(guild_id)] = lang
        async with async_open("./i18n/langs.json", "w") as f:
            await f.write(json.dumps(self.langs, indent=4))


    async def delete_lang(self, guild_id: int) -> None:
        self.langs.pop(str(guild_id))
        async with async_open("./i18n/langs.json", "w") as f:
            await f.write(json.dumps(self.langs, indent=4))



i18n = I18n(data["default_language"])