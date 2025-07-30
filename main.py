from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger, AstrBotConfig
import re
import aiohttp

@register("MafuyuCommands", "Chock", "为真冬ちゃん扩展一些功能", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        self.api_url = f"{self.config.get('hentai_assistant_api_url')}"
        logger.info(f"MafuyuCommands 初始化完毕")
        logger.info(f"Hentai Assistant API URL: {self.api_url}")

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
                
    async def send_to_hentai_assistant(self, url):
        download_api = f"{self.api_url}/api/download?url={url}"
        async with aiohttp.ClientSession() as session:
            async with session.get(download_api) as response:
                if response.status == 202:
                    data = await response.json()
                    return True, data
                else:
                    logger.error(f"Failed to fetch data from {download_api}, status code: {response.status}")
                    return False, response.status
    
    @filter.event_message_type(filter.EventMessageType.ALL)
    async def on_all_message(self, event: AstrMessageEvent):
        message_obj= event.message_obj.message # AstrBot 解析出来的消息链内容
        logger.info(message_obj)
        message_str = event.message_str # 获取消息的纯文本内容
        if message_str == "dl" or message_str == "download":
            for item in message_obj[0].chain:
                if item == 'Plain':
                    message_str = item.text
        pattern = r"https://e.hentai\.org/g/\d+/[a-zA-Z0-9]+/"
        match = re.search(pattern, message_str)
        if match: # 直接处理包含画廊链接的消息
            result = await self.send_to_hentai_assistant(url=match.group(0))
            if result[0] == True:
                yield event.plain_result(f"收到了 {result[1]['message']} 这样的信息，看起来推送成功了呢。") # 调用异步方法发送请求到 hentai 助手
            elif result[0] == False:
                yield event.plain_result(f"返回了 {result[1]} 这样的错误代码，看起来推送失败了呢。")

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""


