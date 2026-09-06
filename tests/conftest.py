import os
from pathlib import Path

import pytest

os.environ.setdefault("LLM_PROVIDER", "stub")


@pytest.fixture
def tmp_db(tmp_path: Path):
    """A fresh SQLite database for one test."""
    from unbilled import config

    path = tmp_path / "test.db"
    conn = config.get_conn(path)
    try:
        yield conn, path
    finally:
        conn.close()


@pytest.fixture
def fixtures_dir() -> Path:
    from unbilled import config

    return config.FIXTURES_DIR
