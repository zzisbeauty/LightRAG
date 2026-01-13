import os


os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''
os.environ['NO_PROXY'] = 'localhost,127.0.0.1,::1,host.docker.internal'


import asyncio
import logging
import logging.config
from lightrag import LightRAG, QueryParam
from lightrag.utils import logger, set_verbose_debug
import numpy as np

WORKING_DIR = "./dickens"
if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)

from dotenv import load_dotenv
load_dotenv('/workspace/lightrag/.env', override=True)

def configure_logging():
    """ Configure logging for the application """

    # Reset any existing handlers to ensure clean configuration
    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error", "lightrag"]:
        logger_instance = logging.getLogger(logger_name)
        logger_instance.handlers = []
        logger_instance.filters = []

    # Get log directory path from environment variable or use current directory
    print(os.getcwd())
    log_dir = os.getenv("LOG_DIR", os.getcwd())
    print(log_dir)
    log_file_path = os.path.abspath(os.path.join(log_dir, "lightrag_demo.log"))

    print(f"\nLightRAG demo log file: {log_file_path}\n")
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







# def chunk_texts_for_embedding(texts: list[str], max_tokens: int = 1000) -> list[str]:  
#     """  
#     将文本列表分割成适合 embedding 的块  
#     """  
#     chunked_texts = []  
#     for text in texts:  
#         # 简单按句子分割（可根据需要改进）  
#         sentences = text.split('。')  
#         current_chunk = ""  
#         current_length = 0  
          
#         for sentence in sentences:  
#             # 估算 token 数（粗略估算：中文字符 ≈ tokens）  
#             sentence_tokens = len(sentence)  
              
#             if current_length + sentence_tokens > max_tokens:  
#                 if current_chunk:  
#                     chunked_texts.append(current_chunk.strip())  
#                 current_chunk = sentence  
#                 current_length = sentence_tokens  
#             else:  
#                 current_chunk += sentence + '。'  
#                 current_length += sentence_tokens  
          
#         if current_chunk:  
#             chunked_texts.append(current_chunk.strip())  
      
#     return chunked_texts 





async def initialize_rag():
    # rag = LightRAG(
    #     working_dir=WORKING_DIR,
    #     embedding_func=openai_embed, 
    #     llm_model_func=gpt_4o_mini_complete,
    # )

    from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed, openai_complete_if_cache

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

    # 嵌入函数 - 使用 SiliconFlow  
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

    from lightrag.utils import EmbeddingFunc  

    rag = LightRAG(  
            working_dir=WORKING_DIR,  
            vector_storage="QdrantVectorDBStorage",
            llm_model_func=llm_model_func,  
            embedding_func=EmbeddingFunc(  
                # ERROR: Embedding func: Error in decorated function for task 124362371644480_20779.877838419: Embedding dimension mismatch detected: 
                # total elements (4096) cannot be evenly divided by expected dimension (1536). 
                embedding_dim=1024,
                func=embedding_func  
            ),  
        )  
          
    await rag.initialize_storages()  # Auto-initializes pipeline_status
    return rag


async def main():
    # Check if OPENAI_API_KEY environment variable exists ；  vllm 其实不用这个验证过程
    if not os.getenv("OPENAI_API_KEY"): 
        print("Error: OPENAI_API_KEY environment variable is not set. Please set this variable before running the program.")
        print("You can set the environment variable by running:")
        print("  export OPENAI_API_KEY='your-openai-api-key'")
        return  # Exit the async function

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

        # Initialize RAG instance
        rag = await initialize_rag()

        # Test embedding function
        test_text = ["This is a test string for embedding."]
        embedding = await rag.embedding_func(test_text)
        embedding_dim = embedding.shape[1]
        print("\n=======================")
        print("Test embedding function")
        print("========================")
        print(f"Test dict: {test_text}")
        print(f"Detected embedding dimension: {embedding_dim}\n\n")

        # with open("/workspace/data/book.txt", "r", encoding="utf-8") as f:
        with open('/workspace/data/文学数据/红楼梦-节选2.txt',encoding='utf-8') as f:
            await rag.ainsert(f.read())

        # Perform naive search
        print("\n=====================")
        print("Query mode: naive")
        print("=====================")
        print(
            await rag.aquery(
                "What are the top themes in this story?", param=QueryParam(mode="naive")
            )
        )

        # Perform local search
        print("\n=====================")
        print("Query mode: local")
        print("=====================")
        print(
            await rag.aquery(
                "What are the top themes in this story?", param=QueryParam(mode="local")
            )
        )

        # Perform global search
        print("\n=====================")
        print("Query mode: global")
        print("=====================")
        print(
            await rag.aquery(
                "What are the top themes in this story?",
                param=QueryParam(mode="global"),
            )
        )

        # Perform hybrid search
        print("\n=====================")
        print("Query mode: hybrid")
        print("=====================")
        print(
            await rag.aquery(
                "What are the top themes in this story?",
                param=QueryParam(mode="hybrid"),
            )
        )
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
