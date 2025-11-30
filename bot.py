import discord
from discord import app_commands
from unidecode import unidecode
import yaml
import asyncio
import re

import database
from wordle_api import update_answer_cache
from guild_functions import get_guild_settings, change_guild_settings
from strings import STRINGS

from __version__ import __version__

CONFIG_PATH = "config.yaml"
WORDLE_BOT_ID = 1211781489931452447

def load_config() -> dict:
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f) or {}

class Client(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.all()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.answer_cache = (None, None)

    async def on_ready(self) -> None:
        await self.wait_until_ready()
        await self.tree.sync()
        print(f"{self.user} has connected to Discord!")

class SettingsEmbed(discord.Embed):
    def __init__(self, settings: dict) -> None:
        super().__init__(title=STRINGS["en"]["settings"]["title"], color=0x0000dd)

        for key, value in settings.items():
            self.add_field(
                name=STRINGS["en"]["settings"]["setting_names"][key],
                value=":white_check_mark: " + STRINGS["en"]["settings"]["enabled"] if value else ":negative_squared_cross_mark: " + STRINGS["en"]["settings"]["disabled"],
                inline=False
            )

class SettingsButtonsView(discord.ui.View):
    def __init__(self, settings: dict, timeout: int = 180) -> None:
        super().__init__(timeout=timeout)

        self.buttons = {}
        for key, value in settings.items():
            self.buttons[key] = discord.ui.Button(
                label=(STRINGS["en"]["settings"]["disable"] if value else STRINGS["en"]["settings"]["enable"]) \
                      + " " + STRINGS["en"]["settings"]["toggle_setting_names"][key],
                style=discord.ButtonStyle.red if value else discord.ButtonStyle.green,
                disabled=not settings["anticheat"] and key != "anticheat"
            )
            self.buttons[key].callback = lambda interaction, key=key, value=not value: self.toggle_setting(interaction, key, value)
            self.add_item(self.buttons[key])

    async def toggle_setting(self, interaction: discord.Interaction, setting_key: str, new_value: bool) -> None:
        if not interaction.user.guild_permissions.administrator:
            return
        await change_guild_settings(interaction.guild.id, {setting_key: new_value})
        new_settings = await get_guild_settings(interaction.guild.id)
        embed = SettingsEmbed(settings=new_settings)
        view = SettingsButtonsView(settings=new_settings)
        await interaction.response.edit_message(embed=embed, view=view)

client = Client()

@client.tree.command(name="about", description="About the bot")
async def about_bot(interaction: discord.Interaction) -> None:
    await interaction.response.defer(ephemeral=True)
    embed = discord.Embed(
        title=STRINGS["en"]["about"]["title"],
        description=STRINGS["en"]["about"]["description"],
        color=0x0000dd
    )
    embed.add_field(name=STRINGS["en"]["about"]["version"], value=f"`{__version__}`", inline=False)
    embed.add_field(name=STRINGS["en"]["about"]["source_code"], value=f"[{STRINGS['en']['about']['github_repository']}]({STRINGS['github_repository_url']})", inline=False)
    embed.add_field(name=STRINGS["en"]["about"]["license"], value="GNU Affero General Public License v3.0", inline=False)
    await interaction.followup.send(embed=embed)

@client.tree.command(name="settings", description="Bot settings for this server")
async def bot_settings(interaction: discord.Interaction) -> None:
    await interaction.response.defer(ephemeral=True)
    current_settings = await get_guild_settings(interaction.guild.id)
    embed = SettingsEmbed(settings=current_settings)
    if interaction.user.guild_permissions.administrator:
        view = SettingsButtonsView(settings=current_settings)
    else:
        view = discord.ui.View()
        embed.set_footer(text=STRINGS["en"]["settings_only_admin"])
    await interaction.followup.send(embed=embed, view=view)

@client.event
async def on_message(message: discord.Message) -> None:
    if message.author == client.user:
        return
    
    guild = await get_guild_settings(message.guild.id)
    if not guild["anticheat"]:
        return
    
    if message.author.id == WORDLE_BOT_ID and guild["delete_wordle_messages"]:
        if not message.content.startswith("**Y"): await message.delete()
        return
    
    client.answer_cache = await update_answer_cache(client.answer_cache)
    
    message_text = message.content.lower()
    message_text = unidecode(message_text) if guild["replace_diacritics"] else message_text
    message_text = re.sub(r"[^A-Za-z]", "", message_text).lower() if guild["remove_not_letters"] else message_text

    if client.answer_cache[1] in message_text or \
       (client.answer_cache[1][::-1] in message_text and guild["reversed_detection"]):
        await message.delete()
        if guild["send_messages"]:
            await message.channel.send(f":warning: {message.author.mention}, {STRINGS['en']['message_deleted']}", silent=True)

def main() -> None:
    config = load_config()
    asyncio.run(database.init_db(config.get("database_url", "sqlite+aiosqlite:///./wordle_anticheat.db")))
    client.run(config.get("bot_token"))

if __name__ == "__main__":
    main()
