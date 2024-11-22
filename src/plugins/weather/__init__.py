from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command
from nonebot.rule import to_me
from nonebot.adapters import Message
from nonebot.params import CommandArg
# from fastapi import FastAPI
import httpx
import json
from nonebot import logger
from functools import lru_cache
# from src.plugins.weather.NowWeatherResponse import Now, WeatherResponse, Refer
from ..weather.NowWeatherResponse import Now, WeatherResponse, Refer
from ..weather.LocationResponse import LocationResponse, Location, Refer
from .config import Config
import time

__plugin_meta__ = PluginMetadata(
    name="weather",
    description="",
    usage="",
    config=Config,
)

plugin_config = get_plugin_config(Config)

# 实时天气接口
NOW_WEATHER_URL: str = "https://devapi.qweather.com/v7/weather/now"

# 城市搜索接口
LOCATION_SEARCH_URL: str = "https://geoapi.qweather.com/v2/city/lookup"

# 初始化本地缓存字典
cache = {}

weather = on_command("天气", rule=to_me(), aliases={"查天气"}, priority=10, block=True)

@weather.handle()
# 定义协程函数 handle_function，传入一个类型为Message的参数
async def handle_function(args: Message = CommandArg()):
    # 提取参数纯文本作为地名，并判断是否有效
    # 调用 extract_plain_text() 方法获取值，并将其赋值给 location 变量
    # 如果返回值为真值（如非空字符串），则执行 if 语句的代码块
    if location := args.extract_plain_text():
        try:
            async with httpx.AsyncClient() as client:
                print(1)
                location_id = await get_location_id(client, location)
                print(2)
                weather_info = await get_weather_info(client, location_id)
                await weather.send(
f"""{location}
· 天    气 - {weather_info.now.text}
· 气    温 - {weather_info.now.temp}℃
· 体感温度 - {weather_info.now.feelsLike}℃
· 湿    度 - {weather_info.now.humidity}%
· 风    向 - {weather_info.now.windDir}
· 风    力 - {weather_info.now.windScale}级
· 风    速 - {weather_info.now.windSpeed}公里/小时  
· 气    压 - {weather_info.now.pressure}hPa
· 能 见 度 - {weather_info.now.vis}公里
· 降 水 量 - {weather_info.now.precip}毫米(过去1小时)

感谢和风天气，{weather_info.refer.sources[0]}提供支持"""
                )
        except Exception as e:
            print(f"request weahter api fail \n{e}")
            await weather.finish("😯天气服务出错了，请晚点再尝试")
    else:
        await weather.finish("请输入地名，例如：\n@bot 天气 北京")

# 搜索城市获取id
async def get_location_id(client: httpx.AsyncClient, location: str):
        cache_suffix = "_id"
        if location_id := cache_get(location + cache_suffix):
            return location_id
        else:
            response = await client.get(LOCATION_SEARCH_URL, params = {
                "key": plugin_config.weather_api_key,
                "location": location,
            })
            # response_text = json.loads(response.text)
            print(f"[和风天气-城市搜索]响应数据：{response.text}")
            # 使用 Pydantic 模型直接解析 JSON 数据
            location_response = LocationResponse.parse_raw(response.text)
            location_id = location_response.location[0].id
            cache_set(location + cache_suffix, location_id, -1)
            return location_id


# 获取天气数据
async def get_weather_info(client: httpx.AsyncClient, location_id: str):
    if response_txt := cache_get(location_id):
        weather_response = WeatherResponse.parse_raw(response_txt)
        return weather_response
    else:
        response = await client.get(NOW_WEATHER_URL, params = {
            "key": plugin_config.weather_api_key,
            "location": location_id
        })
        # 看起来是写法错误，实际应该是response.text，写成了response.text()
        # response_txt = json.loads(response.text)
        print(f"[和风天气-实时天气]响应数据：{response.text}")
        cache_set(location_id, response.text, 3600)
        weather_response = WeatherResponse.parse_raw(response.text)
        return weather_response

# 缓存数据
def cache_set(key, value, ttl=60):
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

# 获取缓存数据
def cache_get(key):
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
def cache_clean():
    """
    清理所有过期的缓存条目
    """
    current_time = time.time()
    keys_to_delete = [key for key, entry in cache.items() 
                      if entry["ttl"] >= 0 and current_time - entry["timestamp"] > entry["ttl"]]
    for key in keys_to_delete:
        del cache[key]