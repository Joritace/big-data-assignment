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
[data-testid="stMetricValue"] { font-size: 26px; }
.block { padding: 10px 0px; }
</style>
""", unsafe_allow_html=True)


# load report + convert to dataframes
@st.cache_data
def load_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(BASE_DIR, "..", "output", "report.json")

    if not os.path.exists(json_path):
        st.error("report.json not found")
        st.stop()

    with open(json_path, "r") as f:
        data = json.load(f)

    inv = pd.DataFrame(data["top_inventors"]).sort_values("total_patents", ascending=False)
    comp = pd.DataFrame(data["top_companies"]).sort_values("total_patents", ascending=False)
    count = pd.DataFrame(data["top_countries"]).sort_values("total", ascending=False)

    return data, inv, comp, count


report, inventors_df, companies_df, countries_df = load_data()


# fix country codes for map
iso_map = {
    "US": "USA", "JP": "JPN", "DE": "DEU", "CN": "CHN",
    "KR": "KOR", "FR": "FRA", "CA": "CAN", "GB": "GBR",
    "TW": "TWN", "IN": "IND"
}
countries_df["iso3"] = countries_df["country"].map(iso_map)


# header
st.title("🛡️ Patent Intelligence Dashboard")
st.caption("overview of patent activity")


# main stats
top_company_share = (companies_df.iloc[0]["total_patents"] / report["total_patents"]) * 100
top3_share = (companies_df.head(3)["total_patents"].sum() / report["total_patents"]) * 100

k1, k2, k3, k4 = st.columns(4)

k1.metric("Total Patents", f"{report['total_patents']:,}")
k2.metric("Top Company", companies_df.iloc[0]["name"], f"{top_company_share:.1f}%")
k3.metric("Top Country", countries_df.iloc[0]["country"])
k4.metric("Top 3 Share", f"{top3_share:.1f}%")


st.divider()


# helper for consistent charts
def clean_chart(fig):
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=10, r=10, t=30, b=10)
    )
    return fig


# tabs
tab1, tab2, tab3 = st.tabs(["Companies & Inventors", "Global View", "Data"])


# companies + inventors
with tab1:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Top Companies")
        fig = px.bar(
            companies_df.head(10),
            x="total_patents",
            y="name",
            orientation="h"
        )
        st.plotly_chart(clean_chart(fig), use_container_width=True)

    with c2:
        st.subheader("Top Inventors")
        fig = px.bar(
            inventors_df.head(10),
            x="total_patents",
            y="name",
            orientation="h"
        )
        st.plotly_chart(clean_chart(fig), use_container_width=True)


# world + share
with tab2:
    c1, c2 = st.columns([2, 1])

    with c1:
        st.subheader("Patent Distribution")

        fig = px.choropleth(
            countries_df,
            locations="iso3",
            color="total",
            hover_name="country",
            color_continuous_scale="Blues"
        )
        st.plotly_chart(clean_chart(fig), use_container_width=True)

    with c2:
        st.subheader("Top Countries Share")

        fig = px.pie(
            countries_df.head(6),
            names="country",
            values="total",
            hole=0.4
        )
        st.plotly_chart(clean_chart(fig), use_container_width=True)


# raw data
with tab3:
    st.subheader("Top Companies")
    st.dataframe(companies_df, use_container_width=True)

    st.markdown("")

    st.subheader("Top Inventors")
    st.dataframe(inventors_df, use_container_width=True)

    st.markdown("")

    st.subheader("Top Countries")
    st.dataframe(countries_df, use_container_width=True)

# insights
st.markdown("---")
st.subheader("Insights")

avg_inv = inventors_df["total_patents"].mean()

st.write(f"- top company: {top_company_share:.2f}% of patents")
st.write(f"- top 3 companies: {top3_share:.2f}%")
st.write(f"- average patents per inventor: {avg_inv:.0f}")

st.success("patent activity is spread out, not dominated by one company")