from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import re
import aiohttp

@register("helloworld", "YourName", "一个简单的 Hello World 插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
                
    async def send_to_hentai_assistant(self, url):
        api_url = f"http://10.0.0.3:5001/api/download?url={url}"
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 202:
                    data = await response.json()
                    return True, data
                else:
                    logger.error(f"Failed to fetch data from {api_url}, status code: {response.status}")
                    return False, response.status

    @filter.event_message_type(filter.EventMessageType.PRIVATE_MESSAGE)
    async def on_private_message(self, event: AstrMessageEvent):
        message_str = event.message_str # 获取消息的纯文本内容
        pattern = r"^https://e.hentai\.org/g/\d+/[a-zA-Z0-9]+/$"
        if re.fullmatch(pattern, message_str):
            result = await self.send_to_hentai_assistant(url=message_str.strip(" "))
            if result[0] == True:
                yield event.plain_result(f"收到了 {result[1]['message']} 这样的信息，看起来推送成功了呢。") # 调用异步方法发送请求到 hentai 助手
            elif result[0] == False:
                yield event.plain_result(f"返回了 {result[1]} 这样的错误代码，看起来推送失败了呢。")
    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
