from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime
import time

def setup_variables(run_id):
    """初始化任务审批状态变量"""
    Variable.set(f"approved_start_task_{run_id}", "False")
    Variable.set(f"approved_process_task_{run_id}", "False")

def wait_for_approval(task_id, run_id, **kwargs):
    """等待任务审批"""
    approved_var = f"approved_{task_id}_{run_id}"
    while not Variable.get(approved_var, default_var="False") == "True":
        print(f"Task {task_id} (run_id {run_id}) is waiting for approval...")
        time.sleep(1)
    print(f"Task {task_id} approved.")

def execute_task(task_id, run_id, **kwargs):
    """执行任务"""
    print(f"Executing task: {task_id} (run_id {run_id})")

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 10, 24),
}

dag = DAG(
    dag_id='multi_step_dag',
    default_args=default_args,
    description='A simple DAG with two tasks that require approval without explicit start approval task',
    schedule_interval=None,
    catchup=False,
)

init_variables = PythonOperator(
    task_id='提交工单',
    python_callable=setup_variables,
    op_kwargs={'run_id': '{{ run_id }}'},
    dag=dag
)

wait_start_task = PythonOperator(
    task_id='ownerApproval',
    python_callable=wait_for_approval,
    op_kwargs={'task_id': 'start_task', 'run_id': '{{ run_id }}'},
    dag=dag
)

execute_start_task = PythonOperator(
    task_id='Sit执行',
    python_callable=execute_task,
    op_kwargs={'task_id': 'start_task', 'run_id': '{{ run_id }}'},
    dag=dag
)

wait_process_task = PythonOperator(
    task_id='再次确认',
    python_callable=wait_for_approval,
    op_kwargs={'task_id': 'process_task', 'run_id': '{{ run_id }}'},
    dag=dag
)

execute_process_task = PythonOperator(
    task_id='Prod执行',
    python_callable=execute_task,
    op_kwargs={'task_id': 'process_task', 'run_id': '{{ run_id }}'},
    dag=dag
)

# Define dependencies
init_variables >> wait_start_task >> execute_start_task >> wait_process_task >> execute_process_task