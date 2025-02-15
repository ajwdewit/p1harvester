-- This view computes the gas usage in m3 between the current time
-- and previous time step.
create or replace view gas_usage_m3 as
select
    from_unixtime(t1.this_time) AS `date_time`,
    date(from_unixtime(t1.this_time)) AS `day`,
    month(from_unixtime(t1.this_time)) AS `month`,
    year(from_unixtime(t1.this_time)) AS `year`,
    t1.gas_usage_m3
from (
select
	`time`as this_time,
--	lag(`time`) over (order by `time`) as time_prev,
 	gas_meter_reading - lag(gas_meter_reading) over (order by `time`) as gas_usage_m3
from p1_readouts pr
) t1
;
