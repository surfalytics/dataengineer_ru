{% macro sum_two_values(x, y) -%}
select {{ x + y }}
{%- endmacro %}
