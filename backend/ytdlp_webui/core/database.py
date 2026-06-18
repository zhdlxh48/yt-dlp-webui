from __future__ import annotations

from pathlib import Path

from sqlalchemy import Boolean, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from ytdlp_webui.core.schemas import LiveChannel


class Base(DeclarativeBase):
    pass


class DbLiveChannel(Base):
    __tablename__ = "live_channels"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, default="")
    handle: Mapped[str] = mapped_column(String, default="")
    url: Mapped[str] = mapped_column(String, default="")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class Database:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(f"sqlite:///{db_path}")
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self._init_db()

    def _init_db(self) -> None:
        Base.metadata.create_all(bind=self.engine)

    def get_channels(self) -> list[LiveChannel]:
        with self.SessionLocal() as session:
            db_channels = session.query(DbLiveChannel).all()
            return [
                LiveChannel(
                    id=ch.id,
                    name=ch.name,
                    handle=ch.handle,
                    url=ch.url,
                    enabled=ch.enabled,
                )
                for ch in db_channels
            ]

    def save_channels(self, channels: list[LiveChannel]) -> None:
        with self.SessionLocal() as session:
            session.query(DbLiveChannel).delete()
            db_channels = [
                DbLiveChannel(
                    id=ch.id,
                    name=ch.name,
                    handle=ch.handle,
                    url=ch.url,
                    enabled=ch.enabled,
                )
                for ch in channels
            ]
            session.add_all(db_channels)
            session.commit()
