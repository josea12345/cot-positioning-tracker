-- 02_biggest_position_swings.sql — largest weekly changes in managed-money
-- net positioning. Big swings = funds rushing in or running for the exit.
WITH nets AS (
    SELECT
        commodity,
        report_date,
        mmoney_long - mmoney_short AS mmoney_net
    FROM cot_weekly
)
SELECT
    commodity,
    report_date,
    mmoney_net,
    mmoney_net - LAG(mmoney_net) OVER (PARTITION BY commodity ORDER BY report_date)
        AS weekly_change_contracts
FROM nets
ORDER BY ABS(mmoney_net - LAG(mmoney_net)
    OVER (PARTITION BY commodity ORDER BY report_date)) DESC
LIMIT 20;
