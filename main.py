from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger, AstrBotConfig
from astrbot.api.message_components import Plain, Image, Reply
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
        
    def parse_message_chain(self, chain):
        # 用于存储提取的信息
        reply_image_url = None
        reply_text = None
        current_text = None
        # 遍历消息链
        for component in chain:
            if isinstance(component, Reply):
                # 处理 Reply 类型的消息段
                logger.info(f"Found Reply message with id: {component.id}")
                # 遍历 Reply 中的嵌套消息链
                for reply_component in component.chain:
                    if isinstance(reply_component, Image):
                        # 提取图片 URL
                        reply_image_url = reply_component.url
                        logger.info(f"Reply contains Image: {reply_image_url}")
                    elif isinstance(reply_component, Plain):
                        # 提取回复中的文本
                        reply_text = reply_component.text
                        logger.info(f"Reply contains Text: {reply_text}")
                # 也可以直接使用 Reply 的 message_str 获取纯文本
                if component.message_str:
                    reply_text = component.message_str
                    logger.info(f"Reply message_str: {reply_text}")
            
            elif isinstance(component, Plain):
                # 处理当前消息的 Plain 类型的消息段
                current_text = component.text
                logger.info(f"Current message Text: {current_text}")
            
            elif isinstance(component, Image):
                # 处理当前消息的 Image 类型的消息段
                logger.info(f"Current message Image: {component.url}")

        # 示例：打印提取的信息
        logger.info(f"Extracted Info - Reply Image URL: {reply_image_url}, Reply Text: {reply_text}, Current Text: {current_text}")
        
        return reply_image_url, reply_text, current_text


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
        message_chain = event.message_obj.message # AstrBot 解析出来的消息链内容
        message_str = event.message_str # 获取消息的纯文本内容
        if message_str == "dl" or message_str == "download":
            reply_image_url, reply_text, current_text = self.parse_message_chain(message_chain)
            if reply_text:
                message_str = reply_text
        pattern = r"https://e.hentai\.org/g/\d+/[a-zA-Z0-9]+/"
        match = re.search(pattern, message_str)
        if match: # 直接处理包含画廊链接的消息
            result = await self.send_to_hentai_assistant(url=match.group(0))
            if result[0] == True:
                yield event.plain_result(f"收到了 {result[1]['message']} 这样的信息，看起来推送成功了呢。") # 调用异步方法发送请求到 hentai 助手
            elif result[0] == False:
                yield event.plain_result(f"返回了 {result[1]} 这样的错误代码，看起来推送失败了呢。")
        else:
            yield event.plain_result(f"看起来这不是真冬能处理的链接呢。")
    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""


