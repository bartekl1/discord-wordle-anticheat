import discord
from discord import app_commands
import yaml
import asyncio

import database
from wordle_api import update_answer_cache
from guild_functions import get_guild, change_enabled

CONFIG_PATH = "config.yaml"

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

client = Client()

@client.tree.command(name="enable", description="Enable Wordle anti-cheat")
async def enable_anticheat(interaction: discord.Interaction) -> None:
    await interaction.response.defer(ephemeral=True)
    if not interaction.user.guild_permissions.administrator:
        await interaction.followup.send(":lock: **Access denied!** This command is only for server administrators.")
        return
    guild = await get_guild(interaction.guild.id)
    if guild.enabled:
        await interaction.followup.send(":information_source: Wordle anti-cheat is already **enabled** in this server.")
        return
    await change_enabled(guild, True)
    await interaction.followup.send(":white_check_mark: Wordle anti-cheat **successfully enabled**.")

@client.tree.command(name="disable", description="Disable Wordle anti-cheat")
async def disable_anticheat(interaction: discord.Interaction) -> None:
    await interaction.response.defer(ephemeral=True)
    if not interaction.user.guild_permissions.administrator:
        await interaction.followup.send(":lock: **Access denied!** This command is only for server administrators.")
        return
    guild = await get_guild(interaction.guild.id)
    if not guild.enabled:
        await interaction.followup.send(":information_source: Wordle anti-cheat is already **disabled** in this server.")
        return
    await change_enabled(guild, False)
    await interaction.followup.send(":negative_squared_cross_mark: Wordle anti-cheat **successfully disabled**.")

@client.tree.command(name="status", description="Get status of Wordle anti-cheat")
async def anticheat_status(interaction: discord.Interaction) -> None:
    await interaction.response.defer(ephemeral=True)
    guild = await get_guild(interaction.guild.id)
    message = f"Wordle anti-cheat is currently **{':white_check_mark: enabled' if guild.enabled else ':negative_squared_cross_mark: disabled'}** in this server.\n"
    message += f"Use `{'/enable' if not guild.enabled else '/disable'}` to {'enable' if not guild.enabled else 'disable'} it."
    await interaction.followup.send(message)

@client.event
async def on_message(message: discord.Message) -> None:
    client.answer_cache = await update_answer_cache(client.answer_cache)
    if message.author == client.user:
        return
    guild = await get_guild(message.guild.id)
    if not guild.enabled:
        return
    message_text = re.sub(r"[^A-Za-z]|(regional_indicator_)", "", message.content).lower()
    if client.answer_cache[1] in message_text:
        await message.delete()
        await message.channel.send(f":warning: {message.author.mention}, your message has been deleted because it contained today's Wordle answer.", silent=True)

def main() -> None:
    config = load_config()
    asyncio.run(database.init_db(config.get("database_url", "sqlite+aiosqlite:///./wordle_anticheat.db")))
    client.run(config.get("bot_token"))

if __name__ == "__main__":
    main()
