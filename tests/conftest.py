"""Shared fixtures for the new-layer test suite."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLES = REPO_ROOT / "app_files" / "samples"


@pytest.fixture(scope="session")
def samples_dir() -> Path:
    return SAMPLES


@pytest.fixture
def contacts_csv(samples_dir: Path) -> Path:
    return samples_dir / "messy_contacts.csv"


@pytest.fixture
def bank_csv(samples_dir: Path) -> Path:
    return samples_dir / "bank_statement.csv"


@pytest.fixture
def ledger_csv(samples_dir: Path) -> Path:
    return samples_dir / "ledger.csv"


@pytest.fixture
def bank_pdf(samples_dir: Path) -> Path:
    return samples_dir / "bank_statement.pdf"


@pytest.fixture
def contacts_json(samples_dir: Path) -> Path:
    return samples_dir / "messy_contacts.json"


@pytest.fixture
def contacts_xlsx(samples_dir: Path) -> Path:
    return samples_dir / "messy_contacts.xlsx"


@pytest.fixture
def contacts_frame(contacts_csv: Path) -> pd.DataFrame:
    return pd.read_csv(contacts_csv, dtype=str, keep_default_na=False)


@pytest.fixture
def clean_frame() -> pd.DataFrame:
    """A small, already-canonical frame for writer and profiler tests."""
    return pd.DataFrame(
        {
            "firstname": ["Ann", "Bob", "Cara"],
            "lastname": ["Smith", "Jones", "Lee"],
            "email": ["ann@x.com", "bob@x.com", "cara@x.com"],
            "phone": ["+14155552671", "+14155552672", "+14155552673"],
        }
    )