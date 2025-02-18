from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.python import PythonSensor  # 关键修改
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
from model import setup_variables, done_for_task, check_approval  # 导入检查函数

default_args = {
    'owner': 'airflow',
    'start_date': datetime.now() - timedelta(days=1),
}

dag = DAG(
    dag_id='fabric_stock_dag',
    default_args=default_args,
    description='爬虫流程',
    schedule_interval=None,
    catchup=False,
)

# 1. 初始化审批变量
init_variables = PythonOperator(
    task_id='submitWork',
    python_callable=setup_variables,
    op_kwargs={'run_id': '{{ run_id }}', 'task_types': ['ownerApproval']},
    dag=dag
)

# 2. 使用传感器等待审批（关键修改）
wait_approval = PythonSensor(
    task_id='ownerApproval',
    python_callable=check_approval,  # 直接使用检查函数
    op_kwargs={'task_id': 'ownerApproval', 'run_id': '{{ run_id }}'},
    poke_interval=1,  # 每秒检查一次
    mode='reschedule',  # 核心优化：释放工作线程
    dag=dag
)

# 3. 正式执行
execute_process = BashOperator(
    task_id='prodExecution',
    bash_command='/data/Airflow/airflow_venv/bin/python /root/airflow/dags/utils/my_fabric_task.py',
    dag=dag
)

# 4. 完成通知
done_notify = PythonOperator(
    task_id='doneExecution',
    python_callable=done_for_task,
    op_kwargs={'run_id': '{{ run_id }}'},
    dag=dag
)

init_variables >> wait_approval >> execute_process >> done_notify