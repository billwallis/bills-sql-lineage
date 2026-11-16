with

table_1(x) as (select 1 from database.schema.table_1),
table_2(y) as (select 2 from schema.table_2),
table_3(z) as (select 3 from table_3)

select *
from
    table_1,
    table_2,
    table_3
