import os
import asyncio
import inspect
import logging
import logging.config
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import openai_complete_if_cache
from lightrag.utils import EmbeddingFunc, logger, set_verbose_debug

from dotenv import load_dotenv

load_dotenv(dotenv_path="/app/LightRAG/.env", override=False)

WORKING_DIR = "./dickens"


def configure_logging():
    """Configure logging for the application"""

    # Reset any existing handlers to ensure clean configuration
    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error", "lightrag"]:
        logger_instance = logging.getLogger(logger_name)
        logger_instance.handlers = []
        logger_instance.filters = []

    # Get log directory path from environment variable or use current directory
    log_dir = os.getenv("LOG_DIR", os.getcwd())
    log_file_path = os.path.abspath(os.path.join(log_dir, "lightrag_compatible_demo.log"))

    print(f"\nLightRAG compatible demo log file: {log_file_path}\n")
    os.makedirs(os.path.dirname(log_dir), exist_ok=True)

    # Get log file max size and backup count from environment variables
    log_max_bytes = int(os.getenv("LOG_MAX_BYTES", 10485760))  # Default 10MB
    log_backup_count = int(os.getenv("LOG_BACKUP_COUNT", 5))  # Default 5 backups

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {"format": "%(levelname)s: %(message)s",},
                "detailed": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",},
            },
            "handlers": {
                "console": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                },
                "file": {
                    "formatter": "detailed",
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": log_file_path,
                    "maxBytes": log_max_bytes,
                    "backupCount": log_backup_count,
                    "encoding": "utf-8",
                },
            },
            "loggers": {
                "lightrag": {
                    "handlers": ["console", "file"],
                    "level": "INFO",
                    "propagate": False,
                },
            },
        }
    )

    # Set the logger level to INFO
    logger.setLevel(logging.INFO)
    # Enable verbose debug if needed
    set_verbose_debug(os.getenv("VERBOSE_DEBUG", "false").lower() == "true")


if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)


async def llm_model_func(prompt, system_prompt=None, history_messages=[], keyword_extraction=False, **kwargs) -> str:
    llm = os.getenv("LLM_MODEL", "deepseek-chat")
    api_key = os.getenv("LLM_BINDING_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("LLM_BINDING_HOST", "nothing ...")
    return await openai_complete_if_cache(llm,prompt,system_prompt=system_prompt,history_messages=history_messages,api_key=api_key,base_url=base_url,**kwargs,)


async def print_stream(stream):
    async for chunk in stream:
        if chunk:
            print(chunk, end="", flush=True)


# 基于 ollama  embedding  server
# from lightrag.llm.ollama import ollama_embed
# async def initialize_rag():
#     rag = LightRAG(
#         working_dir=WORKING_DIR,
#         llm_model_func=llm_model_func,
#         embedding_func=EmbeddingFunc(
#             embedding_dim=int(os.getenv("EMBEDDING_DIM", "1024")),
#             max_token_size=int(os.getenv("MAX_EMBED_TOKENS", "8192")),
#             func=lambda texts: ollama_embed(
#                 texts,
#                 embed_model=os.getenv("EMBEDDING_MODEL", "bge-m3:latest"),
#                 host=os.getenv("EMBEDDING_BINDING_HOST", "http://localhost:11434"),
#             ),
#         ),
#     )
#     await rag.initialize_storages()  # Auto-initializes pipeline_status
#     return rag


# # 基于 openai 兼容 embedding
# from lightrag.llm.openai import openai_embed
# async def initialize_rag():
#     embedding_dim = int(os.getenv("EMBEDDING_DIM", "1536"))
#     model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),  # 参数名改变  
#     api_key=os.getenv("EMBEDDING_BINDING_API_KEY"),  # 新增参数 
#     base_url=os.getenv("EMBEDDING_BINDING_HOST", "https://api.openai.com/v1"),  # 参数名改变
#     rag = LightRAG(
#         working_dir=WORKING_DIR,  
#         llm_model_func=llm_model_func,  
#         embedding_func=EmbeddingFunc(
#             embedding_dim=embedding_dim,  # OpenAI 默认维度  
#             max_token_size=int(os.getenv("MAX_EMBED_TOKENS", "8192")),
#             func=lambda texts: openai_embed(
#                 texts,
#                 model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),  # 参数名改变  
#                 api_key=os.getenv("EMBEDDING_BINDING_API_KEY"),  # 新增参数 
#                 base_url=os.getenv("EMBEDDING_BINDING_HOST", "https://api.openai.com/v1"),  # 参数名改变 
#             )
#         )
#     )
#     await rag.initialize_storages()
#     return rag

# import sys
# from pathlib import Path  
# sys.path.insert(0, str(Path(__file__).parent.parent)) 

import aiohttp
import numpy as np
from lightrag.utils import wrap_embedding_func_with_attrs


@wrap_embedding_func_with_attrs(embedding_dim=1024, max_token_size=8192)
async def siliconflow_embed(  
    texts: list[str],  
    model: str = "BAAI/bge-large-zh-v1.5",  
    base_url: str = "https://api.siliconflow.cn/v1/embeddings",  
    api_key: str = None,  
) -> np.ndarray:  
    headers = {  
        "Authorization": f"Bearer {api_key}",  
        "Content-Type": "application/json",  
    }  
    data = {  
        "model": model,  
        "input": texts,  
        "encoding_format": "float",  # 使用 float 格式  
        "dimensions": 1024,  
    }

    async with aiohttp.ClientSession() as session:  
        async with session.post(base_url, headers=headers, json=data) as response:  
            content = await response.json()  
            # 直接处理 float 数组，不需要 base64 解码  
            return np.array([item["embedding"] for item in content["data"]], dtype=np.float32)


async def initialize_rag():
    # embedding_dim = int(os.getenv("EMBEDDING_DIM", "1536"))
    # model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),  # 参数名改变  
    # api_key=os.getenv("EMBEDDING_BINDING_API_KEY"),  # 新增参数 
    # base_url=os.getenv("EMBEDDING_BINDING_HOST", "https://api.openai.com/v1"),  # 参数名改变
    rag = LightRAG(
        working_dir=WORKING_DIR,  
        llm_model_func=llm_model_func,   # llm_model_func 被定义并注入到 LightRAG 实例中
        embedding_func=EmbeddingFunc(
            embedding_dim=int(os.getenv("EMBEDDING_DIM", "1536")),  # OpenAI 默认维度  
            max_token_size=int(os.getenv("MAX_EMBED_TOKENS", "8192")),
            func=lambda texts: siliconflow_embed(
                texts,
                model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),  # 参数名改变  
                api_key=os.getenv("EMBEDDING_BINDING_API_KEY"),  # 新增参数 
                base_url=os.getenv("EMBEDDING_BINDING_HOST", "https://api.openai.com/v1"),  # 参数名改变 
            )
        )
    )
    print(11111)
    await rag.initialize_storages()
    print(22222)
    return rag


async def main():
    try:
        # Clear old data files
        files_to_delete = [
            "graph_chunk_entity_relation.graphml",
            "kv_store_doc_status.json",
            "kv_store_full_docs.json",
            "kv_store_text_chunks.json",
            "vdb_chunks.json",
            "vdb_entities.json",
            "vdb_relationships.json",
        ]

        for file in files_to_delete:
            file_path = os.path.join(WORKING_DIR, file)
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleting old file:: {file_path}")

        # Initialize RAG instance；  准备 LLM and  EMBEDDINg SERVER
        print("before await initialize_rag()")
        rag = await initialize_rag()
        print("after await initialize_rag()")

        # # Test embedding function  确认 embedding server is ok
        # test_text = ["This is a test string for embedding."]
        # embedding = await rag.embedding_func(test_text)
        # embedding_dim = embedding.shape[1]
        # print("\n=======================")
        # print("Test embedding function")
        # print("========================")
        # print(f"Test dict: {test_text}")
        # print(f"Detected embedding dimension: {embedding_dim}\n\n")

        with open("/app/LightRAG/_study_logs/datasets/101086.txt", "r", encoding="utf-8") as f:
            await rag.ainsert(f.read())

        # Perform naive search
        print("\n=====================")
        print("Query mode: naive")
        print("=====================")
        resp = await rag.aquery("What are the top themes in this story?", param=QueryParam(mode="naive", stream=True),)
        if inspect.isasyncgen(resp):
            await print_stream(resp)
        else:
            print(resp)

        # Perform local search
        print("\n=====================")
        print("Query mode: local")
        print("=====================")
        resp = await rag.aquery("What are the top themes in this story?", param=QueryParam(mode="local", stream=True),)
        if inspect.isasyncgen(resp):
            await print_stream(resp)
        else:
            print(resp)

        # Perform global search
        print("\n=====================")
        print("Query mode: global")
        print("=====================")
        resp = await rag.aquery("What are the top themes in this story?", param=QueryParam(mode="global", stream=True),)
        if inspect.isasyncgen(resp):
            await print_stream(resp)
        else:
            print(resp)

        # Perform hybrid search
        print("\n=====================")
        print("Query mode: hybrid")
        print("=====================")
        resp = await rag.aquery("What are the top themes in this story?", param=QueryParam(mode="hybrid", stream=True),)
        if inspect.isasyncgen(resp):
            await print_stream(resp)
        else:
            print(resp)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if rag:
            await rag.finalize_storages()


if __name__ == "__main__":
    # Configure logging before running the main function
    configure_logging()
    asyncio.run(main())
    print("\nDone!")
