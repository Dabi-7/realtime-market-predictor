from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

# defualt arguments
default_args = {
    'owner': 'carbonX390',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

with DAG(
    'market_prediction_pipeline',
    default_args=default_args,
    description='Automated Market Scraper and AI Trainer',
    schedule_interval='@daily', # Runs every night at midnight
    start_date=days_ago(1),
    catchup=False,
    tags=['mlops', 'category_a'],
) as dag:

    #runnig data ingestion file
    # ---------------------------------------------------------
    task_ingestion = BashOperator(
        task_id='run_ingestion_scripts',
        bash_command='cd /opt/airflow && ./run_ingestion.sh ',
    )

    #runing my_version_code.py
    # ---------------------------------------------------------
    task_training = BashOperator(
        task_id='process_and_train_models',
        bash_command='cd /opt/airflow && python my_version_code.py ',
    )

    #github ci/cd trigger
    # ---------------------------------------------------------
    task_trigger_cicd = BashOperator(
        task_id='trigger_deployment',
        bash_command='echo "New models trained. In a real environment, this triggers git push to deploy." ',
    )

    #Pipeline Flow
    task_ingestion >> task_training >> task_trigger_cicd
