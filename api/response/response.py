from fastapi import FastAPI
from fastapi.responses import JSONResponse

# 定义响应结构体
class Response:
    def __init__(self, code: int, data: dict, msg: str):
        self.code = code
        self.data = data
        self.msg = msg

    def to_dict(self):
        return {
            "code": self.code,
            "data": self.data,
            "msg": self.msg
        }

# 定义状态码常量
ERROR = 800
SUCCESS = 200

# 通用结果返回函数
def result(code: int, data: dict, msg: str) -> JSONResponse:
    resp = Response(code, data, msg)
    return JSONResponse(content=resp.to_dict())

# 成功响应函数
def ok() -> JSONResponse:
    return result(SUCCESS, {}, "操作成功")

def ok_with_message(message: str) -> JSONResponse:
    return result(SUCCESS, {}, message)

def ok_with_data(data: dict) -> JSONResponse:
    return result(SUCCESS, data, "成功")

def ok_with_detailed(data: dict, message: str) -> JSONResponse:
    return result(SUCCESS, data, message)

# 失败响应函数
def fail() -> JSONResponse:
    return result(ERROR, {}, "操作失败")

def fail_with_message(message: str) -> JSONResponse:
    return result(ERROR, {}, message)

def fail_with_data(e: int, data: dict, message: str) -> JSONResponse:
    return result(e, data, message)

def fail_with_decide(data: dict, message: str) -> JSONResponse:
    return result(ERROR, data, message)
