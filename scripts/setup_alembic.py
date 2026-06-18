import os
import subprocess
import sys
from pathlib import Path

ENV_TEMPLATE = """import logging
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from ytdlp_webui.core.database import Base
target_metadata = Base.metadata

from ytdlp_webui.core.paths import AppPaths
db_file = AppPaths.discover().db_file
config.set_main_option("sqlalchemy.url", f"sqlite:///{{db_file}}")


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
"""


def main():
    root = Path(__file__).resolve().parents[1]
    migrations_dir = root / "migrations"
    env_py = migrations_dir / "env.py"

    if not migrations_dir.exists():
        print("Initializing Alembic migrations directory...")
        # Run alembic init
        alembic_exe = root / ".venv" / "Scripts" / "alembic"
        if not alembic_exe.exists():
            alembic_exe = "alembic"

        try:
            subprocess.run([str(alembic_exe), "init", "migrations"], cwd=root, check=True)
        except Exception as e:
            print(f"Error initializing alembic: {e}")
            sys.exit(1)
    else:
        print("migrations/ directory already exists.")

    print("Configuring migrations/env.py...")
    try:
        env_py.write_text(ENV_TEMPLATE, encoding="utf-8")
        print("migrations/env.py successfully configured!")
    except Exception as e:
        print(f"Error writing migrations/env.py: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
