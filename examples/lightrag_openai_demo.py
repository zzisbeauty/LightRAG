from lightrag import LightRAG, QueryParam
from lightrag.llm import gpt_4o_mini_complete
from publics import *


rag = LightRAG(working_dir=WORKING_DIR, llm_model_func=gpt_4o_mini_complete,)
with open(input_file, "r", encoding="utf-8") as f:
    rag.insert(f.read())


# Perform naive search
print(rag.query("What are the top themes in this story?", param=QueryParam(mode="naive")))

# Perform local search
print(rag.query("What are the top themes in this story?", param=QueryParam(mode="local")))

# Perform global search
print(rag.query("What are the top themes in this story?", param=QueryParam(mode="global")))

# Perform hybrid search
print(rag.query("What are the top themes in this story?", param=QueryParam(mode="hybrid")))
