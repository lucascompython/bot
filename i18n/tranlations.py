from aiofiles import open as async_open

import os, json


class I18n:
    def __init__(self) -> None:
        self.path_to_langs = "./i18n/langs.json"
        self.path_to_translations = "./config/translations/"
        self.translations = {}

        self.guild_id = None
        self.cog_name = None
        self.command_name = None

        self.accepted_langs = {
            "pt": ["portuguese", "português"],
            "en": ["english", "inglês"]
        }

        #load the file that contains the guilds and their languages
        with open(self.path_to_langs, "r") as f:
            self.langs = json.load(f)
            

        #load all translations
        for file_name in [file for file in os.listdir(self.path_to_translations) if file.endswith('.json')]:
            with open(self.path_to_translations + file_name) as json_file:
                self.translations[file_name[:-5]] = json.load(json_file)

    def check_lang(self, lang: str) -> bool:
        return lang in self.accepted_langs or lang in self.accepted_langs.values()

    def t(self, mode: str,  *args, mcommand_name: str | None = None, mcog_name: str | None = None, **kwargs) -> str:
        """Searches in the translations for the correct translation

        Args:
            mode (str): The mode (most commun are "cmd" and "err" but it can be anything)
            mcommand_name (str | None, optional): Manually define the command name to use a translation from another command. Defaults to None.
            mcog_name (str | None, optional): Manually define the cog name to use translations of another cog. Defaults to None.

        Returns:
            str: The translated string
        """
        return self.get_key_string(
            self.get_lang(self.guild_id),
            self.cog_name,
            mode,
            mcommand_name, # if needed to use another command's text Manually change the command name
            mcog_name, # if needed to use another cog's text Manually change the cog name
            *args
        ).format(**kwargs)

    async def reload_translations(self) -> None:
        for file_name in [file for file in os.listdir(self.path_to_translations) if file.endswith('.json')]:
            async with async_open(self.path_to_translations + file_name) as f:
                contents = await f.read()
            self.translations[file_name[:-5]] = json.loads(contents)


    def get_key_string(self, lang: str, cog: str, mode: str, mcommand_name: str | None = None, mcog_name: str | None = None, *args) -> str:
        command_name = mcommand_name or self.command_name
        cog_name = mcog_name or self.cog_name
        try:
            return self.get_keys_string(lang, cog_name)[command_name][mode]["-".join(args)]
        except KeyError:
            # if not implemented in the language, return the english version
            return self.get_keys_string("en", cog)[self.command_name][mode]["-".join(args)]

    def get_keys_string(self, lang: str, cog: str) -> dict:
        return self.translations[lang + "." + cog]

    def get_lang(self, guild_id: int) -> str:
        return self.langs[str(guild_id)]
    


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