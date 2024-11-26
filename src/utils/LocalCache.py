import time

# 初始化本地缓存字典
cache = {}

# 缓存数据
def set(key, value, ttl=60):
    """
    设置缓存数据
    :param key: 缓存的键
    :param value: 缓存的值
    :param ttl: 有效时间（秒）
    """
    cache[key] = {
        "value": value,
        "timestamp": time.time(),  # 当前时间戳
        "ttl": ttl
    }
    print(f"已缓存{ttl}:{key}-{value}")
    return True

# 获取缓存数据
def get(key):
    """
    获取缓存数据，如果过期则返回 None
    :param key: 缓存的键
    :return: 缓存的值或 None
    """
    print(f"获取缓存key{key}")
    if key in cache:
        entry = cache[key]
        current_time = time.time()
        # 检查是否过期，ttl < 0 表示永久缓存
        if entry["ttl"] < 0 or current_time - entry["timestamp"] <= entry["ttl"]:
            print(f"拿到缓存cache{cache}")
            return entry["value"]
        else:
            # 删除过期数据
            del cache[key]
    return None

# 清理过期缓存
def clean():
    """
    清理所有过期的缓存条目
    """
    current_time = time.time()
    keys_to_delete = [key for key, entry in cache.items() 
                      if entry["ttl"] >= 0 and current_time - entry["timestamp"] > entry["ttl"]]
    for key in keys_to_delete:
        del cache[key]
        return True
