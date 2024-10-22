from langchain_community.llms import SparkLLM
import os
# 修改使用模型为讯飞3.5
os.environ['IFLYTEK_SPARK_API_URL']='wss://spark-api.xf-yun.com/v1.1/chat'
os.environ["IFLYTEK_SPARK_API_SECRET"] = 'YTY0OTBmZTU4NDFjM2E0ODFiYWY3N2M3'

llm=SparkLLM(model='general')
