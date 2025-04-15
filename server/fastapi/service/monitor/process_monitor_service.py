import json
from utils.connect import redis_client
from utils.response import success_response, error_response
from utils.status_code import HTTP_OK, HTTP_INTERNAL_SERVER_ERROR

# 写入 Redis
def save_process_to_redis(terminal_id: int, process_list: list):
    try:
        key = f"terminal:process:{terminal_id}"
        redis_client.set(key, json.dumps(process_list), ex=60)
        return success_response(message="进程信息写入成功", code=HTTP_OK)
    except Exception as e:
        return error_response(message=f"写入 Redis 失败: {str(e)}", code=HTTP_INTERNAL_SERVER_ERROR)

# 获取进程信息
def get_process_from_redis(terminal_id: int = None):
    try:
        process_list = []

        # 查询指定终端
        if terminal_id:
            key = f"terminal:process:{terminal_id}"
            value = redis_client.get(key)
            if value:
                data = json.loads(value)
                for item in data:
                    item["terminal_id"] = terminal_id
                process_list.extend(data)

        # 查询所有终端
        else:
            keys = redis_client.keys("terminal:process:*")
            for key in keys:
                tid = int(key.split(":")[-1])
                value = redis_client.get(key)
                if value:
                    data = json.loads(value)
                    for item in data:
                        item["terminal_id"] = tid
                    process_list.extend(data)

        return success_response(data=process_list, code=HTTP_OK)

    except Exception as e:
        return error_response(message=f"获取进程数据失败：{str(e)}", code=HTTP_INTERNAL_SERVER_ERROR)

# 终止进程
def send_kill_command(terminal_id: int, pid: int) -> bool:
    try:
        channel = f"terminal:cmd:{terminal_id}"
        command = {
            "action": "kill_process",
            "pid": pid
        }
        redis_client.publish(channel, json.dumps(command))
        return True
    except Exception as e:
        print(f"终止失败: {e}")
        return False