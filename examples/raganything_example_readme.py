""" 用的是这个文件学习多模态功能；但是没有跑通
"""

import asyncio
from raganything import RAGAnything
from lightrag import LightRAG
from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.utils import EmbeddingFunc
import os

import numpy as np


from dotenv import load_dotenv

load_dotenv('/workspace/lightrag/.env', override=True)

from functools import partial

lightrag_working_dir = "./existing_lightrag_storage"  


def process_image_data(image_data):  
    """处理多种图片格式的通用函数"""  
    if not image_data:  
        return None  
      
    # 如果是base64编码  
    if isinstance(image_data, str) and image_data.startswith('data:image'):  
        return image_data  
      
    # 如果是base64字符串（无前缀）  
    elif isinstance(image_data, str) and len(image_data) > 100:  
        # 检查是否为纯base64  
        try:  
            import base64  
            base64.b64decode(image_data)  
            return f"data:image/jpeg;base64,{image_data}"  
        except:  
            pass  
      
    # 如果是文件路径  
    elif isinstance(image_data, str) and (image_data.startswith('/') or image_data.startswith('./')):  
        return image_data  
      
    # 如果是二进制数据  
    elif isinstance(image_data, bytes):  
        import base64  
        return f"data:image/jpeg;base64,{base64.b64encode(image_data).decode()}"  
      
    return image_data  






async def load_existing_lightrag():
        # First, create or load an existing LightRAG instance  # 首先，创建或加载现有的 LightRAG 实例

        # Check if previous LightRAG instance exists  # 检查是否存在之前的 LightRAG 实例
        if os.path.exists(lightrag_working_dir) and os.listdir(lightrag_working_dir):
            print("✅ Found existing LightRAG instance, loading...")
        else:
            print("❌ No existing LightRAG instance found, will create new one")

        async def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs  ) -> str:  
                return await openai_complete_if_cache(  
                    "/localmodels/Qwen3-4B-Instruct-2507",  
                    prompt,  
                    system_prompt=system_prompt,  
                    history_messages=history_messages,  
                    api_key="vllm",  
                    base_url=os.getenv('LLM_BINDING_HOST'),  
                    **kwargs  
                )

        # 本地 embedding server
        async def embedding_func(texts: list[str]) -> np.ndarray:  
                # 如果直接使用这个方法进行 embedding server 的创建，这个方法已经被装饰器硬编码了 embedding dim 1536
                # return await openai_embed(
                # 为了避免上述问题，使用如下方案： .func
                return await openai_embed.func(
                    texts,  
                    model="Qwen/Qwen3-Embedding-0.6B",  
                    api_key=os.getenv('EMBEDDING_BINDING_API_KEY'),  
                    base_url=os.getenv("EMBEDDING_BINDING_HOST") 
                )  


        lightrag_instance = LightRAG( 
            # llm_model_func=lambda prompt, system_prompt=None, history_messages=[], **kwargs: openai_complete_if_cache(  
            #     "gpt-4o-mini", prompt, system_prompt=system_prompt,   
            #     history_messages=history_messages, api_key=os.getenv('LLM_BINDING_API_KEY'), **kwargs,  
            # ),  
            llm_model_func=llm_model_func,   
            embedding_func=EmbeddingFunc(  
                embedding_dim=1024,  
                func=embedding_func
                # func=lambda texts: openai_embed(texts, model="text-embedding-3-large", api_key=api_key),  
            )  
        )  


        # Create/Load LightRAG instance with your configurations
        # lightrag_instance = LightRAG(
        #     working_dir=lightrag_working_dir,
        #     llm_model_func=lambda prompt, system_prompt=None, history_messages=[], **kwargs: openai_complete_if_cache(
        #         "gpt-4o-mini",
        #         prompt,
        #         system_prompt=system_prompt,
        #         history_messages=history_messages,
        #         api_key="your-api-key",
        #         **kwargs,
        #     ),
        #     embedding_func=EmbeddingFunc(
        #         embedding_dim=3072,
        #         max_token_size=8192,
        #         model="text-embedding-3-large",
        #         func=partial(
        #             openai_embed.func,  # Use .func to access the unwrapped function
        #             model="text-embedding-3-large",
        #             api_key=api_key,
        #             base_url=base_url,
        #         ),
        #     )
        # )

        # Initialize storage (this will load existing data if available)
        await lightrag_instance.initialize_storages()



        # Now initialize RAGAnything with the existing LightRAG instance
        # rag = RAGAnything(
        #     lightrag=lightrag_instance,  # Pass the existing LightRAG instance
        #     # Only need vision model for multimodal processing
        #     vision_model_func=lambda prompt, system_prompt=None, history_messages=[], image_data=None, **kwargs: openai_complete_if_cache(
        #         "gpt-4o",
        #         "",
        #         system_prompt=None,
        #         history_messages=[],
        #         messages=[
        #             {"role": "system", "content": system_prompt} if system_prompt else None,
        #             {"role": "user", "content": [
        #                 {"type": "text", "text": prompt},
        #                 {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
        #             ]} if image_data else {"role": "user", "content": prompt}
        #         ],
        #         api_key="your-api-key",
        #         **kwargs,
        #     ) if image_data else openai_complete_if_cache(
        #         "gpt-4o-mini",
        #         prompt,
        #         system_prompt=system_prompt,
        #         history_messages=history_messages,
        #         api_key="your-api-key",
        #         **kwargs,
        #     )
        #     # Note: working_dir, llm_model_func, embedding_func, etc. are inherited from lightrag_instance
        # )



        rag = RAGAnything(  
            lightrag=lightrag_instance,  
            vision_model_func=lambda prompt, system_prompt=None, history_messages=[], image_data=None, **kwargs: openai_complete_if_cache(  
                "MiniCPM-V-2_6-int4",  # 本地模型名称  
                "", system_prompt=None, history_messages=[],  
                messages=[  
                    {"role": "system", "content": system_prompt} if system_prompt else None,  
                    {"role": "user", "content": [  
                        {"type": "text", "text": prompt},  
                        # 注意：这里需要根据你的本地服务要求调整图片URL格式  
                        {"type": "image_url", "image_url": {"url": process_image_data(image_data)}}  
                    ]} if image_data else {"role": "user", "content": prompt}  
                ],  
                base_url="http://localhost:8002/v1",  # 本地服务地址  
                api_key="your-local-api-key",  # 可以设置为任意值  
                **kwargs,  
            )  
        )


        # Query the existing knowledge base
        result = await rag.query_with_multimodal(
            "What data has been processed in this LightRAG instance?",
            mode="hybrid"
        )
        print("Query result:", result)

        # Add new multimodal documents to the existing LightRAG instance
        await rag.process_document_complete(
            # file_path="path/to/new/multimodal_document.pdf",  # 需要是 图片 格式的 pdf
            file_path="/workspace/data/图像数据/G9Ry2ewbwAAmYgo.jpeg",
            output_dir="./output"
        )




if __name__ == "__main__":
        asyncio.run(load_existing_lightrag())
