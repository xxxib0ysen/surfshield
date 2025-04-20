import json
from datetime import datetime
from typing import Optional
from utils.connect import create_connection


# 写入系统操作日志
def write_log(admin_id: Optional[int], ip_address: str, module: str, action: str, detail: dict):
    try:
        if admin_id is None:
            return

        conn = create_connection()
        cursor = conn.cursor()
        sql = """
            insert into log_operation (created_at, admin_id, ip_address, module, action, detail)
            values (%s, %s, %s, %s, %s, %s)
        """
        print(f"Writing log: {admin_id}, {ip_address}, {module}, {action}, {detail}")
        cursor.execute(sql, (
            datetime.now(),
            admin_id,
            ip_address,
            module,
            action,
            json.dumps(detail, ensure_ascii=False)
        ))
        conn.commit()
        print(f"Log written successfully: {admin_id}")
    except Exception as e:
        print(f"[日志写入失败] {e}")
