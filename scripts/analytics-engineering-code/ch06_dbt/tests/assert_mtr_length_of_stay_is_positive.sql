-- tests/assert_mtr_length_of_stay_is_positive.sql
select sk_customer, sk_channel,
       sum(mtr_length_of_stay_minutes) as mtr_length_of_stay_minutes
from {{ ref('fct_visit_history') }}
group by 1, 2
having mtr_length_of_stay_minutes < 0
