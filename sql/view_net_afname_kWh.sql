-- this view computes the amount of electricity (in kWh) used between
-- the current and previous time step. Note that it assumes electricity
-- use to be constant between two time intervals.
create or replace view net_afname_kWh as
select 
    from_unixtime(t1.this_time) AS `date_time`,
    date(from_unixtime(t1.this_time)) AS `day`,
    month(from_unixtime(t1.this_time)) AS `month`,
    year(from_unixtime(t1.this_time)) AS `year`,
    -- the value -2.77e07 converts Joule to kWh
    t1.net_afname_watt * seconds * 2.7777777777778E-7 as net_afname_kWh
from (
	select 
      `time`as this_time,
--      lag(`time`) over (order by `time`) as time_prev,
      `time` - lag(`time`) over (order by `time`) as seconds,
      net_afname * 1000 as net_afname_watt
	from
	   p1_readouts pr
	) t1
;
