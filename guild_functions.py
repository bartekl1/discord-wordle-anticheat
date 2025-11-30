from sqlalchemy import select

import database
from models import Guild

async def get_guild(guild_id: int) -> Guild:
    async with database.get_session() as session:
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

async def get_guild_settings(guild_id: int) -> dict:
    guild = await get_guild(guild_id)
    return {
        "anticheat": guild.enabled,
        "replace_diacritics": guild.replace_diacritics,
        "remove_not_letters": guild.remove_not_letters,
        "reversed_detection": guild.reversed_detection,
        "send_messages": guild.send_messages,
        "delete_wordle_messages": guild.delete_wordle_messages,
    }

async def change_guild_settings(guild_id: int, settings: dict) -> None:
    async with database.get_session() as session:
        result = await session.execute(
            select(Guild).where(Guild.discord_id == guild_id)
        )
        guild_db = result.scalars().first()
        if guild_db:
            for key, value in settings.items():
                if key == "anticheat":
                    key = "enabled"
                if hasattr(guild_db, key):
                    setattr(guild_db, key, value)
            await session.commit()
