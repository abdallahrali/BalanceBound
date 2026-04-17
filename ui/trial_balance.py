"""
Trial Balance page UI.
"""

import io

import streamlit as st

from logic.reports import compute_trial_balance, format_currency


def render():
    st.markdown(
        """
    <div class='main-header'>
      <h1>⚖️ ميزان المراجعة</h1>
      <p>Trial Balance — عرض أرصدة جميع الحسابات</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    tb = compute_trial_balance()

    if tb.empty:
        st.info("لا توجد بيانات لعرضها. أضف قيوداً أولاً.")
        return

    # Summary metrics
    total_ob_dr = tb["رصيد أول المدة - مدين"].sum()
    total_mv_dr = tb["الحركة - مدين"].sum()
    total_tb_dr = tb["ميزان المجاميع - مدين"].sum()
    total_tb_cr = tb["ميزان المجاميع - دائن"].sum()

    c1, c2, c3 = st.columns(3)
    c1.metric("رصيد أول المدة (مدين)", format_currency(total_ob_dr))
    c2.metric("إجمالي الحركة (مدين)", format_currency(total_mv_dr))
    c3.metric("ميزان المجاميع (مدين)", format_currency(total_tb_dr))

    is_balanced = abs(total_tb_dr - total_tb_cr) < 0.01
    if is_balanced:
        st.success("✅ الميزان متوازن")
    else:
        st.error(
            f"❌ الميزان غير متوازن — الفرق: "
            f"{format_currency(abs(total_tb_dr - total_tb_cr))}"
        )

    st.markdown("---")

    # Display table
    display_cols = [
        "رصيد أول المدة - مدين",
        "رصيد أول المدة - دائن",
        "الحركة - مدين",
        "الحركة - دائن",
        "ميزان المجاميع - مدين",
        "ميزان المجاميع - دائن",
        "الرصيد",
    ]
    display_tb = tb.copy()
    for col in display_cols:
        display_tb[col] = display_tb[col].apply(format_currency)

    st.dataframe(
        display_tb[
            [
                "الكود",
                "اسم الحساب",
                "نوع الحساب",
                *display_cols,
                "طبيعة الرصيد",
            ]
        ],
        use_container_width=True,
        hide_index=True,
        height=450,
    )

    # Export
    buf = io.BytesIO()
    tb.to_excel(buf, index=False)
    st.download_button(
        "📥 تحميل ميزان المراجعة (Excel)",
        data=buf.getvalue(),
        file_name="trial_balance.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
