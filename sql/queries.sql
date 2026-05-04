--query for top inventors 
SELECT i.name, COUNT(DISTINCT r.patent_id) AS total_patents
FROM relationships r
JOIN inventors i ON r.inventor_id = i.inventor_id
GROUP BY i.inventor_id
ORDER BY total_patents DESC
LIMIT 10;


-- query for top companies
SELECT c.name, COUNT(DISTINCT r.patent_id) AS total_patents
FROM relationships r
JOIN companies c ON r.company_id = c.company_id
WHERE r.company_id IS NOT NULL
GROUP BY c.company_id
ORDER BY total_patents DESC
LIMIT 10;


-- query for top countries by number of inventors
SELECT country, COUNT(1) AS total
FROM inventors
WHERE country IS NOT NULL
  AND country != 'Unknown'
GROUP BY country
ORDER BY total DESC
LIMIT 10;


-- query for number of patents per year
SELECT year, COUNT(1) AS total_patents
FROM patents
WHERE year IS NOT NULL
GROUP BY year
ORDER BY year;


-- Join querry to get patent details along with inventor and company information
SELECT 
    p.patent_id,
    p.title,
    p.year,
    i.name AS inventor_name,
    i.country AS inventor_country,
    c.name AS company_name
FROM relationships r
JOIN patents p ON r.patent_id = p.patent_id
LEFT JOIN inventors i ON r.inventor_id = i.inventor_id
LEFT JOIN companies c ON r.company_id = c.company_id
LIMIT 20;


--CTE query for top inventors by number of patents
WITH inventor_counts AS (
    SELECT inventor_id, COUNT(DISTINCT patent_id) AS total_patents
    FROM relationships
    GROUP BY inventor_id
)
SELECT i.name, ic.total_patents
FROM inventor_counts ic
JOIN inventors i ON ic.inventor_id = i.inventor_id
ORDER BY ic.total_patents DESC
LIMIT 10;


--ranking query for inventors by number of patents
SELECT 
    name,
    total_patents,
    RANK() OVER (ORDER BY total_patents DESC) AS inventor_rank
FROM (
    SELECT i.name, COUNT(DISTINCT r.patent_id) AS total_patents
    FROM relationships r
    JOIN inventors i ON r.inventor_id = i.inventor_id
    GROUP BY i.name
)
LIMIT 10;