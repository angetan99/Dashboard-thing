# NovaRetail Executive Dashboard
# Deployment: Upload app.py, requirements.txt, and NR_dataset.xlsx to GitHub.
# Connect the repo to Streamlit Cloud at share.streamlit.io and deploy.

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="NovaRetail Executive Dashboard", layout="wide")

# ── Load Data ──────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel("NR_dataset.xlsx")
    df["TransactionDate"] = pd.to_datetime(df["TransactionDate"])
    df["label"] = df["label"].fillna("Unknown")
    return df

df = load_data()

# ── Colour palette per segment ─────────────────────────────────────────────────
SEG_COLORS = {
    "Promising": "#4CAF50",
    "Growth":    "#2196F3",
    "Stable":    "#FF9800",
    "Decline":   "#F44336",
    "Unknown":   "#9E9E9E",
}

# ── Sidebar Filters ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://via.placeholder.com/220x60?text=NovaRetail", use_column_width=True)
    st.title("📊 Filters")

    segments = ["All"] + sorted(df["label"].dropna().unique().tolist())
    sel_seg = st.multiselect("Segment", segments[1:], default=segments[1:])

    regions = sorted(df["CustomerRegion"].dropna().unique().tolist())
    sel_reg = st.multiselect("Region", regions, default=regions)

    categories = sorted(df["ProductCategory"].dropna().unique().tolist())
    sel_cat = st.multiselect("Product Category", categories, default=categories)

    channels = sorted(df["RetailChannel"].dropna().unique().tolist())
    sel_ch = st.multiselect("Retail Channel", channels, default=channels)

    age_groups = sorted(df["CustomerAgeGroup"].dropna().unique().tolist())
    sel_age = st.multiselect("Age Group", age_groups, default=age_groups)

    genders = sorted(df["CustomerGender"].dropna().unique().tolist())
    sel_gen = st.multiselect("Gender", genders, default=genders)

    min_date = df["TransactionDate"].min().date()
    max_date = df["TransactionDate"].max().date()
    date_range = st.date_input("Date Range", value=(min_date, max_date),
                               min_value=min_date, max_value=max_date)

# ── Apply filters ───────────────────────────────────────────────────────────────
fdf = df.copy()
if sel_seg:
    fdf = fdf[fdf["label"].isin(sel_seg)]
if sel_reg:
    fdf = fdf[fdf["CustomerRegion"].isin(sel_reg)]
if sel_cat:
    fdf = fdf[fdf["ProductCategory"].isin(sel_cat)]
if sel_ch:
    fdf = fdf[fdf["RetailChannel"].isin(sel_ch)]
if sel_age:
    fdf = fdf[fdf["CustomerAgeGroup"].isin(sel_age)]
if sel_gen:
    fdf = fdf[fdf["CustomerGender"].isin(sel_gen)]
if len(date_range) == 2:
    fdf = fdf[(fdf["TransactionDate"].dt.date >= date_range[0]) &
              (fdf["TransactionDate"].dt.date <= date_range[1])]

# ── Header ──────────────────────────────────────────────────────────────────────
st.markdown("# 🛍️ NovaRetail · Executive Dashboard")
st.markdown("*Omnichannel performance at a glance — updated dynamically based on sidebar filters.*")
st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 – KPI OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("## 📌 Section 1 · KPI Overview")
st.caption("High-level performance indicators. Use these to quickly assess overall business health before diving deeper.")

total_rev   = fdf["PurchaseAmount"].sum()
total_cust  = fdf["CustomerID"].nunique()
avg_rev     = total_rev / total_cust if total_cust else 0
avg_sat     = fdf["CustomerSatisfaction"].mean()

k1, k2, k3, k4 = st.columns(4)
k1.metric("💰 Total Revenue",          f"${total_rev:,.0f}")
k2.metric("👥 Total Customers",         f"{total_cust:,}")
k3.metric("📈 Avg Revenue / Customer",  f"${avg_rev:,.2f}")
k4.metric("⭐ Avg Satisfaction Score",  f"{avg_sat:.2f} / 5")

# Segment revenue pie
seg_rev = fdf.groupby("label")["PurchaseAmount"].sum().reset_index()
fig_pie = px.pie(seg_rev, names="label", values="PurchaseAmount",
                 title="Revenue Share by Segment",
                 color="label", color_discrete_map=SEG_COLORS,
                 hole=0.4)
fig_pie.update_layout(margin=dict(t=40, b=0))
st.plotly_chart(fig_pie, use_container_width=True)
st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 – CUSTOMER SEGMENTATION ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("## 🧩 Section 2 · Customer Segmentation Analysis")
st.caption("Compare revenue, customer count, and satisfaction across segments. Focus on which segment drives growth and which shows warning signs.")

col1, col2, col3 = st.columns(3)

with col1:
    rev_seg = fdf.groupby("label")["PurchaseAmount"].sum().reset_index()
    fig = px.bar(rev_seg, x="label", y="PurchaseAmount", color="label",
                 color_discrete_map=SEG_COLORS, title="Revenue by Segment",
                 labels={"PurchaseAmount": "Revenue ($)", "label": "Segment"})
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    cnt_seg = fdf.groupby("label")["CustomerID"].nunique().reset_index()
    cnt_seg.columns = ["label", "Customers"]
    fig = px.bar(cnt_seg, x="label", y="Customers", color="label",
                 color_discrete_map=SEG_COLORS, title="Customers by Segment",
                 labels={"label": "Segment"})
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col3:
    sat_seg = fdf.groupby("label")["CustomerSatisfaction"].mean().reset_index()
    fig = px.bar(sat_seg, x="label", y="CustomerSatisfaction", color="label",
                 color_discrete_map=SEG_COLORS, title="Avg Satisfaction by Segment",
                 labels={"CustomerSatisfaction": "Avg Score", "label": "Segment"},
                 range_y=[0, 5])
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# Revenue Trend by Segment
trend = fdf.groupby([pd.Grouper(key="TransactionDate", freq="M"), "label"])["PurchaseAmount"].sum().reset_index()
fig_trend = px.line(trend, x="TransactionDate", y="PurchaseAmount", color="label",
                    color_discrete_map=SEG_COLORS,
                    title="Revenue Trend Over Time by Segment",
                    labels={"PurchaseAmount": "Revenue ($)", "TransactionDate": "Month", "label": "Segment"})
st.plotly_chart(fig_trend, use_container_width=True)
st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 – GROWTH OPPORTUNITIES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("## 🚀 Section 3 · Growth Opportunities")
st.caption("Identify the strongest categories, regions, and channels. Use the stacked bar to pinpoint high-value segment–category combinations.")

col4, col5 = st.columns(2)

with col4:
    cat_rev = fdf.groupby("ProductCategory")["PurchaseAmount"].sum().reset_index().sort_values("PurchaseAmount", ascending=True)
    fig = px.bar(cat_rev, x="PurchaseAmount", y="ProductCategory", orientation="h",
                 title="Revenue by Product Category",
                 labels={"PurchaseAmount": "Revenue ($)", "ProductCategory": "Category"})
    st.plotly_chart(fig, use_container_width=True)

with col5:
    reg_rev = fdf.groupby("CustomerRegion")["PurchaseAmount"].sum().reset_index().sort_values("PurchaseAmount", ascending=False)
    fig = px.bar(reg_rev, x="CustomerRegion", y="PurchaseAmount",
                 title="Revenue by Region",
                 labels={"PurchaseAmount": "Revenue ($)", "CustomerRegion": "Region"},
                 color="PurchaseAmount", color_continuous_scale="Blues")
    st.plotly_chart(fig, use_container_width=True)

col6, col7 = st.columns(2)

with col6:
    ch_rev = fdf.groupby("RetailChannel")["PurchaseAmount"].sum().reset_index()
    fig = px.bar(ch_rev, x="RetailChannel", y="PurchaseAmount",
                 title="Revenue by Retail Channel",
                 labels={"PurchaseAmount": "Revenue ($)", "RetailChannel": "Channel"},
                 color="RetailChannel", color_discrete_sequence=["#5C6BC0", "#26A69A"])
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col7:
    cat_seg = fdf.groupby(["ProductCategory", "label"])["PurchaseAmount"].sum().reset_index()
    top_cats = cat_seg.groupby("ProductCategory")["PurchaseAmount"].sum().nlargest(10).index
    cat_seg_top = cat_seg[cat_seg["ProductCategory"].isin(top_cats)]
    fig = px.bar(cat_seg_top, x="ProductCategory", y="PurchaseAmount", color="label",
                 color_discrete_map=SEG_COLORS, barmode="stack",
                 title="Top 10 Categories · Revenue by Segment",
                 labels={"PurchaseAmount": "Revenue ($)", "ProductCategory": "Category", "label": "Segment"})
    fig.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 – EARLY WARNING SIGNALS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("## ⚠️ Section 4 · Early Warning Signals")
st.caption("Monitor the Decline segment closely. Low satisfaction scores, geographic concentration, and specific categories at risk are key signals for leadership action.")

col8, col9 = st.columns(2)

with col8:
    fig = px.bar(sat_seg, x="label", y="CustomerSatisfaction", color="label",
                 color_discrete_map=SEG_COLORS, title="Satisfaction Score by Segment",
                 labels={"CustomerSatisfaction": "Avg Score", "label": "Segment"},
                 range_y=[0, 5])
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col9:
    decline_df = fdf[fdf["label"] == "Decline"]
    if not decline_df.empty:
        d_trend = decline_df.groupby(pd.Grouper(key="TransactionDate", freq="M"))["PurchaseAmount"].sum().reset_index()
        fig = px.line(d_trend, x="TransactionDate", y="PurchaseAmount",
                      title="Revenue Trend – Decline Segment",
                      labels={"PurchaseAmount": "Revenue ($)", "TransactionDate": "Month"},
                      line_shape="spline", color_discrete_sequence=["#F44336"])
        fig.update_traces(fill="tozeroy", fillcolor="rgba(244,67,54,0.1)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No Decline segment data in the current filter selection.")

col10, col11 = st.columns(2)

with col10:
    if not decline_df.empty:
        d_reg = decline_df.groupby("CustomerRegion")["CustomerID"].nunique().reset_index()
        d_reg.columns = ["Region", "Customers"]
        fig = px.bar(d_reg, x="Region", y="Customers",
                     title="Decline Customers by Region",
                     color="Customers", color_continuous_scale="Reds")
        st.plotly_chart(fig, use_container_width=True)

with col11:
    if not decline_df.empty:
        d_cat = decline_df.groupby("ProductCategory")["PurchaseAmount"].sum().reset_index().sort_values("PurchaseAmount", ascending=True).tail(10)
        fig = px.bar(d_cat, x="PurchaseAmount", y="ProductCategory", orientation="h",
                     title="Decline Revenue by Category (Top 10)",
                     color="PurchaseAmount", color_continuous_scale="Reds",
                     labels={"PurchaseAmount": "Revenue ($)", "ProductCategory": "Category"})
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 – DEMOGRAPHIC INSIGHTS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("## 👤 Section 5 · Demographic Insights")
st.caption("Explore how revenue and segment distribution vary by age group and gender. Use these insights to target marketing and retention efforts.")

col12, col13 = st.columns(2)

with col12:
    age_rev = fdf.groupby("CustomerAgeGroup")["PurchaseAmount"].sum().reset_index().sort_values("PurchaseAmount", ascending=False)
    fig = px.bar(age_rev, x="CustomerAgeGroup", y="PurchaseAmount",
                 title="Revenue by Age Group",
                 labels={"PurchaseAmount": "Revenue ($)", "CustomerAgeGroup": "Age Group"},
                 color="PurchaseAmount", color_continuous_scale="Viridis")
    st.plotly_chart(fig, use_container_width=True)

with col13:
    gen_rev = fdf.groupby("CustomerGender")["PurchaseAmount"].sum().reset_index()
    fig = px.pie(gen_rev, names="CustomerGender", values="PurchaseAmount",
                 title="Revenue by Gender",
                 color_discrete_sequence=["#42A5F5", "#EF5350"], hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

age_seg = fdf.groupby(["CustomerAgeGroup", "label"])["CustomerID"].nunique().reset_index()
age_seg.columns = ["AgeGroup", "Segment", "Customers"]
fig = px.bar(age_seg, x="AgeGroup", y="Customers", color="Segment",
             color_discrete_map=SEG_COLORS, barmode="group",
             title="Segment Distribution by Age Group",
             labels={"AgeGroup": "Age Group", "Customers": "Number of Customers"})
st.plotly_chart(fig, use_container_width=True)

st.divider()
st.caption("NovaRetail Executive Dashboard · Powered by Streamlit & Plotly · Data: NR_dataset.xlsx")
