import pymysql
import redis

from utils.config import Config


# mysql
def create_connection():
    try:
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor
        )
        print("数据库连接成功")
        return conn
    except pymysql.MySQLError as e:
        print(f"数据库连接失败: {str(e)}")
        raise


# redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
