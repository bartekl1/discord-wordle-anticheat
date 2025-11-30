from sqlalchemy import Column, Integer, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Guild(Base):
    __tablename__ = "guilds"

    id = Column(Integer, primary_key=True)
    discord_id = Column(Integer, unique=True, nullable=False)
    enabled = Column(Boolean, nullable=False, server_default="0")
    replace_diacritics = Column(Boolean, nullable=False, server_default="0")
    remove_not_letters = Column(Boolean, nullable=False, server_default="0")
    reversed_detection = Column(Boolean, nullable=False, server_default="0")
    send_messages = Column(Boolean, nullable=False, server_default="1")
    delete_wordle_messages = Column(Boolean, nullable=False, server_default="0")

    def __repr__(self) -> str:
        return f"<Guild id={self.id} discord_id={self.discord_id} enabled={self.enabled}>"
