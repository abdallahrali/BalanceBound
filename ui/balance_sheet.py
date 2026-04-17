"""
Balance Sheet page UI.
"""

import plotly.graph_objects as go
import streamlit as st

from logic.reports import (
    compute_trial_balance,
    format_currency,
    get_asset_breakdown,
    get_balance_sheet_data,
)


def render():
    st.markdown(
        """
    <div class='main-header'>
      <h1>🏛️ الميزانية العمومية</h1>
      <p>Balance Sheet — المركز المالي للشركة</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    tb = compute_trial_balance()
    data = get_balance_sheet_data(tb)
    assets_df = data["assets_df"]
    liab_df = data["liab_df"]
    net_income = data["net_income"]
    total_assets = data["total_assets"]
    total_liab = data["total_liab"]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🏦 الأصول")
        if not assets_df.empty:
            a_show = assets_df[["الكود", "اسم الحساب"]].copy()
            a_show["الرصيد"] = (
                assets_df["ميزان المجاميع - مدين"] - assets_df["ميزان المجاميع - دائن"]
            ).apply(format_currency)
            st.dataframe(a_show, use_container_width=True, hide_index=True)
        st.markdown(
            f"""
        <div style='background:#0f3460; color:white; padding:12px 16px;
                    border-radius:8px; font-weight:700; font-size:16px;'>
          إجمالي الأصول: {format_currency(total_assets)}
        </div>""",
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown("### ⚖️ الإلتزامات وحقوق الملكية")
        if not liab_df.empty:
            l_show = liab_df[["الكود", "اسم الحساب"]].copy()
            l_show["الرصيد"] = (
                liab_df["ميزان المجاميع - دائن"] - liab_df["ميزان المجاميع - مدين"]
            ).apply(format_currency)
            st.dataframe(l_show, use_container_width=True, hide_index=True)
        st.markdown(
            f"**صافي الربح المضاف لحقوق الملكية:** {format_currency(net_income)}"
        )
        st.markdown(
            f"""
        <div style='background:#155724; color:white; padding:12px 16px;
                    border-radius:8px; font-weight:700; font-size:16px;'>
          إجمالي الإلتزامات وحقوق الملكية: {format_currency(total_liab)}
        </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    diff = total_assets - total_liab
    if abs(diff) < 1:
        st.success("✅ الميزانية العمومية متوازنة")
    else:
        st.warning(
            f"⚠️ فرق في الميزانية: {format_currency(abs(diff))} — "
            "قد يكون بسبب أرصدة حقوق الملكية الافتراضية"
        )

    # Asset breakdown donut chart
    labels, values = get_asset_breakdown(assets_df)
    if any(v > 0 for v in values):
        fig = go.Figure(
            go.Pie(
                labels=labels,
                values=[max(v, 0) for v in values],
                hole=0.5,
                marker=dict(
                    colors=["#0f3460", "#e94560", "#533483", "#28a745", "#ffc107"]
                ),
            )
        )
        fig.update_layout(
            title="توزيع الأصول",
            height=350,
            font=dict(family="Cairo"),
        )
        st.plotly_chart(fig, use_container_width=True)
