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
    # Assuming CSV headers are: code, dr, cr
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
        {"code": "", "account_type": "", "cost_centre": "", "numerical": 0, "dr": 0.0, "cr": 0.0},
        {"code": "", "account_type": "", "cost_centre": "", "numerical": 0, "dr": 0.0, "cr": 0.0},
    ]

def add_je_line():
    """Append a blank line to the working journal entry."""
    st.session_state.je_lines.append(
        {"code": "", "account_type": "", "cost_centre": "", "numerical": 0, "dr": 0.0, "cr": 0.0}
    )

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
    # Balanced if difference is negligible and there is at least one debit
    is_balanced = diff < 0.01 and total_dr > 0
    return total_dr, total_cr, diff, is_balanced


# logic/journal.py

def save_journal_entry(
    entry_date: date,
    explanation: str,
    # Remove cost_centre from here as it's now in the lines
) -> dict | None:
    accounts = get_accounts_dict()
    new_lines = []
    for line in st.session_state.je_lines:
        if line["code"] and (line["dr"] > 0 or line["cr"] > 0):
            new_lines.append(
                {
                    "code": line["code"],
                    "name": accounts.get(line["code"], line["code"]),
                    "account_type": line.get("account_type", ""),
                    "cost_centre": line.get("cost_centre", ""), # Get from line
                    "numerical": int(line.get("numerical", 0)),
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
        # cost_centre is now inside 'lines'
        "lines": new_lines,
    }

    st.session_state.entries.append(new_entry)
    st.session_state.next_journal += 1

    try:
        with open(SAMPLE_ENTRIES_JSON, "w", encoding="utf-8") as f:
            json.dump(st.session_state.entries, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Failed to save to JSON: {e}")

    reset_je_lines()
    return new_entry

def delete_journal_entry(entry_id: int):
    """Delete a journal entry by its ID and update the JSON file."""
    # 1. Remove from session state
    st.session_state.entries = [
        e for e in st.session_state.entries if e["id"] != entry_id
    ]

    # 2. Update the JSON file
    try:
        with open(SAMPLE_ENTRIES_JSON, "w", encoding="utf-8") as f:
            json.dump(st.session_state.entries, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Failed to delete from JSON: {e}")


def get_all_entries() -> list[dict]:
    """Return all journal entries."""
    return st.session_state.entries


# Add this at the end of logic/journal.py


def update_opening_balance(code: str, dr: float, cr: float):
    """Update opening balance for an account and save to CSV."""
    st.session_state.opening_balances[code] = {"dr": dr, "cr": cr}

    # Format as a list of dictionaries for pandas
    data = [
        {"code": c, "dr": b["dr"], "cr": b["cr"]}
        for c, b in st.session_state.opening_balances.items()
    ]
    df = pd.DataFrame(data)

    try:
        df.to_csv(OPENING_BALANCES_CSV, index=False)
    except Exception as e:
        st.error(f"Failed to save opening balances to CSV: {e}")
