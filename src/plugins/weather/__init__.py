from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command
from nonebot.rule import to_me
from nonebot.adapters import Message
from nonebot.params import CommandArg
# from fastapi import FastAPI
import httpx
from functools import lru_cache
# from src.plugins.weather.NowWeatherResponse import WeatherResponse, Refer
from ..weather.NowWeatherResponse import WeatherResponse
from ..weather.LocationResponse import LocationResponse
from .config import Config
import redis

__plugin_meta__ = PluginMetadata(
    name="weather",
    description="使用和风天气接口查询天气",
    usage="帮助用户了解天气状况",
    config=Config,
)

config = get_plugin_config(Config)

rc = redis.Redis(host=config.redis_host, port=config.redis_port, decode_responses=True)

# 实时天气接口
NOW_WEATHER_URL: str = "https://devapi.qweather.com/v7/weather/now"

# 城市搜索接口
LOCATION_SEARCH_URL: str = "https://geoapi.qweather.com/v2/city/lookup"

ERROR_MESSAGE: str = "😯天气服务出错了，请晚点再尝试"

weather = on_command("天气", rule=to_me(), priority=10, block=True)

@weather.handle()
# 定义协程函数 handle_function，传入一个类型为Message的参数
async def handle_function(args: Message = CommandArg()):
    # 提取参数纯文本作为地名，并判断是否有效
    # 调用 extract_plain_text() 方法获取值，并将其赋值给 location 变量
    # 如果返回值为真值（如非空字符串），则执行 if 语句的代码块
    if location := args.extract_plain_text():
        try:
            async with httpx.AsyncClient() as client:
                location_id = await get_location_id(client, location)
                if location_id is None:
                    await weather.finish("请尝试输入正确的市级城市名称或者反馈问题")
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
            await weather.finish(ERROR_MESSAGE)
    else:
        await weather.finish("请输入地名，例如：\n@bot 天气 北京")

# 搜索城市获取id
async def get_location_id(client: httpx.AsyncClient, location: str):
        cache_suffix = "_id"
        if location_id := rc.get(location + cache_suffix):
            return location_id
        else:
            try:
                response = await client.get(LOCATION_SEARCH_URL, params = {
                    "key": config.weather_api_key,
                    "location": location,
                })
                print(f"[和风天气-城市搜索]响应数据：{response.text}")
                # 使用 Pydantic 模型直接解析 JSON 数据
                location_response = LocationResponse.parse_raw(response.text)
                location_id = location_response.location[0].id
                rc.set(location + cache_suffix, location_id)
                return location_id
            except Exception as e:
                print(f"[和风天气-城市搜索]request fail \n{e}")
                await weather.finish(ERROR_MESSAGE)

# 获取天气数据
async def get_weather_info(client: httpx.AsyncClient, location_id: str):
    if response_txt := rc.get(location_id):
        weather_response = WeatherResponse.parse_raw(response_txt)
        return weather_response
    else:
        try:
            response = await client.get(NOW_WEATHER_URL, params = {
                "key": config.weather_api_key,
                "location": location_id
            })
            print(f"[和风天气-实时天气]响应数据：{response.text}")
            rc.set(location_id, response.text, 3600)
            weather_response = WeatherResponse.parse_raw(response.text)
            return weather_response
        except Exception as e:
            print(f"[和风天气-实时天气]request fail \n{e}")
            await weather.finish(ERROR_MESSAGE)
