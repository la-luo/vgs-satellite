import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, String

from satellite.aliases import AliasGeneratorType

from .base import Base


class Alias(Base):
    __tablename__ = 'aliases'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=lambda: datetime.utcnow())
    value = Column(String)
    alias_generator = Column(Enum(AliasGeneratorType, create_constraint=False))
    public_alias = Column(String)
    expires_at = Column(DateTime)
