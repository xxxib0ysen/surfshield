import pymysql
from utils.connect import create_connection
from utils.response import success_response, error_response
from utils.common import validate_url, format_datetime
from model.control.website_model import *

# 检查类型是否存在
def is_valid_type(type_id: int) -> bool:
    conn = create_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("select count(*) from website_type where type_id = %s", (type_id,))
            return cursor.fetchone()["count(*)"] > 0
    finally:
        conn.close()

# 更新类型更新时间
def update_type_last_modified(type_id: int):
    conn = create_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                insert into website_type_update (type_id, last_modified)
                values (%s, now())
                on duplicate key update last_modified = now()
            """, (type_id,))
            conn.commit()
    finally:
        conn.close()

# 获取所有网站类型
def get_website_type():
    conn = create_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                select wt.*, coalesce(wtu.last_modified, wt.createdon) as last_modified
                from website_type wt
                left join website_type_update wtu on wt.type_id = wtu.type_id
                order by wt.createdon desc
            """)
            types = cursor.fetchall()
            for t in types:
                t["last_modified"] = format_datetime(t["last_modified"])
        return success_response(types, "获取网站类型成功")
    finally:
        conn.close()

# 添加网站类型
def add_type(req: WebsiteTypeAddRequest):
    conn = create_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("insert into website_type (type_name, status) values (%s, %s)", (req.type_name, req.status))
            conn.commit()
        return success_response("网站类型添加成功")
    except pymysql.IntegrityError:
        return error_response("该网站类型已存在")
    finally:
        conn.close()

# 删除网站类型及其规则
def delete_website_type(type_id: int):
    if not is_valid_type(type_id):
        return error_response("网站类型不存在")
    conn = create_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("delete from website_control where type_id = %s", (type_id,))
            cursor.execute("delete from website_type_update where type_id = %s", (type_id,))
            cursor.execute("delete from website_type where type_id = %s", (type_id,))
            conn.commit()
        return success_response("网站类型及规则已删除")
    finally:
        conn.close()

# 修改网站类型状态
def update_type_status(type_id: int, status: int):
    if not is_valid_type(type_id):
        return error_response("网站类型不存在")
    conn = create_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("update website_type set status = %s where type_id = %s", (status, type_id))
            conn.commit()
        return success_response("状态更新成功")
    finally:
        conn.close()

# 添加网站访问规则
def add_website_rule(req: WebsiteRuleAddRequest):
    if not req.website_url or not req.type_id:
        return error_response("网址与类型不能为空")
    if not is_valid_type(req.type_id):
        return error_response("无效类型ID")

    urls = [url.strip() for url in req.website_url.splitlines() if url.strip()]
    for url in urls:
        url = url.lower()
        if not validate_url(url) and "*" not in url and ">" not in url:
            return error_response(f"无效网址格式: {url}")

    conn = create_connection()
    try:
        with conn.cursor() as cursor:
            sql = "insert into website_control (website_url, type_id, status) values (%s, %s, %s)"
            values = [(url, req.type_id, req.status) for url in urls]
            cursor.executemany(sql, values)
            conn.commit()
        update_type_last_modified(req.type_id)
        return success_response("规则添加成功")
    finally:
        conn.close()

# 删除网站规则
def delete_website_rule(website_id: int):
    conn = create_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("select type_id from website_control where website_id = %s", (website_id,))
            row = cursor.fetchone()
            if not row:
                return error_response("规则不存在")
            type_id = row["type_id"]
            cursor.execute("delete from website_control where website_id = %s", (website_id,))
            conn.commit()
        update_type_last_modified(type_id)
        return success_response("规则删除成功")
    finally:
        conn.close()

# 修改规则启用状态
def update_website_status(website_id: int, status: int):
    conn = create_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("select type_id from website_control where website_id = %s", (website_id,))
            row = cursor.fetchone()
            if not row:
                return error_response("规则不存在")
            type_id = row["type_id"]
            cursor.execute("update website_control set status = %s where website_id = %s", (status, website_id))
            conn.commit()
        update_type_last_modified(type_id)
        return success_response("规则状态更新成功")
    finally:
        conn.close()

# 获取所有网站规则，按类型分组
def get_rules_grouped_by_type():
    conn = create_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                select wt.type_id, wt.type_name, wt.status as type_status,
                       wc.website_id, wc.website_url, wc.status, wc.createdon
                from website_type wt
                left join website_control wc on wt.type_id = wc.type_id
                order by wt.type_id, wc.createdon desc
            """)
            rows = cursor.fetchall()
            result = {}
            for row in rows:
                tid = row["type_id"]
                if tid not in result:
                    result[tid] = {
                        "type_id": tid,
                        "type_name": row["type_name"],
                        "type_status": row["type_status"],
                        "rules": []
                    }
                if row["website_id"]:
                    result[tid]["rules"].append({
                        "website_id": row["website_id"],
                        "website_url": row["website_url"],
                        "status": row["status"],
                        "createdon": format_datetime(row["createdon"])
                    })
            return success_response(list(result.values()), "获取规则成功")
    finally:
        conn.close()
