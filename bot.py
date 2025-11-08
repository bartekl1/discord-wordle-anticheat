import discord
from discord import app_commands
import yaml
import requests
import datetime
import asyncio

import database
from models import Guild
from sqlalchemy import select, update


CONFIG_PATH = "config.yaml"

async def get_guild(guild_id: int) -> Guild:
    async with database.AsyncSessionLocal() as session:
        result = await session.execute(
            select(Guild).where(Guild.discord_id == guild_id)
        )
        guild = result.scalars().first()
        if not guild:
            guild = Guild(discord_id=guild_id)
            session.add(guild)
            await session.commit()
            await session.refresh(guild)
        return guild

async def change_enabled(guild: Guild, enabled: bool):
    async with database.AsyncSessionLocal() as session:
        result = await session.execute(
            select(Guild).where(Guild.id == guild.id)
        )
        guild_db = result.scalars().first()
        if guild_db:
            guild_db.enabled = enabled
            await session.commit()


def fetch_answer_from_api() -> dict:
    today_date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    r = requests.get(f"https://www.nytimes.com/svc/wordle/v2/{today_date_str}.json")
    print("Request done")
    if r.status_code == 200:
        return r.json()
    raise Exception("Failed to fetch Wordle answer from API")

def get_today_answer(answer_cache) -> str:
    if answer_cache["date"] == datetime.date.today():
        return answer_cache["word"]
    word = fetch_answer_from_api().get("solution", "").lower()
    answer_cache["word"] = word
    answer_cache["date"] = datetime.date.today()
    return word

def load_config() -> dict:
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f) or {}

class Client(discord.Client):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.answer_cache = {"word": None, "date": None}

    async def on_ready(self):
        await self.wait_until_ready()
        await self.tree.sync()
        print(f"{self.user} has connected to Discord!")

client = Client()

@client.tree.command(name="enable", description="Enable Wordle anti-cheat")
async def enable_anticheat(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    if not interaction.user.guild_permissions.administrator:
        await interaction.followup.send("Only for administrators!")
        return
    guild = await get_guild(interaction.guild.id)
    if guild.enabled:
        await interaction.followup.send("Wordle anti-cheat is already enabled in this server.")
        return
    await change_enabled(guild, True)
    await interaction.followup.send("Wordle anti-cheat successfully enabled.")

@client.tree.command(name="disable", description="Disable Wordle anti-cheat")
async def disable_anticheat(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    if not interaction.user.guild_permissions.administrator:
        await interaction.followup.send("Only for administrators!")
        return
    guild = await get_guild(interaction.guild.id)
    if not guild.enabled:
        await interaction.followup.send("Wordle anti-cheat is already disabled in this server.")
        return
    await change_enabled(guild, False)
    await interaction.followup.send("Wordle anti-cheat successfully disabled.")

@client.tree.command(name="status", description="Get status of Wordle anti-cheat")
async def anticheat_status(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    guild = await get_guild(interaction.guild.id)
    message = f"Wordle anti-cheat is currently **{'enabled' if guild.enabled else 'disabled'}** in this server.\n"
    message += f"Use `{'/enable' if not guild.enabled else '/disable'}` to {'enable' if not guild.enabled else 'disable'} it."
    await interaction.followup.send(message)
    # await interaction.followup.send("Not implemented yet.")

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return
    guild = await get_guild(message.guild.id)
    if not guild.enabled:
        return
    if get_today_answer(client.answer_cache) in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention}, your message has been deleted because it contained today's Wordle answer.", silent=True)

def main():
    config = load_config()
    asyncio.run(database.init_db(config.get("database_url", "sqlite+aiosqlite:///./wordle_anticheat.db")))
    client.run(config.get("bot_token"))

if __name__ == "__main__":
    main()
