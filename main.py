from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

@register("helloworld", "YourName", "一个简单的 Hello World 插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
        
    async def send_to_hentai_assistant(self, url):
        api_url = f"http://10.0.0.3:5001/api/download?url={url}"
        async with self.context.http_client.get(api_url) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                logger.error(f"Failed to fetch data from {api_url}, status code: {response.status}")
                return None

    @filter.command("url")
    async def url(self, event: AstrMessageEvent):
        """这是一个 hello world 指令""" # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
        user_name = event.get_sender_name()
        message_str = event.message_str # 用户发的纯文本消息字符串
        message_chain = event.get_messages() # 用户所发的消息的消息链 # from astrbot.api.message_components import *
        logger.info(message_chain)
        if "hentai.org" in message_str:
            result = await self.send_to_hentai_assistant(url=message_str)
            if result != None:
                yield event.plain_result(result) # 调用异步方法发送请求到 hentai 助手
            else:
                yield event.plain_result("解析错误")
        
    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
