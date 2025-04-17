import os
import shutil
import sqlite3
from datetime import datetime

# 定义浏览器默认路径
def get_browser_history_paths():
    user_dir = os.environ.get("USERPROFILE", "")
    local = os.path.join(user_dir, "AppData", "Local")
    roaming = os.path.join(user_dir, "AppData", "Roaming")

    return [
        # Chrome
        {
            "browser": "chrome",
            "path": os.path.join(local, "Google", "Chrome", "User Data", "Default", "History")
        },
        # Firefox
        {
            "browser": "firefox",
            "path": os.path.join(roaming, "Mozilla", "Firefox", "Profiles")
        },
        # Edge
        {
            "browser": "edge",
            "path": os.path.join(local, "Microsoft", "Edge", "User Data", "Default", "History")
        },
        # 360
        {
            "browser": "360",
            "path": os.path.join(local, "360Chrome", "Chrome", "User Data", "Default", "History")
        },
        # 百度
        {
            "browser": "baidu",
            "path": os.path.join(local, "baidu", "BaiduBrowser", "User Data", "Default", "History")
        },
    ]

# 读取 Chromium 内核浏览器的记录
def extract_chromium_history(db_path: str, browser: str, last_ts: float):
    result = []

    # 如果数据库文件不存在则跳过
    if not os.path.exists(db_path):
        return result

    # 拷贝一份防止数据库锁定
    temp_path = db_path + ".copy"
    try:
        shutil.copy2(db_path, temp_path)

        # 连接 SQLite 数据库
        conn = sqlite3.connect(temp_path)
        cursor = conn.cursor()

        # 查询最近访问记录
        sql = """
            select urls.url, urls.title, visits.visit_time
            from urls
            join visits on urls.id = visits.url
            where visits.visit_time > ?
            order by visits.visit_time desc
        """
        cursor.execute(sql, (last_ts,))
        rows = cursor.fetchall()

        # 解析记录
        for row in rows:
            url, title, visit_time = row
            timestamp = visit_time / 1000000 - 11644473600  # Chrome 时间戳转换
            visit_time_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
            result.append({
                "url": url,
                "title": title,
                "visit_time": visit_time_str,
                "timestamp": timestamp,
                "browser": browser
            })

    except Exception as e:
        print(f"[{browser}] 读取失败：{e}")
    finally:
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)  # 删除副本
        except:
            pass

    return result

# 读取 Firefox 历史记录
def extract_firefox_history(firefox_profile_dir: str, last_ts: float):
    result = []

    # 检查 Profiles 目录是否存在
    if not os.path.exists(firefox_profile_dir):
        return result

    # 遍历所有配置文件夹
    for folder in os.listdir(firefox_profile_dir):
        path = os.path.join(firefox_profile_dir, folder, "places.sqlite")
        if not os.path.exists(path):
            continue

        temp_path = path + ".copy"
        try:
            shutil.copy2(path, temp_path)

            conn = sqlite3.connect(temp_path)
            cursor = conn.cursor()

            # 查询最近访问记录
            sql = """
                select p.url, p.title, v.visit_date
                from moz_places p
                join moz_historyvisits v on p.id = v.place_id
                where v.visit_date > ?
                order by v.visit_date desc
            """
            cursor.execute(sql, (last_ts,))
            rows = cursor.fetchall()

            for row in rows:
                url, title, visit_date = row
                timestamp = visit_date / 1000000  # Firefox 纳秒 → 秒
                visit_time_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                result.append({
                    "url": url,
                    "title": title,
                    "visit_time": visit_time_str,
                    "timestamp": timestamp,
                    "browser": "firefox"
                })

        except Exception as e:
            print(f"[firefox] 读取失败：{e}")
        finally:
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except:
                pass

    return result

# 获取所有浏览器历史记录
def extract_all_browser_history(last_ts: float):
    all_records = []
    paths = get_browser_history_paths()

    for item in paths:
        browser = item["browser"]
        path = item["path"]

        # 处理 Firefox 独立函数
        if browser == "firefox":
            all_records.extend(extract_firefox_history(path, last_ts))
        else:
            all_records.extend(extract_chromium_history(path, browser, last_ts))

    return all_records
