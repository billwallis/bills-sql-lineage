with

used_cte(x) as (select 1 from database.schema.table),
dead_cte(y) as (select 2 from used_cte)

select * from used_cte
