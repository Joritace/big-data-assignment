import os
import json
import streamlit as st
import pandas as pd
import plotly.express as px

# page setup
st.set_page_config(
    page_title="Patent Intelligence",
    page_icon="🛡️",
    layout="wide"
)

# simple styling
st.markdown("""
<style>
    [data-testid="stMetricValue"] { font-size: 28px; font-weight: 700; color: #1f77b4; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; font-size: 16px; }
    .main-stats-card { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #1f77b4; }
</style>
""", unsafe_allow_html=True)

# load the json report and convert to dataframes
@st.cache_data
def load_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(BASE_DIR, "..", "output")

    json_path = os.path.join(output_dir, "report.json")
    country_trends_path = os.path.join(output_dir, "country_trends.csv")
    patent_trends_path = os.path.join(output_dir, "patent_trends.csv")

    if not os.path.exists(json_path):
        st.error("report.json not found")
        st.stop()

    with open(json_path, "r") as f:
        data = json.load(f)

    inv = pd.DataFrame(data["top_inventors"]).sort_values("total_patents", ascending=True) # Ascending for better H-Bar display
    comp = pd.DataFrame(data["top_companies"]).sort_values("total_patents", ascending=True)
    count = pd.DataFrame(data["top_countries"]).sort_values("total", ascending=False)

    country_trends = pd.read_csv(country_trends_path)
    patent_trends = pd.read_csv(patent_trends_path)

    # standardize column names for consistency
    if "total" in patent_trends.columns:
        patent_trends = patent_trends.rename(columns={"total": "total_patents"})

    if "total" in country_trends.columns:
        country_trends = country_trends.rename(columns={"total": "total_patents"})

    return data, inv, comp, count, country_trends, patent_trends

report, inventors_df, companies_df, countries_df, country_trends_df, patent_trends_df = load_data()

# fix country codes for map
iso_map = {
    "US": "USA", "JP": "JPN", "DE": "DEU", "CN": "CHN",
    "KR": "KOR", "FR": "FRA", "CA": "CAN", "GB": "GBR",
    "TW": "TWN", "IN": "IND"
}
countries_df["iso3"] = countries_df["country"].map(iso_map)

st.title("🛡️ Patent Analytics Dashboard")

# main stats
top_company_share = (
    companies_df.iloc[-1]["total_patents"] / report["total_patents"]
) * 100

top3_share = (
    companies_df.tail(3)["total_patents"].sum() / report["total_patents"]
) * 100

# Metric Cards
with st.container():
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Total Patents", f"{report['total_patents']:,}")
    with k2:
        st.metric("Top Company", companies_df.iloc[-1]["name"], f"{top_company_share:.1f}%")
    with k3:
        st.metric("Top Country", countries_df.iloc[0]["country"])
    with k4:
        st.metric("Top 3 Share", f"{top3_share:.1f}%")

st.write("---")

# helper for consistent charts
def clean_chart(fig):
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode="x unified"
    )
    return fig

# tabs
tab1, tab2, tab4, tab3 = st.tabs([
    "Companies & Inventors",
    "Global View",
    "Trends",
    "Data"
])

# tab 1, top companies and inventors
with tab1:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Top Companies")
        fig = px.bar(
            companies_df.tail(10),
            x="total_patents",
            y="name",
            orientation="h",
            color="total_patents",
            color_continuous_scale="Blues"
        )
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(clean_chart(fig), use_container_width=True)

    with c2:
        st.subheader("Top Inventors")
        fig = px.bar(
            inventors_df.tail(10),
            x="total_patents",
            y="name",
            orientation="h",
            color="total_patents",
            color_continuous_scale="Greens"
        )
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(clean_chart(fig), use_container_width=True)

# tab 2, global distribution
with tab2:
    c1, c2 = st.columns([2, 1])

    with c1:
        st.subheader("Patent Distribution")
        fig = px.choropleth(
            countries_df,
            locations="iso3",
            color="total",
            hover_name="country",
            projection="natural earth",
            color_continuous_scale="Blues"
        )
        st.plotly_chart(clean_chart(fig), use_container_width=True)

    with c2:
        st.subheader("Top Countries Share")
        fig = px.pie(
            countries_df.head(6),
            names="country",
            values="total",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(clean_chart(fig), use_container_width=True)

# tab 4, trends over time
with tab4:
    st.subheader("Patent Growth Over Time")
    fig = px.line(
        patent_trends_df,
        x="year",
        y="total_patents",
        markers=True,
        line_shape="spline"
    )
    st.plotly_chart(clean_chart(fig), use_container_width=True)

    st.subheader("Country Patent Trends")
    selected = st.selectbox(
        "Select country",
        country_trends_df["country"].unique()
    )

    filtered = country_trends_df[
        country_trends_df["country"] == selected
    ]

    fig = px.area(
        filtered,
        x="year",
        y="total_patents",
        title=f"{selected} Patent Growth",
        markers=True
    )
    st.plotly_chart(clean_chart(fig), use_container_width=True)

# tab 3, raw data tables
with tab3:
    with st.expander("View Top Companies"):
        st.dataframe(companies_df.sort_values("total_patents", ascending=False), use_container_width=True)
    with st.expander("View Top Inventors"):
        st.dataframe(inventors_df.sort_values("total_patents", ascending=False), use_container_width=True)
    with st.expander("View Top Countries"):
        st.dataframe(countries_df, use_container_width=True)

# insights
st.markdown("---")
st.subheader("Key Insights")

avg_inv = inventors_df["total_patents"].mean()

# Creating a clean, card-like layout for insights
# Using columns to space out the metrics, but keeping the logic focused on the analysis
col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"**Market Concentration**\nThe top company accounts for **{top_company_share:.2f}%** of all patent filings.")

with col2:
    st.info(f"**Top Player Influence**\nThe top 3 companies combined represent **{top3_share:.2f}%** of the total volume.")

with col3:
    st.info(f"**Researcher Productivity**\nOn average, inventors in this dataset are credited with **{avg_inv:.0f}** patents.")

# Large summary box at the bottom
st.success(f"**Analysis Conclusion:** Patent activity is spread out, not dominated by one company.")