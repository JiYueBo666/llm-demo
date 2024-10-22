from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage
from llm_config import LLM_config
from utils import time_logger, get_green_logger

logger = get_green_logger()


class LLM:
    def __init__(self, callback=None) -> None:
        self.spark_model = ChatSparkLLM(
            spark_api_url=LLM_config.URL,
            spark_app_id=LLM_config.APP_ID,
            spark_api_key=LLM_config.API_KEY,
            spark_api_secret=LLM_config.API_SECRET,
            spark_llm_domain=LLM_config.DOMAIN,
            streaming=False,
        )
        self.handler = ChunkPrintHandler()
        self.history = []
        self.max_size = 3  # 历史对话长度
        self.callback = callback

    @time_logger
    def chat(self, query: str):
        logger.info(f"user:{query}")
        messages = [ChatMessage(role="user", content=query)]
        response = self.spark_model.generate([messages], callbacks=[self.handler])
        self.callback(response.generations[0][0].text)
