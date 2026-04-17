"""
Journal Entries page UI.
"""

from datetime import date

import pandas as pd
import streamlit as st

from logic.accounts import get_accounts_dict, get_leaf_accounts
from logic.journal import (
    add_je_line,
    delete_journal_entry,
    get_all_entries,
    remove_je_line,
    save_journal_entry,
    validate_je_lines,
)
from logic.reports import format_currency


def render():
    st.markdown(
        """
    <div class='main-header'>
      <h1>✍️ القيود اليومية</h1>
      <p>تسجيل وعرض القيود المحاسبية</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    tab_view, tab_add = st.tabs(["📋 عرض القيود", "➕ إضافة قيد جديد"])

    with tab_view:
        _render_view_tab()

    with tab_add:
        _render_add_tab()


def _render_view_tab():
    entries = get_all_entries()
    if not entries:
        st.info("لا توجد قيود مسجلة حتى الآن.")
        return

    for entry in reversed(entries):
        total_dr = sum(l["dr"] for l in entry["lines"])
        total_cr = sum(l["cr"] for l in entry["lines"])
        balanced = abs(total_dr - total_cr) < 0.01

        header = (
            f"قيد رقم {entry['journal_no']} — {entry['date']} — "
            f"{entry.get('explanation', '')} | المبلغ: {format_currency(total_dr)}"
        )
        with st.expander(header):
            lines_df = pd.DataFrame(entry["lines"])
            lines_df = lines_df.rename(
                columns={
                    "code": "الكود",
                    "name": "اسم الحساب",
                    "dr": "مدين",
                    "cr": "دائن",
                    "type": "النوع",
                }
            )
            lines_df["مدين"] = lines_df["مدين"].apply(format_currency)
            lines_df["دائن"] = lines_df["دائن"].apply(format_currency)
            st.dataframe(
                lines_df[["الكود", "اسم الحساب", "مدين", "دائن"]],
                use_container_width=True,
                hide_index=True,
            )

            cols = st.columns([3, 1, 1])
            cols[0].markdown(f"**مركز التكلفة:** {entry.get('cost_centre', '-')}")
            if balanced:
                cols[1].success("✅ متوازن")
            else:
                cols[2].error("❌ غير متوازن")

            if st.button(
                f"🗑️ حذف القيد رقم {entry['journal_no']}",
                key=f"del_{entry['id']}",
            ):
                delete_journal_entry(entry["id"])
                st.rerun()


def _render_add_tab():
    st.markdown(
        "<div class='section-title'>إضافة قيد محاسبي جديد</div>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        entry_date = st.date_input("📅 التاريخ", value=date.today())
    with col2:
        explanation = st.text_input("📝 البيان", placeholder="وصف القيد...")
    with col3:
        cost_centre = st.text_input("🏢 مركز التكلفة (اختياري)", placeholder="")

    st.markdown("---")
    st.markdown("**📌 سطور القيد:**")

    # Build account options
    leaf_accounts = get_leaf_accounts()
    accounts_dict = get_accounts_dict()
    account_options = [""] + [f"{code} | {name}" for code, name in leaf_accounts]

    lines_to_remove = []
    for i, line in enumerate(st.session_state.je_lines):
        c1, c2, c3, c4 = st.columns([4, 2, 2, 1])
        with c1:
            # Determine current index
            current_label = ""
            if line["code"]:
                current_label = (
                    f"{line['code']} | {accounts_dict.get(line['code'], '')}"
                )
            idx = (
                account_options.index(current_label)
                if current_label in account_options
                else 0
            )
            sel = st.selectbox(
                f"الحساب {i + 1}",
                account_options,
                index=idx,
                key=f"acc_{i}",
            )
            if sel:
                st.session_state.je_lines[i]["code"] = sel.split(" | ")[0]
        with c2:
            dr = st.number_input(
                "مدين",
                min_value=0.0,
                value=float(line["dr"]),
                step=100.0,
                key=f"dr_{i}",
                format="%.2f",
            )
            st.session_state.je_lines[i]["dr"] = dr
        with c3:
            cr = st.number_input(
                "دائن",
                min_value=0.0,
                value=float(line["cr"]),
                step=100.0,
                key=f"cr_{i}",
                format="%.2f",
            )
            st.session_state.je_lines[i]["cr"] = cr
        with c4:
            st.write("")
            if st.button("🗑️", key=f"rm_{i}") and len(st.session_state.je_lines) > 2:
                lines_to_remove.append(i)

    for idx in reversed(lines_to_remove):
        remove_je_line(idx)
        st.rerun()

    col_add, col_save = st.columns([1, 2])
    with col_add:
        if st.button("➕ إضافة سطر"):
            add_je_line()
            st.rerun()

    # Validation display
    total_dr, total_cr, diff, is_balanced = validate_je_lines()

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("إجمالي مدين", format_currency(total_dr))
    col_b.metric("إجمالي دائن", format_currency(total_cr))
    col_c.metric("الفرق", format_currency(diff))

    if is_balanced:
        st.success("✅ القيد متوازن — جاهز للحفظ")
    elif total_dr > 0:
        st.warning(f"⚠️ القيد غير متوازن — الفرق: {format_currency(diff)}")

    with col_save:
        if st.button("💾 حفظ القيد", disabled=(not is_balanced)):
            result = save_journal_entry(entry_date, explanation, cost_centre)
            if result:
                st.success(f"✅ تم حفظ القيد رقم {result['journal_no']} بنجاح!")
                st.rerun()
