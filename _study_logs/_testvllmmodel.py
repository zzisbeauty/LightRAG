# 测试LightRAG是否能正确调用vLLM  
import requests  
  
headers = {  
    "Content-Type": "application/json",  
    "Authorization": "Bearer your_api_key"  # 如果需要  
}  
  
data = {  
    "model": "/localmodels/Qwen3-4B-Thinking-2507",  
    "messages": [{"role": "user", "content": "halo"}],  
    "max_tokens": 10  
}  
  
# response = requests.post(  
#     "http://192.168.1.6:1128/v1/chat/completions",  
#     headers=headers,  
#     json=data  
# )  
# print(response.status_code, response.text)



import os
import asyncio  
import numpy as np  
from dotenv import load_dotenv

load_dotenv(dotenv_path="/app/LightRAG/.env", override=False)
siliconflowkey = os.getenv('EMBEDDING_BINDING_API_KEY')

# siliconflow embedding model 的嵌入并发性测试

def get_embedding(text: str, token: str):
    url = "https://api.siliconflow.cn/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {siliconflowkey}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "BAAI/bge-large-zh-v1.5",
        "input": text
    }

    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()  # 如果失败会抛异常
    return response.json()


# 示例调用
# token = "<token>"
# text = "Silicon flow embedding online: fast, affordable, and high-quality embedding services. come try it out!"
# result = get_embedding(text, token)
# print(result)


# async def test_batch_embedding():  
#     """测试你的嵌入函数是否支持批处理"""  
#     texts = ["text1", "text2", "text3"]  
      
#     # 调用你的实际嵌入函数  
#     result = await get_embedding(texts)  
      
#     print(f"输入文本数: {len(texts)}")  
#     print(f"返回向量形状: {result.shape}")  
#     print(f"期望向量数: {len(texts)}, 实际向量数: {result.shape[0]}")  
      
#     # 检查是否每个文本都有对应的向量  
#     if result.shape[0] != len(texts):  
#         print("❌ 批处理失败：向量数量不匹配")  
#     else:  
#         print("✅ 批处理正常")  
  
# asyncio.run(test_batch_embedding())