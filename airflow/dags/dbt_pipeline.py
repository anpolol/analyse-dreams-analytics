from airflow.decorators import dag
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime
import csv

DBT_DIR = "/usr/local/airflow/dbt_project"
CSV_PATH = "/usr/local/airflow/include/ad_costs.csv"

def load_ad_costs():
    hook = PostgresHook(postgres_conn_id="postgres_dreams")
    conn = hook.get_conn()
    cur = conn.cursor()

    # читаем CSV
    with open(CSV_PATH) as f:
        rows = list(csv.DictReader(f))

    # собираем множество дат из файла — их и будем перезаливать
    dates = {r["date"] for r in rows}

    # idempotent: удаляем строки за эти даты, потом вставляем свежие
    for d in dates:
        cur.execute("DELETE FROM raw.ad_costs WHERE date = %s", (d,))

    for r in rows:
        cur.execute(
            "INSERT INTO raw.ad_costs (date, utm_source, cost, clicks) "
            "VALUES (%s, %s, %s, %s)",
            (r["date"], r["utm_source"], r["cost"], r["clicks"]),
        )

    conn.commit()
    cur.close()
    conn.close()

@dag(
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["dbt"],
)
def dbt_pipeline():
    load_costs = PythonOperator(
        task_id="load_ad_costs",
        python_callable=load_ad_costs,
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {DBT_DIR} && dbt run --profiles-dir {DBT_DIR}",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_DIR} && dbt test --profiles-dir {DBT_DIR}",
    )

    load_costs >> dbt_run >> dbt_test

dbt_pipeline()