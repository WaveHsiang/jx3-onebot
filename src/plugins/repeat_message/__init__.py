from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from .config import Config
from nonebot import on_message
from nonebot.adapters.onebot.v11 import GROUP, GroupMessageEvent
from nonebot.params import Matcher

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
async def handle_function(matcher: Matcher, event: GroupMessageEvent):
    # 获取群号
    group_id = event.group_id
    # 获取消息内容
    message = event.get_message()
    # 获取发送者id
    user_id = event.user_id
    print(f"群聊{group_id}用户{user_id}发送了{message}")
    """
    根据提供的逻辑处理消息
    """
    # 1. 有没有消息记录
    if group_id in last_message_cache:
        last_user_id, last_message = last_message_cache[group_id]
        # 2. 本次和上次发言是否相同
        if last_user_id != user_id and last_message == message:
            # 3. 有没有已经读过
            if group_id in replied_cache:
                replied_message = replied_cache[group_id]
                # 如果缓存 message 和当前 message 不相等，则发送
                if replied_message != message:
                    # 4. 调用 send 方法传入 message，并更新到 replied_cache
                    print(f"repeat 发送 {message}")
                    await repeat.send(message)
                    replied_cache[group_id] = message
            else:
                # 4. 调用 send 方法传入 message，并更新到 replied_cache
                print(f"norepeat 发送 {message}")
                await repeat.send(message)
                replied_cache[group_id] = message
    # 5. 在合适的时候将当前 group_id 和 message 缓存到 last_message_cache
    print(f"打印0-消息缓存{last_message_cache.get(group_id)}")
    last_message_cache[group_id] = (user_id, message)
    print(f"打印1-消息缓存{last_message_cache.get(group_id)}")
    print(f"打印2-复读缓存{replied_cache.get(group_id)}")