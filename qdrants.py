from qdrant_client import QdrantClient

client = QdrantClient(url="http://qdrant:6333")

# 获取所有集合
collections = client.get_collections().collections

for col in collections:
    print(f"正在删除集合: {col.name}")
    client.delete_collection(collection_name=col.name)

print("清理完成！")