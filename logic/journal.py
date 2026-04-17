"""
Journal entry operations: creation, validation, state management.
"""

import json
from datetime import date

import pandas as pd
import streamlit as st

from config import OPENING_BALANCES_CSV, SAMPLE_ENTRIES_JSON
from logic.accounts import get_account_type, get_accounts_dict


def _load_opening_balances() -> dict:
    """Load opening balances from CSV."""
    df = pd.read_csv(OPENING_BALANCES_CSV, dtype={"code": str})
    result = {}
    for _, row in df.iterrows():
        result[row["code"]] = {"dr": float(row["dr"]), "cr": float(row["cr"])}
    return result


def _load_sample_entries() -> list[dict]:
    """Load seed journal entries from JSON."""
    with open(SAMPLE_ENTRIES_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def init_session_state():
    """Initialize all journal-related session state."""
    if "entries" not in st.session_state:
        st.session_state.entries = _load_sample_entries()
    if "next_journal" not in st.session_state:
        existing = [e["journal_no"] for e in st.session_state.entries]
        st.session_state.next_journal = max(existing, default=0) + 1
    if "opening_balances" not in st.session_state:
        st.session_state.opening_balances = _load_opening_balances()
    if "je_lines" not in st.session_state:
        reset_je_lines()


def reset_je_lines():
    """Reset the working journal entry lines to two blank rows."""
    st.session_state.je_lines = [
        {"code": "", "dr": 0.0, "cr": 0.0},
        {"code": "", "dr": 0.0, "cr": 0.0},
    ]


def add_je_line():
    """Append a blank line to the working journal entry."""
    st.session_state.je_lines.append({"code": "", "dr": 0.0, "cr": 0.0})


def remove_je_line(index: int):
    """Remove a line by index (minimum 2 lines enforced)."""
    if len(st.session_state.je_lines) > 2:
        st.session_state.je_lines.pop(index)


def validate_je_lines() -> tuple[float, float, float, bool]:
    """
    Validate current working lines.
    Returns (total_dr, total_cr, difference, is_balanced).
    """
    total_dr = sum(l["dr"] for l in st.session_state.je_lines)
    total_cr = sum(l["cr"] for l in st.session_state.je_lines)
    diff = abs(total_dr - total_cr)
    is_balanced = diff < 0.01 and total_dr > 0
    return total_dr, total_cr, diff, is_balanced


def save_journal_entry(
    entry_date: date,
    explanation: str,
    cost_centre: str,
) -> dict | None:
    """
    Save the current working lines as a new journal entry.
    Returns the saved entry dict, or None if nothing to save.
    """
    accounts = get_accounts_dict()
    new_lines = []
    for line in st.session_state.je_lines:
        if line["code"] and (line["dr"] > 0 or line["cr"] > 0):
            new_lines.append(
                {
                    "code": line["code"],
                    "name": accounts.get(line["code"], line["code"]),
                    "dr": line["dr"],
                    "cr": line["cr"],
                    "type": get_account_type(line["code"]),
                }
            )
    if not new_lines:
        return None

    new_entry = {
        "id": max((e["id"] for e in st.session_state.entries), default=0) + 1,
        "date": entry_date.strftime("%Y-%m-%d"),
        "journal_no": st.session_state.next_journal,
        "explanation": explanation,
        "cost_centre": cost_centre,
        "lines": new_lines,
    }
    st.session_state.entries.append(new_entry)
    st.session_state.next_journal += 1
    reset_je_lines()
    return new_entry


def delete_journal_entry(entry_id: int):
    """Delete a journal entry by its ID."""
    st.session_state.entries = [
        e for e in st.session_state.entries if e["id"] != entry_id
    ]


def get_all_entries() -> list[dict]:
    """Return all journal entries."""
    return st.session_state.entries
