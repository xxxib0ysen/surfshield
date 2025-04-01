import pymysql
from utils.connect import create_connection
from utils.common import validate_url, format_datetime
from utils.response import success_response, error_response
from model.control.website_model import WebsiteRuleCreate, WebsiteTypeCreate

# 检查类型是否存在
def is_valid_type(type_id):
    conn = create_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("select 1 from website_type where type_id = %s", (type_id,))
            return cursor.fetchone() is not None
    finally:
        conn.close()

# 获取网站类型列表
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
            rows = cursor.fetchall()
            for row in rows:
                row["last_modified"] = format_datetime(row["last_modified"])
            return rows
    finally:
        conn.close()

# 添加网站类型
def add_type(data: WebsiteTypeCreate):
    type_name = data.type_name
    status = data.status

    conn = create_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("insert into website_type (type_name, status) values (%s, %s)", (type_name, status))
            conn.commit()
        return success_response("网站类型添加成功")
    except pymysql.IntegrityError:
        return error_response("该网站类型已存在")
    except pymysql.MySQLError as e:
        return error_response(f"数据库错误: {str(e)}")
    finally:
        conn.close()

# 删除网站类型及其规则
def delete_website_type(type_id):
    conn = create_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("delete from website_control where type_id = %s", (type_id,))
            cursor.execute("delete from website_type_update where type_id = %s", (type_id,))
            cursor.execute("delete from website_type where type_id = %s", (type_id,))
            conn.commit()
        return success_response("网站类型及其规则已删除")
    finally:
        conn.close()

# 修改网站类型状态
def update_type_status(type_id, status):
    conn = create_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("update website_type set status = %s where type_id = %s", (status, type_id))
            conn.commit()
        return success_response("类型状态已更新")
    finally:
        conn.close()

# 添加网站访问规则
def add_website_rule(data: WebsiteRuleCreate):
    website_url = data.website_url.strip()
    type_id = data.type_id
    status = data.status

    if not website_url or not type_id:
        return error_response("网址和类型ID不能为空")

    if not is_valid_type(type_id):
        return error_response(f"无效的类型 ID: {type_id}")

    urls = [url.strip() for url in website_url.splitlines() if url.strip()]

    for url in urls:
        if not validate_url(url) and "*" not in url and ">" not in url:
            return error_response(f"无效的网址格式: {url}")

    conn = create_connection()
    try:
        with conn.cursor() as cursor:
            for url in urls:
                cursor.execute("select 1 from website_control where website_url = %s and type_id = %s", (url, type_id))
                if cursor.fetchone():
                    return error_response(f"网址已存在: {url}")

            cursor.executemany(
                "insert into website_control (website_url, type_id, status) values (%s, %s, %s)",
                [(url, type_id, status) for url in urls]
            )

            cursor.execute(
                "insert into website_type_update (type_id) values (%s) on duplicate key update last_modified = now()",
                (type_id,)
            )
            conn.commit()

        return success_response("规则添加成功")
    finally:
        conn.close()

# 删除网站规则
def delete_website_rule(website_id):
    conn = create_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("delete from website_control where website_id = %s", (website_id,))
            conn.commit()
        return success_response("规则已删除")
    finally:
        conn.close()

# 修改网站规则状态
def update_website_status(website_id, status):
    conn = create_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("update website_control set status = %s where website_id = %s", (status, website_id))
            conn.commit()
        return success_response("规则状态已更新")
    finally:
        conn.close()

# 获取所有网站规则
def get_website_rule():
    conn = create_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                select wc.website_id, wc.website_url, wt.type_name, wc.status, wc.createdon
                from website_control wc
                join website_type wt on wc.type_id = wt.type_id
                order by wc.createdon desc
            """)
            rows = cursor.fetchall()
            return rows
    finally:
        conn.close()

# 分组返回规则
def get_website_rule_grouped():
    conn = create_connection()
    grouped = {}
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                select wc.website_id, wc.website_url, wt.type_name, wc.status, wc.createdon
                from website_control wc
                join website_type wt on wc.type_id = wt.type_id
                order by wt.type_name, wc.createdon desc
            """)
            for row in cursor.fetchall():
                row["createdon"] = format_datetime(row["createdon"])
                grouped.setdefault(row["type_name"], []).append(row)
        return grouped
    finally:
        conn.close()
