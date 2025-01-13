# We use OpenAI compatible API to call LLM on Oracle Cloud ，More docs here https://github.com/jin38324/OCI_GenAI_access_gateway

# APIKEY = "ocigenerativeai"
# BASE_URL = "http://xxx.xxx.xxx.xxx:8088/v1/"
# CHATMODEL = "cohere.command-r-plus"
# EMBEDMODEL = "cohere.embed-multilingual-v3.0"


import os

# WORKING_DIR = "./dickens"
# input_file = '/home/fzm/Desktop/LightRAG/resources/红楼梦.txt'

# WORKING_DIR = "./dickens"
# input_file = '/home/fzm/Desktop/LightRAG/resources/红楼梦.txt'

# WORKING_DIR = "/home/fzm/Desktop/LightRAG/_index_dickens"
# input_file = '/home/fzm/Desktop/LightRAG/_resources/mock_data.txt'



# ✅ qwen api use - ✅lightrag_openai_compatible_demo.py
WORKING_DIR = "/home/fzm/Desktop/LightRAG/_index_hongloumeng_qwenapi"
input_file = '/home/fzm/Desktop/LightRAG/_resources/红楼梦.txt'




# ❎ ollama - ❎lightrag_ollama_demo_until_larger_model.py
# WORKING_DIR = "/home/fzm/Desktop/LightRAG/_index_hongloumeng_ollama"
# input_file = '/home/fzm/Desktop/LightRAG/_resources/红楼梦.txt'



if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)



# neo4j database setting
# Constants
BATCH_SIZE_NODES = 500
BATCH_SIZE_EDGES = 100
# Neo4j connection credentials
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "your_password"
NEO4J_URI = "bolt://localhost:7687"