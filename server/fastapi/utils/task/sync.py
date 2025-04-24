from service.log.sync_ import sync_process_behavior_from_redis, sync_web_behavior_from_redis, \
    sync_search_behavior_from_redis

def sync_all_behavior_from_redis():
    print("开始同步终端行为日志...")
    sync_process_behavior_from_redis()
    sync_web_behavior_from_redis()
    sync_search_behavior_from_redis()
    print("所有行为日志同步完成")
