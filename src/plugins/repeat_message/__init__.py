from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from .config import Config
from nonebot import on_message
from nonebot.adapters.onebot.v11 import GROUP, GroupMessageEvent, Message, MessageSegment
from nonebot.log import logger
import httpx
import os

__plugin_meta__ = PluginMetadata(
    name="repeat_message",
    description="当一句话被重复发送时，bot也主动发送这句话",
    usage="让机器人活跃群内气氛",
    config=Config,
)

repeat = on_message(priority=100, block=True, permission=GROUP)

config = get_plugin_config(Config)

# 缓存结构用json表示为{group_id:MessageCache}
last_message_cache = {}

# 缓存结构用json表示为{group_id:message_str}
replied_cache = {}

@repeat.handle()
async def handle_function(event: GroupMessageEvent):
    # 获取群号
    group_id = event.group_id
    # 获取消息内容
    message = event.get_message()
    # 用来判断 & 打印 消息富文本
    message_content = message.to_rich_text()
    if message[0].get("type") == "image":
        message_content = message[0].data.get("filename")
        # 用于相同表情包以不同后缀出现的情况下区分
        name, ext = os.path.splitext(message_content)
        message_content = name
        file = event.get_message()[0].get("data").get("file")
        async with httpx.AsyncClient() as client:
            response = await client.get(file)
            message = Message([
                MessageSegment.image(response.content)
            ])
    # 获取发送者id
    user_id = event.user_id
    """
    根据提供的逻辑处理消息
    """
    # 1. 有没有消息记录
    if group_id in last_message_cache:
        last_user_id, last_message = last_message_cache[group_id]
        # 2. 本次和上次发言是否相同
        if last_user_id != user_id and last_message == message_content:
            # 3. 有没有已经读过
            if group_id in replied_cache:
                replied_message = replied_cache[group_id]
                # 如果缓存 message 和当前 message 不相等，则发送
                if replied_message != message:
                    # 4. 调用 send 方法传入 message，并更新到 replied_cache
                    logger.debug(f"repeat 发送 {message}")
                    replied_cache[group_id] = message
                    await repeat.send(message)
            else:
                # 4. 调用 send 方法传入 message，并更新到 replied_cache
                logger.debug(f"norepeat 发送 {message}")
                replied_cache[group_id] = message_content
                await repeat.send(message)
    # 5. 在合适的时候将当前 group_id 和 message 缓存到 last_message_cache
    logger.debug(f"消息缓存 last-{last_message_cache.get(group_id)}")
    last_message_cache[group_id] = (user_id, message_content)
    logger.debug(f"消息缓存 current-{last_message_cache.get(group_id)}")
    logger.debug(f"复读缓存 repeat-{replied_cache.get(group_id)}")