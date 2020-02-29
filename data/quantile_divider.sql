-- SQLite
-- SQL Queries to create quantile column for each of the nutrient factors

select max(case when rownum*1.0/numrows <= 0.33 then calories end) as percentile_33th
from (select calories,
             row_number() over (order by calories) as rownum,
             count(*) over (partition by NULL) as numrows
      from recipes
      where calories is not null
     ) recipes;
