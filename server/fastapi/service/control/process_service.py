from utils.connect import create_connection
from utils.response import success_response, error_response
from utils.status_code import *
from utils.common import format_datetime, is_valid_process_keyword
from datetime import datetime

# 添加单个进程
def add_single_process(process_name: str):
    process_name = process_name.strip().lower()
    if not process_name:
        return error_response("进程名称不能为空", HTTP_BAD_REQUEST)

    if not is_valid_process_keyword(process_name):
        return error_response("不允许添加完整路径或非法进程名称，请仅填写进程名或关键词", HTTP_BAD_REQUEST)

    try:
        conn = create_connection()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = "insert into process_control (process_name, status, create_time) values (%s, %s, %s)"
        cursor.execute(sql, (process_name, 1, now))
        conn.commit()
        return success_response(message="添加成功")
    except Exception as e:
        return error_response("数据库操作失败", HTTP_INTERNAL_SERVER_ERROR, str(e))
    finally:
        cursor.close()
        conn.close()

# 批量添加
def add_batch_process(process_list: list):
    if not isinstance(process_list, list):
        return error_response("进程列表格式错误，应为数组", HTTP_BAD_REQUEST)

    # 去重 & 清洗
    cleaned = list(set([
        p.strip().lower() for p in process_list
        if isinstance(p, str) and p.strip() and is_valid_process_keyword(p.strip())
    ]))

    if not cleaned:
        return error_response("无有效进程，格式应为进程名或关键词，不能是路径", HTTP_BAD_REQUEST)

    try:
        conn = create_connection()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = "insert into process_control (process_name, status, create_time) values (%s, %s, %s)"
        values = [(name, 1, now) for name in cleaned]
        cursor.executemany(sql, values)
        conn.commit()
        return success_response(message="批量添加成功", data={"新增数量": len(values)})
    except Exception as e:
        return error_response("数据库操作失败", HTTP_INTERNAL_SERVER_ERROR, str(e))
    finally:
        cursor.close()
        conn.close()


# 删除单个
def delete_single_process(rule_id: int):
    if not isinstance(rule_id, int) or rule_id <= 0:
        return error_response("无效的规则 ID", HTTP_BAD_REQUEST)

    try:
        conn = create_connection()
        cursor = conn.cursor()
        sql = "delete from process_control where id = %s"
        cursor.execute(sql, (rule_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return error_response("规则不存在或已删除", HTTP_NOT_FOUND)
        return success_response(message="删除成功")
    except Exception as e:
        return error_response("数据库删除失败", HTTP_INTERNAL_SERVER_ERROR, str(e))
    finally:
        cursor.close()
        conn.close()


# 批量删除
def delete_batch_process(ids: list):
    if not isinstance(ids, list) or not all(isinstance(i, int) and i > 0 for i in ids):
        return error_response("ID 列表格式错误", HTTP_BAD_REQUEST)

    try:
        conn = create_connection()
        cursor = conn.cursor()
        sql = "delete from process_control where id in (%s)" % ','.join(['%s'] * len(ids))
        cursor.execute(sql, ids)
        conn.commit()
        return success_response(message="批量删除成功", data={"删除数量": cursor.rowcount})
    except Exception as e:
        return error_response("数据库删除失败", HTTP_INTERNAL_SERVER_ERROR, str(e))
    finally:
        cursor.close()
        conn.close()


# 启用/禁用
def toggle_process_status(rule_id: int, status: int ):
    if not isinstance(rule_id, int) or rule_id <= 0:
        return error_response("无效的规则 ID", HTTP_BAD_REQUEST)
    if status not in [0, 1]:
        return error_response("状态值只能为 0 或 1", HTTP_BAD_REQUEST)

    try:
        conn = create_connection()
        cursor = conn.cursor()
        sql = "update process_control set status = %s where id = %s"
        cursor.execute(sql, (status, rule_id))
        conn.commit()
        if cursor.rowcount == 0:
            return error_response("规则不存在", HTTP_NOT_FOUND)
        return success_response(message="状态更新成功")
    except Exception as e:
        return error_response("数据库更新失败", HTTP_INTERNAL_SERVER_ERROR, str(e))
    finally:
        cursor.close()
        conn.close()


# 获取进程列表
def get_process_list():
    try:
        conn = create_connection()
        cursor = conn.cursor()
        sql = "select id, process_name, status, create_time from process_control order by create_time desc"
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            row["create_time"] = format_datetime(row["create_time"])
        return success_response(data=rows)
    except Exception as e:
        return error_response("查询失败", HTTP_INTERNAL_SERVER_ERROR, str(e))
    finally:
        cursor.close()
        conn.close()
