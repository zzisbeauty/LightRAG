import os
import asyncio
from lightrag import LightRAG, QueryParam
from lightrag.llm import openai_complete_if_cache, openai_embedding
from lightrag.utils import EmbeddingFunc
import numpy as np

from publics import *

async def llm_model_func(prompt, system_prompt=None, history_messages=[], keyword_extraction=False, **kwargs) -> str:
    return await openai_complete_if_cache(
        "qwen-plus",
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        api_key=os.getenv("UPSTAGE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        **kwargs,
    )

async def embedding_func(texts: list[str]) -> np.ndarray:
    return await openai_embedding(
        texts,
        model="text-embedding-v1",
        api_key=os.getenv("UPSTAGE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

async def get_embedding_dim():
    test_text = ["This is a test sentence."]
    embedding = await embedding_func(test_text)
    embedding_dim = embedding.shape[1]
    return embedding_dim


# function test
async def test_funcs():
    result = await llm_model_func("How are you?")
    print("llm_model_func: ", result)

    result = await embedding_func(["How are you?"])
    print("embedding_func: ", result)


# asyncio.run(test_funcs())


async def main():
    try:
        embedding_dimension = await get_embedding_dim()
        print(f"Detected embedding dimension: {embedding_dimension}")

        rag = LightRAG(
            working_dir=WORKING_DIR,
            llm_model_func=llm_model_func,
            embedding_func=EmbeddingFunc(embedding_dim=embedding_dimension,max_token_size=8192,func=embedding_func,),
        )

        rag.addon_params['entity_types'] = ['人物','时间','地点','事件','组织','角色','概念']

        with open(input_file, "r", encoding="utf-8") as f:
            await rag.ainsert(f.read())

        print("Perform naive search ... ...")
        print(
            await rag.aquery(
                # "What are the top themes in this story?", param=QueryParam(mode="naive")
                "贾宝玉和林黛玉是什么关系？", param=QueryParam(mode="naive")
            )
        )

        print()
        print()
        print()
        print()
        print()

        # Perform local search
        print("Perform local search ... ...")
        print(
            await rag.aquery(
                # "What are the top themes in this story?", param=QueryParam(mode="local")
                "贾宝玉和林黛玉是什么关系?", param=QueryParam(mode="local")
            )
        )

        print()
        print()
        print()
        print()
        print()

        # Perform global search
        print("Perform global search ... ...")
        print(
            await rag.aquery(
                # "What are the top themes in this story?",
                "贾宝玉和林黛玉是什么关系?",
                param=QueryParam(mode="global"),
            )
        )

        print()
        print()
        print()
        print()
        print()
        
        # Perform hybrid search
        print("Perform hybrid search ... ...")
        print(
            await rag.aquery(
                # "What are the top themes in this story?",
                "贾宝玉和林黛玉是什么关系?",
                param=QueryParam(mode="hybrid"),
            )
        )
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())
