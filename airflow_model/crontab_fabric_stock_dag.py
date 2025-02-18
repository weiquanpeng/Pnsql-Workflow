from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
from model import setup_variables, done_for_task

# ================= 配置基础参数 =================

default_args = {
    'owner': 'airflow',
    'start_date': datetime.now() - timedelta(days=1),
}

dag = DAG(
    dag_id='crontab_fabric_stock_dag',
    default_args=default_args,
    description='爬虫流程',
    schedule_interval='10 15 * * *',
    catchup=False
)

# ================= 定义所有任务 =================

# 1. 初始化审批变量 -> submitWork
init_variables = PythonOperator(
    task_id='submitWork',
    python_callable=setup_variables,
    op_kwargs={'run_id': '{{ run_id }}'},
    dag=dag  # 显式绑定到dag对象
)

# 3. 任务执行 -> prodExecution
execute_process = BashOperator(
    task_id='prodExecution',
    bash_command='/data/Airflow/airflow_venv/bin/python /root/airflow/dags/utils/my_fabric_task.py',
    dag=dag
)

# 4. 任务执行 -> prodExecution
mysql_execution = BashOperator(
    task_id='mysqlExecution',
    bash_command='mysql pnsql_workflow -e "truncate p_follow_stock; insert into p_follow_stock (stock_ticker,stock_name) select distinct f0,f20 from p_stock"',
    dag=dag
)

# 5. 完成通知 -> doneExecution
done_notify = PythonOperator(
    task_id='doneExecution',
    python_callable=done_for_task,
    op_kwargs={'run_id': '{{ run_id }}'},
    dag=dag
)

# ============== 定义任务依赖关系 ==============

init_variables >> execute_process >> mysql_execution >> done_notify