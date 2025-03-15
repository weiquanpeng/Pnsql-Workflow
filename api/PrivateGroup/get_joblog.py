from fastapi import APIRouter, Request
from initialize.init_config import config
import os
import util.response as response

router = APIRouter()
CHUNK_SIZE = 1024 * 1024
@router.post("/read_log")
async def read_log(request: Request):
    body = await request.json()
    job_id = body.get("jobid")
    file_name = f"{job_id}.log"
    file_path = os.path.join(config['app']['job_log'], file_name)
    try:
        def read_in_chunks(file_path):
            with open(file_path, 'r') as file:
                while True:
                    chunk = file.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    yield chunk
        log_data = "".join(read_in_chunks(file_path))
        return response.ok_with_data(log_data)
    except FileNotFoundError:
        return response.ok_with_data({"log_data": "暂无日志..."})
    except Exception as e:
        return response.fail_with_message(f"读取日志文件时发生错误: {str(e)}")
