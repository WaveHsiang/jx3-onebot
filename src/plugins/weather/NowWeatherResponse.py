from pydantic import BaseModel
from typing import List

# [详见文档](https://dev.qweather.com/docs/api/weather/weather-now/#%E8%BF%94%E5%9B%9E%E6%95%B0%E6%8D%AE)
class Now(BaseModel):
    obsTime: str # 数据观测时间
    temp: str # 温度，默认单位：摄氏度
    feelsLike: str # 体感温度，默认单位：摄氏度
    icon: str # 天气状况的图标代码
    text: str # 天气状况的文字描述，包括阴晴雨雪等天气状态的描述
    wind360: str # 风向360角度
    windDir: str # 风向
    windScale: str # 风力等级
    windSpeed: str # 风速，公里/小时
    humidity: str # 相对湿度，百分比数值
    precip: str # 过去1小时降水量，默认单位：毫米
    pressure: str # 大气压强，默认单位：百帕
    vis: str # 能见度，默认单位：公里
    cloud: str # 云量，百分比数值。可能为空
    dew: str # 露点温度。可能为空

class Refer(BaseModel):
    sources: List[str] # 原始数据来源，或数据源说明，可能为空
    license: List[str] # 数据许可或版权声明，可能为空

class WeatherResponse(BaseModel):
    code: str # 状态码，详见https://dev.qweather.com/docs/resource/status-code/
    updateTime: str # 当前API的最近更新时间
    fxLink: str # 当前数据的响应式页面，便于嵌入网站或应用
    now: Now # 天气数据
    refer: Refer # 数据来源申明
