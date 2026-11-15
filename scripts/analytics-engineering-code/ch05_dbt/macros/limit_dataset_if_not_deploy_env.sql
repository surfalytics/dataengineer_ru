{# Вне среды deploy берём только последние nbr_months_of_data месяцев #}
{% macro limit_dataset_if_not_deploy_env(column_name, nbr_months_of_data) %}
{% if target.name != 'deploy' %}
where {{ column_name }} > current_date - interval {{ nbr_months_of_data }} month
{% endif %}
{% endmacro %}
