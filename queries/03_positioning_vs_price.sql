-- 03_positioning_vs_price.sql — weekly managed-money net vs futures price.
-- The dataset behind the charts: does price follow the funds?
WITH weekly AS (
    SELECT
        w.report_date,
        w.commodity,
        w.mmoney_long - w.mmoney_short AS mmoney_net,
        p.close                        AS friday_close
    FROM cot_weekly w
    JOIN price_at_report p USING (report_date, commodity)
)
SELECT
    commodity,
    report_date,
    mmoney_net,
    ROUND(friday_close / 100.0, 2) AS price_usd_bu,
    ROUND(100.0 * (friday_close - LAG(friday_close)
        OVER (PARTITION BY commodity ORDER BY report_date))
        / LAG(friday_close) OVER (PARTITION BY commodity ORDER BY report_date), 2)
        AS weekly_price_pct_change,
    (mmoney_net - LAG(mmoney_net)
        OVER (PARTITION BY commodity ORDER BY report_date)) AS weekly_net_change
FROM weekly
ORDER BY commodity, report_date;
