import asyncio
import inspect

from lightrag import LightRAG, QueryParam
from lightrag.llm import ollama_model_complete, ollama_embedding
from lightrag.utils import EmbeddingFunc


from publics import *

import logging
logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)


rag = LightRAG(
    working_dir=WORKING_DIR,
    llm_model_func=ollama_model_complete,
    llm_model_name="qwen:1.8b",
    llm_model_max_async=4,
    llm_model_max_token_size=32768,
    llm_model_kwargs={"host": "http://192.168.10.8:11434", "options": {"num_ctx": 32768}},
    embedding_func=EmbeddingFunc(
        embedding_dim=1024,
        max_token_size=8192,
        func=lambda texts: ollama_embedding(texts, embed_model="bge-m3:latest", host="http://192.168.10.8:11434"),
    ),
)

with open(input_file, "r", encoding="utf-8") as f:
    rag.insert(f.read())

# Perform naive search
print(rag.query("What are the top themes in this story?", param=QueryParam(mode="naive")))

print()
print()
print()
print()
print()

# Perform local search
print(rag.query("What are the top themes in this story?", param=QueryParam(mode="local")))

print()
print()
print()
print()
print()

# Perform global search
print(rag.query("What are the top themes in this story?", param=QueryParam(mode="global")))

print()
print()
print()
print()
print()

# Perform hybrid search
print(rag.query("What are the top themes in this story?", param=QueryParam(mode="hybrid")))

print()
print()
print()
print()
print()

# stream response
resp = rag.query(
    "What are the top themes in this story?",
    param=QueryParam(mode="hybrid", stream=True),
)


async def print_stream(stream):
    async for chunk in stream:
        print(chunk, end="", flush=True)


if inspect.isasyncgen(resp):
    asyncio.run(print_stream(resp))
else:
    print(resp)
