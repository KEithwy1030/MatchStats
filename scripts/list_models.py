import requests
import json

API_KEY = "AIzaSyDIcOvvB5hM7DxgjuIb7jBEzIxESR6AR9g"

print("查询可用的 Gemini 模型...")

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"

try:
    response = requests.get(url)
    
    if response.status_code == 200:
        result = response.json()
        print("\n可用模型列表:")
        print("=" * 60)
        for model in result.get('models', []):
            name = model.get('name', '')
            display_name = model.get('displayName', '')
            supported_methods = model.get('supportedGenerationMethods', [])
            print(f"\n模型: {name}")
            print(f"显示名: {display_name}")
            print(f"支持的方法: {', '.join(supported_methods)}")
    else:
        print(f"查询失败: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"错误: {e}")
