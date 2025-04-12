from utils.common import format_time_fields, format_time_in_rows
from utils.connect import create_connection
from utils.response import success_response, error_response
from model.terminal_admin.group_model import GroupCreateUpdate
from datetime import datetime

from utils.status_code import *


# 递归获取所有子group_id
def get_all_descendant_ids(group_id, all_groups):
    ids = [group_id]
    for g in all_groups:
        if g['parent_id'] == group_id:
            ids.extend(get_all_descendant_ids(g['group_id'], all_groups))
    return ids

# 获取分组树结构
def get_group_tree_service():
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("select * from sys_group order by parent_id, group_id")
        rows = cursor.fetchall()
        rows = format_time_in_rows(rows, ['createdon', 'updatedon'])

        group_map = {row['group_id']: {**row, 'children': []} for row in rows}
        root = []

        for row in rows:
            node = group_map[row['group_id']]
            parent_id = row['parent_id']
            if parent_id in group_map:
                group_map[parent_id]['children'].append(node)
            else:
                root.append(node)

        return success_response(data=root, code=HTTP_OK)
    except Exception as e:
        return error_response(message=f"获取分组失败：{str(e)}", code=HTTP_INTERNAL_SERVER_ERROR)

# 新增分组
def add_group_service(group: GroupCreateUpdate):
    try:
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("select * from sys_group where group_name = %s and parent_id = %s", 
                       (group.group_name, group.parent_id))
        if cursor.fetchone():
            return error_response(message="该父分组下已存在同名分组",code=HTTP_BAD_REQUEST)

        sql = "insert into sys_group (group_name, parent_id, description) values (%s, %s, %s)"
        cursor.execute(sql, (group.group_name, group.parent_id, group.description))
        conn.commit()
        return success_response(message="分组添加成功", code=HTTP_CREATED)
    except Exception as e:
        return error_response(message=f"添加分组失败：{str(e)}", code=HTTP_INTERNAL_SERVER_ERROR)


# 编辑分组
def update_group_service(group_id: int, group: GroupCreateUpdate):
    try:
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("select * from sys_group where group_id = %s", (group_id,))
        if not cursor.fetchone():
            return error_response(message="分组不存在", code=HTTP_NOT_FOUND)

        if group_id == group.parent_id:
            return error_response(message="分组不能设置为自己的父级", code=HTTP_BAD_REQUEST)

        if group.parent_id not in (0, None):
            cursor.execute("select * from sys_group where group_id = %s", (group.parent_id,))
            if not cursor.fetchone():
                return error_response(message="父分组不存在", code=HTTP_BAD_REQUEST)

        cursor.execute("""
            select * from sys_group 
            where group_name = %s and parent_id = %s and group_id != %s
        """, (group.group_name, group.parent_id, group_id))
        if cursor.fetchone():
            return error_response(message="该父分组下已存在同名分组", code=HTTP_BAD_REQUEST)

        sql = "update sys_group set group_name=%s, parent_id=%s, description=%s where group_id=%s"
        cursor.execute(sql, (group.group_name, group.parent_id, group.description, group_id))
        conn.commit()
        return success_response(message="分组更新成功", code=HTTP_OK)
    except Exception as e:
        return error_response(message=f"更新分组失败：{str(e)}", code=HTTP_INTERNAL_SERVER_ERROR)


# 删除分组及其子分组和终端
def delete_group_service(group_id: int):
    try:
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("select * from sys_group where group_id = %s", (group_id,))
        if not cursor.fetchone():
            return error_response(message="分组不存在", code=HTTP_NOT_FOUND)

        cursor.execute("select group_id, parent_id from sys_group")
        all_groups = cursor.fetchall()
        ids_to_delete = get_all_descendant_ids(group_id, all_groups)
        format_strings = ','.join(['%s'] * len(ids_to_delete))

        cursor.execute(f"delete from sys_terminal where group_id in ({format_strings})", tuple(ids_to_delete))
        cursor.execute(f"delete from sys_group where group_id in ({format_strings})", tuple(ids_to_delete))

        conn.commit()
        return success_response(
            message=f"成功删除分组及其子分组（共 {len(ids_to_delete)} 个）及相关终端",
            code=HTTP_OK
        )
    except Exception as e:
        return error_response(message=f"删除分组失败：{str(e)}", code=HTTP_INTERNAL_SERVER_ERROR)


# 获取分组详情
def get_group_detail_service(group_id: int):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("select * from sys_group where group_id = %s", (group_id,))
        row = cursor.fetchone()
        if not row:
            return error_response(message="分组不存在", code=HTTP_NOT_FOUND)
        row = format_time_fields(row, ['createdon', 'updatedon'])
        return success_response(data=row, code=HTTP_OK)
    except Exception as e:
        return error_response(message=f"获取分组详情失败：{str(e)}", code=HTTP_INTERNAL_SERVER_ERROR)


# 创建默认分组
def create_default_group_service():
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("select count(*) as cnt from sys_group")
        count = cursor.fetchone()['cnt']
        if count == 0:
            cursor.execute("insert into sys_group (group_name, parent_id, description) values ('默认分组', 0, '系统自动创建')")
            conn.commit()
    except Exception:
        pass
