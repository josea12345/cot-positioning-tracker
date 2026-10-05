-- 01_current_positioning.sql — latest COT snapshot: who is positioned how
SELECT
    w.commodity,
    w.report_date,
    w.open_interest,
    (w.mmoney_long - w.mmoney_short)                          AS mmoney_net,
    ROUND(100.0 * (w.mmoney_long - w.mmoney_short) / w.open_interest, 1)
                                                             AS mmoney_net_pct_oi,
    (w.prod_long - w.prod_short)                              AS commercial_net,
    ROUND(p.close / 100.0, 2)                                 AS futures_usd_bu
FROM cot_weekly w
LEFT JOIN price_at_report p USING (report_date, commodity)
WHERE w.report_date = (SELECT MAX(report_date) FROM cot_weekly)
ORDER BY w.commodity;
