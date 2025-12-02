import requests  
import os  
  
def upload_txt_file(server_url, file_path, api_key=None):  
    """ 上传 txt 文件到 LightRAG 服务器  
    Args:  
        server_url: 服务器地址，如 "http://localhost:9621"  
        file_path: 要上传的 txt 文件路径  
        api_key: 可选的 API 密钥（如果服务器启用了认证）  
    Returns:  
        dict: 服务器响应，包含 status, message, track_id  
    """  
    upload_url = f"{server_url}/documents/upload"  
    # 准备文件  
    if not os.path.exists(file_path):  
        raise FileNotFoundError(f"文件不存在: {file_path}")  
    with open(file_path, 'rb') as f:  
        files = {'file': f}  
        # 准备请求头  
        headers = {}  
        if api_key:  
            headers['X-API-Key'] = api_key  
        try:  
            response = requests.post(  
                upload_url,  
                files=files,  
                headers=headers,  
                timeout=30  
            ) 
            if response.status_code == 200:
                return response.json()
            else:
                response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"上传失败: {e}")
            raise
  
# 使用示例  
if __name__ == "__main__":  
    # 服务器配置  
    SERVER_URL = "http://localhost:9621"  
    API_KEY = None  # 如果需要认证，设置您的 API 密钥  
    # 上传文件  
    file_to_upload = "/app/LightRAG/_study_logs/datasets/13513.txt"  
    try:
        result = upload_txt_file(SERVER_URL, file_to_upload, API_KEY)  
        print("上传成功!")  
        print(f"状态: {result['status']}")  
        print(f"消息: {result['message']}")  
        print(f"跟踪ID: {result['track_id']}")  
        # 使用 track_id 监控处理状态  
        track_id = result['track_id']  
        print(f"\n您可以使用 track_id '{track_id}' 监控文档处理状态")  
    except Exception as e:  
        print(f"上传失败: {e}")