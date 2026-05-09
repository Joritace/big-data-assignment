import os
import json
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


# Page setup
st.set_page_config(
    page_title="Patent Intelligence Dashboard",
    page_icon="🧠",
    layout="wide"
)

st.markdown("""
<style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    [data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 800;
    }

    [data-testid="stMetricLabel"] {
        font-size: 15px;
    }

    .insight-card {
        background-color: #f8fafc;
        padding: 18px;
        border-radius: 14px;
        border-left: 6px solid #2563eb;
        box-shadow: 0px 1px 5px rgba(0,0,0,0.08);
        min-height: 125px;
    }

    .orange-card {
        background-color: #fff7ed;
        padding: 18px;
        border-radius: 14px;
        border-left: 6px solid #f97316;
        box-shadow: 0px 1px 5px rgba(0,0,0,0.08);
        min-height: 125px;
    }

    .green-card {
        background-color: #f0fdf4;
        padding: 18px;
        border-radius: 14px;
        border-left: 6px solid #22c55e;
        box-shadow: 0px 1px 5px rgba(0,0,0,0.08);
        min-height: 125px;
    }

    .small-note {
        color: #64748b;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)


# Project paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "output")


# Apply a clean and consistent chart style
def clean_chart(fig):
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=20, r=20, t=45, b=25),
        hovermode="x unified"
    )
    return fig


chart_counter = 0

# Display charts using unique keys so Streamlit does not create duplicate chart IDs
def show_chart(fig):
    global chart_counter
    chart_counter += 1

    st.plotly_chart(
        clean_chart(fig),
        use_container_width=True,
        key=f"chart_{chart_counter}"
    )


# Standardize count column names across different output files
def rename_count_column(df):
    df = df.copy()

    if "total" in df.columns and "total_patents" not in df.columns:
        df = df.rename(columns={"total": "total_patents"})

    return df


# Convert a number into a percentage of the total
def percent(part, whole):
    if whole == 0 or pd.isna(whole):
        return 0
    return (part / whole) * 100


# Load optional CSV files without stopping the dashboard if they are missing
def optional_csv(filename):
    path = os.path.join(OUTPUT_DIR, filename)

    if os.path.exists(path):
        return pd.read_csv(path)

    return pd.DataFrame()


# Load required CSV files because the dashboard depends on them
def required_csv(filename):
    path = os.path.join(OUTPUT_DIR, filename)

    if not os.path.exists(path):
        st.error(f"{filename} was not found in the output folder.")
        st.stop()

    return pd.read_csv(path)


# Convert a column to numeric values where possible
def safe_numeric(df, column):
    if column in df.columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    return df


# Show a simple message when an optional analysis file is missing
def show_missing_file(message):
    st.info(message)


# Load and prepare all dashboard data once, then cache it for faster refreshes
@st.cache_data
def load_data():
    json_path = os.path.join(OUTPUT_DIR, "report.json")

    if not os.path.exists(json_path):
        st.error("report.json not found in the output folder.")
        st.stop()

    with open(json_path, "r", encoding="utf-8") as f:
        report = json.load(f)

    inventors = pd.DataFrame(report.get("top_inventors", []))
    companies = pd.DataFrame(report.get("top_companies", []))
    countries = pd.DataFrame(report.get("top_countries", []))

    inventors = rename_count_column(inventors)
    companies = rename_count_column(companies)
    countries = rename_count_column(countries)

    country_trends = rename_count_column(required_csv("country_trends.csv"))
    patent_trends = rename_count_column(required_csv("patent_trends.csv"))
    technology_trends = optional_csv("technology_trends.csv")
    technology_totals = optional_csv("technology_totals.csv")
    technology_growth = optional_csv("technology_growth.csv")
    technology_sector_share = optional_csv("technology_sector_share.csv")
    complexity_by_year = optional_csv("complexity_by_year.csv")
    most_complex_patents = optional_csv("most_complex_patents.csv")

    # Keep count column names consistent for all analysis tables
    technology_trends = rename_count_column(technology_trends)
    technology_totals = rename_count_column(technology_totals)
    technology_growth = rename_count_column(technology_growth)
    technology_sector_share = rename_count_column(technology_sector_share)
    complexity_by_year = rename_count_column(complexity_by_year)
    most_complex_patents = rename_count_column(most_complex_patents)

    # Clean key numeric columns used in calculations and charts
    for df in [inventors, companies, countries, country_trends, patent_trends]:
        if not df.empty:
            if "total_patents" in df.columns:
                df["total_patents"] = pd.to_numeric(
                    df["total_patents"],
                    errors="coerce"
                ).fillna(0)

            if "year" in df.columns:
                df["year"] = pd.to_numeric(df["year"], errors="coerce")

    if not technology_trends.empty:
        technology_trends = safe_numeric(technology_trends, "year")
        technology_trends = safe_numeric(technology_trends, "total_patents")

    if not technology_totals.empty:
        technology_totals = safe_numeric(technology_totals, "total_patents")

    if not technology_growth.empty:
        technology_growth = safe_numeric(technology_growth, "recent_patents")
        technology_growth = safe_numeric(technology_growth, "previous_patents")
        technology_growth = safe_numeric(technology_growth, "growth_percent")

    if not technology_sector_share.empty:
        technology_sector_share = safe_numeric(technology_sector_share, "total_patents")

    if not complexity_by_year.empty:
        numeric_cols = [
            "year",
            "patents_with_figure_data",
            "avg_figures",
            "avg_sheets",
            "avg_complexity_score",
            "high_complexity_share"
        ]

        for col in numeric_cols:
            complexity_by_year = safe_numeric(complexity_by_year, col)

    if not most_complex_patents.empty:
        numeric_cols = [
            "year",
            "num_figures",
            "num_sheets",
            "complexity_score"
        ]

        for col in numeric_cols:
            most_complex_patents = safe_numeric(most_complex_patents, col)

    # Sort summary tables so the strongest contributors appear first
    if not inventors.empty and "total_patents" in inventors.columns:
        inventors = inventors.sort_values("total_patents", ascending=False)

    if not companies.empty and "total_patents" in companies.columns:
        companies = companies.sort_values("total_patents", ascending=False)

    if not countries.empty and "total_patents" in countries.columns:
        countries = countries.sort_values("total_patents", ascending=False)

    return {
        "report": report,
        "inventors": inventors,
        "companies": companies,
        "countries": countries,
        "country_trends": country_trends,
        "patent_trends": patent_trends,
        "technology_trends": technology_trends,
        "technology_totals": technology_totals,
        "technology_growth": technology_growth,
        "technology_sector_share": technology_sector_share,
        "complexity_by_year": complexity_by_year,
        "most_complex_patents": most_complex_patents
    }


# Store loaded data in clear variable names for each dashboard section
data = load_data()

report = data["report"]
inventors_df = data["inventors"]
companies_df = data["companies"]
countries_df = data["countries"]
country_trends_df = data["country_trends"]
patent_trends_df = data["patent_trends"]

technology_trends_df = data["technology_trends"]
technology_totals_df = data["technology_totals"]
technology_growth_df = data["technology_growth"]
technology_sector_share_df = data["technology_sector_share"]

complexity_by_year_df = data["complexity_by_year"]
most_complex_patents_df = data["most_complex_patents"]


# Calculate the main values shown at the top of the dashboard
total_patents = int(report.get("total_patents", 0))

if total_patents == 0 and not patent_trends_df.empty and "total_patents" in patent_trends_df.columns:
    total_patents = int(patent_trends_df["total_patents"].sum())

if not companies_df.empty:
    top_company = companies_df.iloc[0]["name"]
    top_company_patents = companies_df.iloc[0]["total_patents"]
    top_company_share = percent(top_company_patents, total_patents)
    top3_share = percent(companies_df.head(3)["total_patents"].sum(), total_patents)
else:
    top_company = "N/A"
    top_company_share = 0
    top3_share = 0

if not countries_df.empty:
    top_country = countries_df.iloc[0]["country"]
else:
    top_country = "N/A"

if not patent_trends_df.empty and "year" in patent_trends_df.columns:
    latest_year = int(patent_trends_df["year"].max())
else:
    latest_year = "N/A"


# Compare the most recent five years with the five years before them for each country
country_growth = pd.DataFrame()

if not country_trends_df.empty and "year" in country_trends_df.columns and latest_year != "N/A":
    recent_years = country_trends_df[
        country_trends_df["year"] >= latest_year - 4
    ]

    previous_years = country_trends_df[
        (country_trends_df["year"] >= latest_year - 9) &
        (country_trends_df["year"] <= latest_year - 5)
    ]

    if not recent_years.empty and not previous_years.empty:
        recent_sum = recent_years.groupby("country", as_index=False)["total_patents"].sum()
        previous_sum = previous_years.groupby("country", as_index=False)["total_patents"].sum()

        recent_sum = recent_sum.rename(columns={"total_patents": "recent_patents"})
        previous_sum = previous_sum.rename(columns={"total_patents": "previous_patents"})

        country_growth = recent_sum.merge(previous_sum, on="country", how="left")
        country_growth["previous_patents"] = country_growth["previous_patents"].fillna(0)

        country_growth = country_growth[country_growth["previous_patents"] > 0]

        country_growth["growth_percent"] = (
            (country_growth["recent_patents"] - country_growth["previous_patents"]) /
            country_growth["previous_patents"]
        ) * 100

        country_growth = country_growth.sort_values("growth_percent", ascending=False)


st.title("🧠 Global Patent Intelligence Dashboard")

st.markdown("""
A summary of patent activity across companies, countries, technology fields, and technical complexity.
""")

st.write("---")


# Key performance indicators
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric("Total Patents", f"{total_patents:,}")

with k2:
    st.metric("Leading Company", top_company, f"{top_company_share:.2f}% share")

with k3:
    st.metric("Leading Country", top_country)

with k4:
    st.metric("Latest Year", latest_year)


st.write("---")


# Main dashboard sections
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Executive Overview",
    "Company Concentration",
    "Country Analysis",
    "Technology Trends",
    "Patent Complexity",
    "Core Charts",
    "Data Tables"
])


# Executive overview
with tab1:
    st.subheader("Executive Overview")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"""
        <div class="insight-card">
            <b>Leading company</b><br><br>
            <b>{top_company}</b> has the highest patent count, representing
            <b>{top_company_share:.2f}%</b> of the patents in this dataset.
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="green-card">
            <b>Top company group</b><br><br>
            The top 3 companies together account for
            <b>{top3_share:.2f}%</b> of all patents.
        </div>
        """, unsafe_allow_html=True)

    with c3:
        if not country_growth.empty:
            fastest_country = country_growth.iloc[0]["country"]
            fastest_growth = country_growth.iloc[0]["growth_percent"]

            st.markdown(f"""
            <div class="orange-card">
                <b>Fastest-growing country</b><br><br>
                <b>{fastest_country}</b> recorded the strongest recent growth,
                at <b>{fastest_growth:.1f}%</b> compared with the previous period.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="orange-card">
                <b>Country growth</b><br><br>
                Country growth could not be calculated because yearly country data is limited.
            </div>
            """, unsafe_allow_html=True)

    st.write("")

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Patent Activity Over Time")

        fig = px.line(
            patent_trends_df,
            x="year",
            y="total_patents",
            markers=True,
            labels={
                "year": "Year",
                "total_patents": "Number of patents"
            }
        )

        fig.update_traces(line=dict(width=3))
        show_chart(fig)

    with c2:
        st.subheader("Top Countries by Patent Output")

        fig = px.bar(
            countries_df.head(10).sort_values("total_patents"),
            x="total_patents",
            y="country",
            orientation="h",
            text="total_patents",
            labels={
                "country": "Country",
                "total_patents": "Patents"
            }
        )

        fig.update_traces(texttemplate="%{text:,}", textposition="outside")
        show_chart(fig)


# largest companies and how much of the total patent output they account for
with tab2:
    st.subheader("Company Concentration")

    if companies_df.empty:
        st.info("Company data was not found.")
    else:
        company_power = companies_df.head(20).copy()
        company_power = company_power.sort_values("total_patents", ascending=False)

        company_power["cumulative_patents"] = company_power["total_patents"].cumsum()
        company_power["cumulative_share"] = (
            company_power["cumulative_patents"] / total_patents
        ) * 100

        st.caption("Patent counts are compared with cumulative share to show how much ownership is held by the largest companies.")

        fig = go.Figure()

        fig.add_bar(
            x=company_power["name"],
            y=company_power["total_patents"],
            name="Patent count"
        )

        fig.add_trace(go.Scatter(
            x=company_power["name"],
            y=company_power["cumulative_share"],
            name="Cumulative share (%)",
            yaxis="y2",
            mode="lines+markers"
        ))

        fig.update_layout(
            xaxis=dict(tickangle=-45),
            yaxis=dict(title="Patent count"),
            yaxis2=dict(
                title="Cumulative share (%)",
                overlaying="y",
                side="right"
            ),
            legend=dict(
                orientation="h",
                y=1.1,
                x=0
            )
        )

        show_chart(fig)

        top10_share = percent(company_power.head(10)["total_patents"].sum(), total_patents)

        st.success(
            f"The top 10 companies account for {top10_share:.2f}% of all patents, showing the level of concentration among leading organizations."
        )


# tcountry analysis
with tab3:
    st.subheader("Country Analysis")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Country Patent Share")

        if countries_df.empty:
            st.info("Country data was not found.")
        else:
            fig = px.pie(
                countries_df.head(8),
                names="country",
                values="total_patents",
                hole=0.45
            )

            show_chart(fig)

    with c2:
        st.markdown("### Fastest-Growing Countries")

        if country_growth.empty:
            st.info("Not enough country trend data to calculate growth.")
        else:
            fig = px.bar(
                country_growth.head(10).sort_values("growth_percent"),
                x="growth_percent",
                y="country",
                orientation="h",
                text="growth_percent",
                labels={
                    "growth_percent": "Growth %",
                    "country": "Country"
                }
            )

            fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            show_chart(fig)

    st.markdown("### Country Trends Over Time")

    if country_trends_df.empty:
        st.info("country_trends.csv was not found or is empty.")
    else:
        country_options = sorted(country_trends_df["country"].dropna().unique())

        default_countries = countries_df.head(5)["country"].tolist() if not countries_df.empty else []
        default_countries = [c for c in default_countries if c in country_options]

        selected_countries = st.multiselect(
            "Select countries to compare",
            country_options,
            default=default_countries
        )

        filtered_country_trends = country_trends_df[
            country_trends_df["country"].isin(selected_countries)
        ]

        fig = px.line(
            filtered_country_trends,
            x="year",
            y="total_patents",
            color="country",
            markers=True,
            labels={
                "year": "Year",
                "total_patents": "Patents",
                "country": "Country"
            }
        )

        fig.update_traces(line=dict(width=3))
        show_chart(fig)


# technology field analysis showing largest fields, sector share, growth, and trends over time
with tab4:
    st.subheader("Technology Trends")

    st.caption("WIPO technology categories are used to compare the largest fields, sector shares, and recent growth patterns.")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Largest Technology Fields")

        if technology_totals_df.empty:
            show_missing_file("technology_totals.csv was not found. Run the WIPO technology report cell first.")
        else:
            fig = px.bar(
                technology_totals_df.head(15).sort_values("total_patents"),
                x="total_patents",
                y="wipo_field_title",
                orientation="h",
                color="wipo_sector_title" if "wipo_sector_title" in technology_totals_df.columns else None,
                text="total_patents",
                labels={
                    "total_patents": "Patents",
                    "wipo_field_title": "Technology field",
                    "wipo_sector_title": "Sector"
                }
            )

            fig.update_traces(texttemplate="%{text:,}", textposition="outside")
            show_chart(fig)

    with c2:
        st.markdown("### Technology Sector Share")

        if technology_sector_share_df.empty:
            show_missing_file("technology_sector_share.csv was not found. Run the WIPO technology report cell first.")
        else:
            fig = px.pie(
                technology_sector_share_df,
                names="wipo_sector_title",
                values="total_patents",
                hole=0.45
            )

            show_chart(fig)

    st.write("---")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Fastest-Growing Technology Fields")

        if technology_growth_df.empty:
            show_missing_file("technology_growth.csv was not found. Run the WIPO technology report cell first.")
        else:
            fig = px.bar(
                technology_growth_df.head(12).sort_values("growth_percent"),
                x="growth_percent",
                y="wipo_field_title",
                orientation="h",
                color="wipo_sector_title" if "wipo_sector_title" in technology_growth_df.columns else None,
                text="growth_percent",
                labels={
                    "growth_percent": "Growth %",
                    "wipo_field_title": "Technology field",
                    "wipo_sector_title": "Sector"
                }
            )

            fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            show_chart(fig)

    with c2:
        st.markdown("### Technology Trend Over Time")

        if technology_trends_df.empty:
            show_missing_file("technology_trends.csv was not found. Run the WIPO technology report cell first.")
        else:
            technology_options = technology_totals_df.head(8)["wipo_field_title"].tolist() if not technology_totals_df.empty else []

            technology_options = [
                tech for tech in technology_options
                if tech in technology_trends_df["wipo_field_title"].unique()
            ]

            selected_technologies = st.multiselect(
                "Select technology fields",
                sorted(technology_trends_df["wipo_field_title"].dropna().unique()),
                default=technology_options
            )

            filtered_technology = technology_trends_df[
                technology_trends_df["wipo_field_title"].isin(selected_technologies)
            ]

            fig = px.line(
                filtered_technology,
                x="year",
                y="total_patents",
                color="wipo_field_title",
                markers=True,
                labels={
                    "year": "Year",
                    "total_patents": "Patents",
                    "wipo_field_title": "Technology field"
                }
            )

            fig.update_traces(line=dict(width=3))
            show_chart(fig)


# patent complexity analysis
with tab5:
    st.subheader("Patent Complexity")

    st.caption("Complexity is estimated using the number of figures and drawing sheets available for each patent.")

    if complexity_by_year_df.empty:
        st.info("complexity_by_year.csv was not found. Run the complexity-by-year report cell first.")
    else:
        c1, c2 = st.columns(2)

        with c1:
            st.markdown("### Average Complexity Over Time")

            fig = px.line(
                complexity_by_year_df,
                x="year",
                y="avg_complexity_score",
                markers=True,
                labels={
                    "year": "Year",
                    "avg_complexity_score": "Average complexity score"
                }
            )

            fig.update_traces(line=dict(width=3))
            show_chart(fig)

        with c2:
            st.markdown("### High-Complexity Patent Share")

            fig = px.area(
                complexity_by_year_df,
                x="year",
                y="high_complexity_share",
                labels={
                    "year": "Year",
                    "high_complexity_share": "High-complexity patents (%)"
                }
            )

            show_chart(fig)

        latest_complexity = complexity_by_year_df.sort_values("year").iloc[-1]

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "Latest Avg Figures",
                f"{latest_complexity['avg_figures']:.2f}"
            )

        with c2:
            st.metric(
                "Latest Avg Sheets",
                f"{latest_complexity['avg_sheets']:.2f}"
            )

        with c3:
            st.metric(
                "High Complexity Share",
                f"{latest_complexity['high_complexity_share']:.2f}%"
            )

        st.success(
            "The complexity section highlights whether patents are becoming more visually detailed over time."
        )

    st.write("---")

    if most_complex_patents_df.empty:
        st.info("most_complex_patents.csv was not found. Run the most-complex-patents report cell first.")
    else:
        st.markdown("### Most Complex Individual Patents")

        display_cols = [
            "patent_id",
            "title",
            "year",
            "num_figures",
            "num_sheets",
            "complexity_score"
        ]

        available_cols = [
            col for col in display_cols
            if col in most_complex_patents_df.columns
        ]

        st.dataframe(
            most_complex_patents_df[available_cols].head(20),
            use_container_width=True
        )

        top_complex = most_complex_patents_df.sort_values(
            "complexity_score",
            ascending=False
        ).iloc[0]

        st.info(
            f"Highest complexity score in this output: {top_complex['complexity_score']:.0f}."
        )


# basic charts for companies, inventors, countries, and patent trends
with tab6:
    st.subheader("Core Charts")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Top Companies")

        if companies_df.empty:
            st.info("Company data was not found.")
        else:
            fig = px.bar(
                companies_df.head(10).sort_values("total_patents"),
                x="total_patents",
                y="name",
                orientation="h",
                text="total_patents",
                labels={
                    "name": "Company",
                    "total_patents": "Patents"
                }
            )

            fig.update_traces(texttemplate="%{text:,}", textposition="outside")
            show_chart(fig)

    with c2:
        st.markdown("### Top Inventors")

        if inventors_df.empty:
            st.info("Inventor data was not found.")
        else:
            fig = px.bar(
                inventors_df.head(10).sort_values("total_patents"),
                x="total_patents",
                y="name",
                orientation="h",
                text="total_patents",
                labels={
                    "name": "Inventor",
                    "total_patents": "Patents"
                }
            )

            fig.update_traces(texttemplate="%{text:,}", textposition="outside")
            show_chart(fig)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Top Countries")

        if countries_df.empty:
            st.info("Country data was not found.")
        else:
            fig = px.bar(
                countries_df.head(10).sort_values("total_patents"),
                x="total_patents",
                y="country",
                orientation="h",
                text="total_patents",
                labels={
                    "country": "Country",
                    "total_patents": "Patents"
                }
            )

            fig.update_traces(texttemplate="%{text:,}", textposition="outside")
            show_chart(fig)

    with c2:
        st.markdown("### Patent Trend Over Time")

        if patent_trends_df.empty:
            st.info("Patent trend data was not found.")
        else:
            fig = px.area(
                patent_trends_df,
                x="year",
                y="total_patents",
                labels={
                    "year": "Year",
                    "total_patents": "Patents"
                }
            )

            show_chart(fig)


# data tables 
with tab7:
    st.subheader("Data Tables")

    with st.expander("Top companies"):
        st.dataframe(companies_df, use_container_width=True)

    with st.expander("Top inventors"):
        st.dataframe(inventors_df, use_container_width=True)

    with st.expander("Top countries"):
        st.dataframe(countries_df, use_container_width=True)

    with st.expander("Patent trends"):
        st.dataframe(patent_trends_df, use_container_width=True)

    with st.expander("Country trends"):
        st.dataframe(country_trends_df, use_container_width=True)

    with st.expander("Technology trends"):
        if technology_trends_df.empty:
            st.info("technology_trends.csv was not found.")
        else:
            st.dataframe(technology_trends_df, use_container_width=True)

    with st.expander("Technology growth"):
        if technology_growth_df.empty:
            st.info("technology_growth.csv was not found.")
        else:
            st.dataframe(technology_growth_df, use_container_width=True)

    with st.expander("Complexity by year"):
        if complexity_by_year_df.empty:
            st.info("complexity_by_year.csv was not found.")
        else:
            st.dataframe(complexity_by_year_df, use_container_width=True)

    with st.expander("Most complex patents"):
        if most_complex_patents_df.empty:
            st.info("most_complex_patents.csv was not found.")
        else:
            st.dataframe(most_complex_patents_df, use_container_width=True)
