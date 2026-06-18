from __future__ import annotations

from pathlib import Path

from ytdlp_webui.core.database import Database
from ytdlp_webui.core.schemas import LiveChannel


def test_database_initialization_and_operations(tmp_path: Path) -> None:
    db_file = tmp_path / "test.db"
    db = Database(db_file)

    # Database file should be created
    assert db_file.exists()

    # Initial channels list should be empty
    assert len(db.get_channels()) == 0

    # Save channels
    channels = [
        LiveChannel(
            id="ch1",
            name="Chan 1",
            handle="@chan1",
            url="https://www.youtube.com/@chan1/live",
            enabled=True,
        ),
        LiveChannel(
            id="ch2",
            name="Chan 2",
            handle="@chan2",
            url="https://www.youtube.com/@chan2/live",
            enabled=False,
        ),
    ]
    db.save_channels(channels)

    # Retrieve and verify
    retrieved = db.get_channels()
    assert len(retrieved) == 2
    assert retrieved[0].id == "ch1"
    assert retrieved[0].enabled is True
    assert retrieved[1].id == "ch2"
    assert retrieved[1].enabled is False

    # Modify list (update ch1, delete ch2, add ch3)
    channels_updated = [
        LiveChannel(
            id="ch1",
            name="Chan 1 Updated",
            handle="@chan1",
            url="https://www.youtube.com/@chan1/live",
            enabled=False,
        ),
        LiveChannel(
            id="ch3",
            name="Chan 3",
            handle="@chan3",
            url="https://www.youtube.com/@chan3/live",
            enabled=True,
        ),
    ]
    db.save_channels(channels_updated)

    retrieved_updated = db.get_channels()
    assert len(retrieved_updated) == 2
    assert retrieved_updated[0].id == "ch1"
    assert retrieved_updated[0].name == "Chan 1 Updated"
    assert retrieved_updated[0].enabled is False
    assert retrieved_updated[1].id == "ch3"
    assert retrieved_updated[1].enabled is True
