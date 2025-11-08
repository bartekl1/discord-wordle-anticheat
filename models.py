from sqlalchemy import Column, Integer, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Guild(Base):
    __tablename__ = "guilds"

    id = Column(Integer, primary_key=True)
    discord_id = Column(Integer, unique=True, nullable=False)
    enabled = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<Guild id={self.id} discord_id={self.discord_id} enabled={self.enabled}>"
