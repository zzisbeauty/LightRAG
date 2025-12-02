import asyncio  
import json  
import time  
import requests  
from typing import List, Dict  

""" 重启失败文档的处理过程。会观察到文档的处理过程
"""

# LightRAG 服务器配置  
LIGHTRAG_URL = "http://localhost:9621"  
  
class DocumentProcessor:  
    """文档处理客户端，用于手动处理失败文档"""  
      
    def __init__(self, base_url: str):  
        self.base_url = base_url  
      
    def get_failed_documents(self) -> List[Dict]:  
        """获取所有失败和待处理的文档"""  
        url = f"{self.base_url}/documents/paginated"  
        payload = {  
            "status_filter": "failed",  # 也可以用 "pending" 获取待处理文档  
            "page": 1,  
            "page_size": 100,  
            "sort_field": "updated_at",  
            "sort_direction": "desc"  
        }  
          
        response = requests.post(url, json=payload)  
        response.raise_for_status()  
        data = response.json()  
          
        return data["documents"]  

    
    # 开启失败稳定处理的入口； 这个入口代码会调用 文档处理 的 pipeline； 因为失败的稳定也是 文档；
    def reprocess_failed_documents(self) -> str:  
        """ 手动触发重新处理所有失败文档。此 API 对应的方法为： reprocess_failed_documents,路径为： lightrag/api/routers/document_routes.py """  
        url = f"{self.base_url}/documents/reprocess_failed"  
        response = requests.post(url)  
        response.raise_for_status()  
        return response.json()["track_id"]  
      
    def track_processing_status(self, track_id: str) -> Dict:  
        """ 跟踪处理状态 """  
        url = f"{self.base_url}/track_status/{track_id}"  
        response = requests.get(url)
        response.raise_for_status()
        return response.json()  
      
    def monitor_processing(self, track_id: str, interval: int = 2):  
        """ 监控处理进度，直到完成 """  
        print(f"开始监控处理进度 ( track_id: {track_id})...")  
        while True:  
            status = self.track_processing_status(track_id)  
            print(f"状态: {status}")  
            if status.get("status") in ["processed", "failed"]:  
                break  
            time.sleep(interval)  
        return status

    def get_document_details(self, doc_id: str) -> Dict:  
        """获取文档详细信息"""  
        url = f"{self.base_url}/documents/paginated"  
        payload = {"status_filter": "all",  "page": 1,  "page_size": 1000}  
          
        response = requests.post(url, json=payload)  
        response.raise_for_status()  
        data = response.json()  
          
        # 查找指定 ID 的文档  
        for doc in data["documents"]:  
            if doc["id"] == doc_id:  
                return doc  
          
        return None  
      
    def delete_document(self, doc_id: str) -> bool:  
        """删除指定文档（清理后重新处理）"""  
        url = f"{self.base_url}/documents/{doc_id}"  
        response = requests.delete(url)  
        return response.status_code == 200  
  
async def main():  
    """主函数：演示手动处理失败文档的完整流程"""  
    processor = DocumentProcessor(LIGHTRAG_URL)  
      
    # 1. 查看当前失败的文档  
    print("=== 1. 查看失败文档 ===")  
    failed_docs = processor.get_failed_documents()  
      
    if not failed_docs:  
        print("没有找到失败的文档")  
        return

    print(f"找到 {len(failed_docs)} 个失败文档:")  
    for doc in failed_docs:  
        print(f"  - ID: {doc['id']}")  
        print(f"    文件: {doc['file_path']}")  
        print(f"    状态: {doc['status']}")  
        print(f"    错误: {doc.get('error_msg', 'N/A')}")  
        print(f"    更新时间: {doc['updated_at']}")  
        print() 
    
    # 2. 手动触发重新处理  
    print("=== 2. 手动触发重新处理 ===")  
    track_id = processor.reprocess_failed_documents()  
    print(f"重新处理已启动，track_id: {track_id}")  
      
    # 3. 监控处理进度  
    print("\n=== 3. 监控处理进度 ===")  
    final_status = processor.monitor_processing(track_id)  
      
    if final_status["status"] == "processed":  
        print("\n✅ 所有文档处理成功!")  
    else:  
        print("\n❌ 处理过程中出现错误")  
        print(f"错误信息: {final_status.get('error_msg', 'N/A')}")  
      
    # 4. 查看处理结果  
    print("\n=== 4. 查看处理结果 ===")  
    for doc in failed_docs:  
        updated_doc = processor.get_document_details(doc["id"])  
        if updated_doc:  
            print(f"文档 {doc['file_path']}:")  
            print(f"  新状态: {updated_doc['status']}")  
            if updated_doc['status'] == 'failed':  
                print(f"  错误: {updated_doc.get('error_msg', 'N/A')}")  
  
def debug_single_document(doc_id: str):  
    """调试单个文档的处理过程"""  
    processor = DocumentProcessor(LIGHTRAG_URL)  
      
    # 获取文档详情  
    doc = processor.get_document_details(doc_id)  
    if not doc:  
        print(f"文档 {doc_id} 不存在")  
        return  
      
    print(f"文档信息:")  
    print(f"  ID: {doc['id']}")  
    print(f"  文件: {doc['file_path']}")  
    print(f"  状态: {doc['status']}")  
    print(f"  错误: {doc.get('error_msg', 'N/A')}")  
      
    # 如果文档失败了，可以选择删除后重新上传  
    if doc['status'] == 'failed':  
        choice = input("\n是否删除此文档以便重新上传? (y/n): ")  
        if choice.lower() == 'y':  
            if processor.delete_document(doc_id):  
                print(f"文档 {doc_id} 已删除，请重新上传")  
            else:  
                print(f"删除文档 {doc_id} 失败")  
  
if __name__ == "__main__":  
    # 运行主程序  
    asyncio.run(main())  
      
    # 或者调试特定文档  
    # debug_single_document("your-doc-id-here")