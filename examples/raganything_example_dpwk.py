"""
不用此文件进行多模态的学习处理
"""

import asyncio  
from raganything import RAGAnything  
from lightrag import LightRAG  
from lightrag.llm.openai import openai_complete_if_cache, openai_embed  
from lightrag.utils import EmbeddingFunc  

import numpy as np

import os
from dotenv import load_dotenv

load_dotenv('/workspace/lightrag/.env', override=True)

working_dir="./raganything-example-dpwk",  

async def load_existing_lightrag():  
    # 创建或加载LightRAG实例  

    # 本地 vllm model server
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

    await lightrag_instance.initialize_storages()  
      
    # 初始化RAGAnything进行多模态处理
    rag = RAGAnything(  
        lightrag=lightrag_instance,  
        vision_model_func=lambda prompt, system_prompt=None, history_messages=[], image_data=None, **kwargs: openai_complete_if_cache(  
            "gpt-4o",   # 多模态模型 vlm
            "", system_prompt=None, history_messages=[],  
            messages=[  
                {"role": "system", "content": system_prompt} if system_prompt else None,  
                {"role": "user", "content": [  
                    {"type": "text", "text": prompt},  
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}  
                ]} if image_data else {"role": "user", "content": prompt}  
            ],  
            api_key="your-api-key", **kwargs,  
        )  
    )  


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
                    {"type": "image_url", "image_url": {"url": f"/localmodels/picturesdemo/test.jpeg"}}  
                ]} if image_data else {"role": "user", "content": prompt}  
            ],  
            base_url="http://localhost:8002/v1",  # 本地服务地址  
            api_key="your-local-api-key",  # 可以设置为任意值  
            **kwargs,  
        )  
    )
      
    # 处理多模态文档  
    await rag.process_document_complete(  
        file_path="path/to/multimodal_document.pdf",  
        output_dir="./output"  
    )
