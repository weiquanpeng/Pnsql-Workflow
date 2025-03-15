import subprocess
import paramiko
import sys

def safe_execute_local_cmd(cmd_array):
    # 获取虚拟环境的 Python 解释器路径
    python_path = sys.executable
    # 检查 cmd_array 的第一个元素是否为 'python'
    if cmd_array[0] == 'python':
        cmd_array[0] = python_path
    child = subprocess.Popen(cmd_array, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = child.communicate()
    if child.poll() != 0:
        message = '{}\n{}\n{}'.format(cmd_array, stdout, stderr)
        raise Exception(message)
    return stdout

def simple_execute_ssh_cmd(cmd, host, port, user, password, timeout=60):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port, user, password, timeout=10)
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    status = stdout.channel.recv_exit_status()
    return status, stdout.readlines(), stderr.readlines()