-- Total number of patents
SELECT COUNT(1) AS total_patents
FROM patents;

-- Patent trends over time
-- Output file: patent_trends.csv
SELECT
    year,
    COUNT(1) AS total_patents
FROM patents
WHERE year IS NOT NULL
GROUP BY year
ORDER BY year;

-- Top countries by patent output
-- Output file: top_countries.csv
SELECT
    i.country,
    COUNT(DISTINCT r.patent_id) AS total_patents
FROM relationships r
JOIN inventors i
    ON r.inventor_id = i.inventor_id
WHERE i.country IS NOT NULL
  AND i.country != 'Unknown'
GROUP BY i.country
ORDER BY total_patents DESC
LIMIT 10;

-- Top inventors by patent output
-- Output file: top_inventors.csv
SELECT
    i.name,
    t.total_patents
FROM (
    SELECT
        inventor_id,
        COUNT(DISTINCT patent_id) AS total_patents
    FROM relationships
    WHERE inventor_id IS NOT NULL
    GROUP BY inventor_id
    ORDER BY total_patents DESC
    LIMIT 10
) t
JOIN inventors i
    ON t.inventor_id = i.inventor_id
ORDER BY t.total_patents DESC;

-- Top companies by patent output
-- Output file: top_companies.csv
SELECT
    c.name,
    t.total_patents
FROM (
    SELECT
        company_id,
        COUNT(DISTINCT patent_id) AS total_patents
    FROM relationships
    WHERE company_id IS NOT NULL
    GROUP BY company_id
    ORDER BY total_patents DESC
    LIMIT 10
) t
JOIN companies c
    ON t.company_id = c.company_id
ORDER BY t.total_patents DESC;

-- Joined sample showing patents with inventors and companies
SELECT
    p.patent_id,
    p.title,
    i.name AS inventor_name,
    c.name AS company_name,
    p.year
FROM relationships r
JOIN patents p
    ON r.patent_id = p.patent_id
LEFT JOIN inventors i
    ON r.inventor_id = i.inventor_id
LEFT JOIN companies c
    ON r.company_id = c.company_id
LIMIT 20;

-- CTE query for inventor patent counts
WITH inventor_counts AS (
    SELECT
        inventor_id,
        COUNT(DISTINCT patent_id) AS total_patents
    FROM relationships
    WHERE inventor_id IS NOT NULL
    GROUP BY inventor_id
)
SELECT
    i.name,
    ic.total_patents
FROM inventor_counts ic
JOIN inventors i
    ON ic.inventor_id = i.inventor_id
ORDER BY ic.total_patents DESC
LIMIT 10;

-- Ranking query for inventors
SELECT
    name,
    total_patents,
    RANK() OVER (ORDER BY total_patents DESC) AS inventor_rank
FROM (
    SELECT
        i.name,
        COUNT(DISTINCT r.patent_id) AS total_patents
    FROM relationships r
    JOIN inventors i
        ON r.inventor_id = i.inventor_id
    WHERE i.name IS NOT NULL
    GROUP BY i.name
)
ORDER BY inventor_rank
LIMIT 10;

-- Country trends over time
-- Output file: country_trends.csv
SELECT
    i.country,
    p.year,
    COUNT(DISTINCT r.patent_id) AS total_patents
FROM relationships r
JOIN inventors i
    ON r.inventor_id = i.inventor_id
JOIN patents p
    ON r.patent_id = p.patent_id
WHERE i.country IS NOT NULL
  AND i.country != 'Unknown'
  AND p.year IS NOT NULL
GROUP BY i.country, p.year
ORDER BY p.year, total_patents DESC;

-- Fastest-growing countries
-- Compares the latest 5 years against the previous 5 years
WITH latest AS (
    SELECT MAX(year) AS latest_year
    FROM patents
    WHERE year IS NOT NULL
),
country_yearly AS (
    SELECT
        i.country,
        p.year,
        COUNT(DISTINCT r.patent_id) AS total_patents
    FROM relationships r
    JOIN inventors i
        ON r.inventor_id = i.inventor_id
    JOIN patents p
        ON r.patent_id = p.patent_id
    WHERE i.country IS NOT NULL
      AND i.country != 'Unknown'
      AND p.year IS NOT NULL
    GROUP BY i.country, p.year
),
recent AS (
    SELECT
        country,
        SUM(total_patents) AS recent_patents
    FROM country_yearly, latest
    WHERE year BETWEEN latest_year - 4 AND latest_year
    GROUP BY country
),
previous AS (
    SELECT
        country,
        SUM(total_patents) AS previous_patents
    FROM country_yearly, latest
    WHERE year BETWEEN latest_year - 9 AND latest_year - 5
    GROUP BY country
)
SELECT
    r.country,
    r.recent_patents,
    p.previous_patents,
    ROUND(
        100.0 * (r.recent_patents - p.previous_patents) / p.previous_patents,
        2
    ) AS growth_percent
FROM recent r
JOIN previous p
    ON r.country = p.country
WHERE p.previous_patents > 0
ORDER BY growth_percent DESC
LIMIT 10;

-- Company power and innovation concentration
-- Shows each top company plus cumulative share of all patents
WITH total AS (
    SELECT COUNT(1) AS total_patents
    FROM patents
),
company_counts AS (
    SELECT
        c.name,
        COUNT(DISTINCT r.patent_id) AS total_patents
    FROM relationships r
    JOIN companies c
        ON r.company_id = c.company_id
    WHERE c.name IS NOT NULL
    GROUP BY c.name
),
ranked_companies AS (
    SELECT
        name,
        total_patents,
        SUM(total_patents) OVER (
            ORDER BY total_patents DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_patents
    FROM company_counts
    ORDER BY total_patents DESC
    LIMIT 20
)
SELECT
    rc.name,
    rc.total_patents,
    rc.cumulative_patents,
    ROUND(100.0 * rc.cumulative_patents / t.total_patents, 2) AS cumulative_share
FROM ranked_companies rc
CROSS JOIN total t
ORDER BY rc.total_patents DESC;

-- top 10 company share of all patents
WITH total AS (
    SELECT COUNT(1) AS total_patents
    FROM patents
),
top_companies AS (
    SELECT
        company_id,
        COUNT(DISTINCT patent_id) AS total_patents
    FROM relationships
    WHERE company_id IS NOT NULL
    GROUP BY company_id
    ORDER BY total_patents DESC
    LIMIT 10
)
SELECT
    SUM(tc.total_patents) AS top_10_company_patents,
    t.total_patents,
    ROUND(100.0 * SUM(tc.total_patents) / t.total_patents, 2) AS top_10_company_share
FROM top_companies tc
CROSS JOIN total t;

--  Technology trends over time
-- Output file: technology_trends.csv
SELECT
    p.year,
    w.wipo_sector_title,
    w.wipo_field_title,
    COUNT(DISTINCT w.patent_id) AS total_patents
FROM wipo_technology w
JOIN patents p
    ON w.patent_id = p.patent_id
WHERE p.year IS NOT NULL
  AND w.wipo_field_title IS NOT NULL
  AND w.wipo_field_title != 'Unknown'
GROUP BY p.year, w.wipo_sector_title, w.wipo_field_title
ORDER BY p.year, total_patents DESC;

-- Largest technology fields overall
-- Output file: technology_totals.csv
SELECT
    w.wipo_sector_title,
    w.wipo_field_title,
    COUNT(DISTINCT w.patent_id) AS total_patents
FROM wipo_technology w
WHERE w.wipo_field_title IS NOT NULL
  AND w.wipo_field_title != 'Unknown'
GROUP BY w.wipo_sector_title, w.wipo_field_title
ORDER BY total_patents DESC;

-- Fastest-growing technology fields
-- Output file: technology_growth.csv
WITH latest AS (
    SELECT MAX(year) AS latest_year
    FROM patents
    WHERE year IS NOT NULL
),
technology_yearly AS (
    SELECT
        p.year,
        w.wipo_sector_title,
        w.wipo_field_title,
        COUNT(DISTINCT w.patent_id) AS total_patents
    FROM wipo_technology w
    JOIN patents p
        ON w.patent_id = p.patent_id
    WHERE p.year IS NOT NULL
      AND w.wipo_field_title IS NOT NULL
      AND w.wipo_field_title != 'Unknown'
    GROUP BY p.year, w.wipo_sector_title, w.wipo_field_title
),
recent AS (
    SELECT
        wipo_sector_title,
        wipo_field_title,
        SUM(total_patents) AS recent_patents
    FROM technology_yearly, latest
    WHERE year BETWEEN latest_year - 4 AND latest_year
    GROUP BY wipo_sector_title, wipo_field_title
),
previous AS (
    SELECT
        wipo_sector_title,
        wipo_field_title,
        SUM(total_patents) AS previous_patents
    FROM technology_yearly, latest
    WHERE year BETWEEN latest_year - 9 AND latest_year - 5
    GROUP BY wipo_sector_title, wipo_field_title
)
SELECT
    r.wipo_sector_title,
    r.wipo_field_title,
    r.recent_patents,
    p.previous_patents,
    ROUND(
        100.0 * (r.recent_patents - p.previous_patents) / p.previous_patents,
        2
    ) AS growth_percent
FROM recent r
JOIN previous p
    ON r.wipo_sector_title = p.wipo_sector_title
   AND r.wipo_field_title = p.wipo_field_title
WHERE p.previous_patents >= 50
ORDER BY growth_percent DESC;

--Technology sector share
-- Output file: technology_sector_share.csv
SELECT
    wipo_sector_title,
    COUNT(DISTINCT patent_id) AS total_patents
FROM wipo_technology
WHERE wipo_sector_title IS NOT NULL
  AND wipo_sector_title != 'Unknown'
GROUP BY wipo_sector_title
ORDER BY total_patents DESC;

-- patent complexity by year
-- Output file: complexity_by_year.csv
SELECT
    p.year,
    COUNT(*) AS patents_with_figure_data,
    ROUND(AVG(f.num_figures), 2) AS avg_figures,
    ROUND(AVG(f.num_sheets), 2) AS avg_sheets,
    ROUND(AVG(f.num_figures + f.num_sheets), 2) AS avg_complexity_score,
    ROUND(
        100.0 * SUM(
            CASE
                WHEN (f.num_figures + f.num_sheets) >= 20 THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS high_complexity_share
FROM figures f
JOIN patents p
    ON f.patent_id = p.patent_id
WHERE p.year IS NOT NULL
GROUP BY p.year
ORDER BY p.year;

--  Most complex patents
-- Output file: most_complex_patents.csv
SELECT
    p.patent_id,
    p.title,
    p.year,
    f.num_figures,
    f.num_sheets,
    (f.num_figures + f.num_sheets) AS complexity_score
FROM figures f
JOIN patents p
    ON f.patent_id = p.patent_id
ORDER BY complexity_score DESC
LIMIT 100;

--  Most common CPC subclasses
SELECT
    c.cpc_subclass,
    COALESCE(t.title, 'Unknown') AS cpc_title,
    COUNT(DISTINCT c.patent_id) AS total_patents
FROM cpc_at_issue c
LEFT JOIN cpc_title t
    ON c.cpc_subclass = t.cpc_subclass
WHERE c.cpc_subclass IS NOT NULL
GROUP BY c.cpc_subclass, cpc_title
ORDER BY total_patents DESC
LIMIT 20;

--  Most cited patents
SELECT
    p.patent_id,
    p.title,
    p.year,
    ci.total_citations
FROM patent_citation_influence ci
JOIN patents p
    ON ci.patent_id = p.patent_id
ORDER BY ci.total_citations DESC
LIMIT 20;

--  Patents with the most references made
SELECT
    p.patent_id,
    p.title,
    p.year,
    cr.total_references_made
FROM citing_patent_references cr
JOIN patents p
    ON cr.patent_id = p.patent_id
ORDER BY cr.total_references_made DESC
LIMIT 20;

--  Citation categories
SELECT
    citation_category,
    total_citations
FROM citation_category_counts
ORDER BY total_citations DESC;

--PCT( Patent Cooperation Treaty) filing countries
SELECT
    filed_country,
    COUNT(DISTINCT patent_id) AS total_patents
FROM pct_data
WHERE filed_country IS NOT NULL
  AND filed_country != 'Unknown'
GROUP BY filed_country
ORDER BY total_patents DESC
LIMIT 20;

-- Government-linked patents by agency
SELECT
    fedagency_name,
    COUNT(DISTINCT patent_id) AS total_patents
FROM gov_interest_org
WHERE fedagency_name IS NOT NULL
  AND fedagency_name != 'Unknown'
GROUP BY fedagency_name
ORDER BY total_patents DESC
LIMIT 20;

--  Government-linked patents by level one organization
SELECT
    level_one,
    COUNT(DISTINCT patent_id) AS total_patents
FROM gov_interest_org
WHERE level_one IS NOT NULL
  AND level_one != 'Unknown'
GROUP BY level_one
ORDER BY total_patents DESC
LIMIT 20;
