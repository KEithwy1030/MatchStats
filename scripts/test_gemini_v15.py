import requests
import json
import sys

# 设置输出编码
if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8')

API_KEY = "AIzaSyDIcOvvB5hM7DxgjuIb7jBEzIxESR6AR9g"

print("=" * 60)
print("🔍 尝试调用最稳定的 Gemini 1.5 Flash 模型")
print("=" * 60)

# 使用 1.5-flash，这是免费层级最常用的模型
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

payload = {
    "contents": [{
        "parts": [{
            "text": "请搜索：2026年1月29日欧冠阿森纳对阵卡拉特的比赛预测。请简洁回答。"
        }]
    }],
    "tools": [{
        "googleSearchRetrieval": {}
    }]
}

try:
    print("📤 发送请求到 gemini-1.5-flash...")
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        text = result['candidates'][0]['content']['parts'][0]['text']
        print("\n✅ 成功！Gemini 1.5 Flash 可用。")
        print("-" * 30)
        print(text)
    else:
        print(f"❌ 依然失败")
        print(f"状态码: {response.status_code}")
        print(f"提示: {response.json().get('error', {}).get('message', '未知错误')}")
        
except Exception as e:
    print(f"❌ 运行错误: {e}")
